from textwrap import dedent
from itertools import chain
from collections import OrderedDict
from hashlib import blake2b

from m42pl.commands import StreamingCommand, MergingCommand, DequeBufferingCommand
from m42pl.fields import Field, FieldsMap
from m42pl.event import Event

# Stats functors
# Each stats functions (aka. functors) is defined in its own module.
# The module 'functions' (imported here as 'stats_functions') holds a
# a dict named 'names' which map a stats function name with its class.
from . import functions as stats_functions


class StreamStats(StreamingCommand):
    """Aggregates events over functions results by fields values.

    `StreamStats` performs a *streaming aggregation* on the incoming
    events. Since its working on a data stream, events yields by 
    `StreamStats` are partial statistical results (event #1 may be
    replaced by event #1 + N).

    In order to track the latest result, events sharing the same
    aggregation fields values also share the same signature: if you
    receive an event with the same signature as a previous one, you
    should update your calculation to take this new event values into
    account.

    To reduce the pressure on commands which follows a `StreamStats`,
    the `PostStatsBuffer` command is automatically injected in the
    pipeline after `StreamStats` to keep only the latest iteration of
    each unique event.
    """

    _aliases_ = ['_stream_stats',]

    def __init__(self, functions: list, fields: list, **kwargs):
        """
        :param functions:   Aggregation functions list.
                            Ex: `[('function_name', 'source_field', 'dest_field')]`
        :param fields:      Aggregation fields list.
        """
        super().__init__(functions, fields)
        # ---
        # Aggregation fields
        self.aggr_fields = [
            Field(f, default=None, seqn=False)
            for f
            in fields
        ]
        # ---
        # Aggreation results
        self.aggregates = {} # type: dict
        # ---
        # Stated fields map (aka. functions calling map)
        self.stated_fields = {}
        for function in functions:
            # Extract and format function name, source field and destination field names
            function_name, source_field, dest_field, *_ = chain(function, [None] * 3)
            source_field = Field(source_field)
            dest_field = dest_field and Field(dest_field) or Field(f'{function_name}({source_field.name or ""})')
            # Add destination field and function call
            if function_name in stats_functions.names:
                self.stated_fields[dest_field] = stats_functions.names[function_name](source_field, self.aggr_fields, dest_field, self.aggregates)
            else:
                raise Exception(f'Unknown stats function: {function_name}')

    async def setup(self, event, pipeline):
        await super().setup(event, pipeline)

    async def target(self, event, pipeline):
        # ---
        # Create new event which will holds the aggregated values
        stated_event = Event()
        # ---
        # Prepare event signature
        signature = blake2b()
        # ---
        # Read aggregation fields values and update signature
        for field in self.aggr_fields:
            # Read aggregation field value
            value = await field.read(event, pipeline)
            # Update signature
            signature.update(str(value).encode())
            # Write aggregation field value to new event
            await field.write(stated_event, value)
        # ---
        # Update source event and new event signatures
        event['sign'] = signature.hexdigest()
        stated_event['sign'] = signature.hexdigest()
        # ---
        # Compute and add the stated fields to the new event
        for field, function in self.stated_fields.items():
            await field.write(stated_event, await function(event, pipeline))
        # ---
        # Done
        yield stated_event

class PreStatsMerge(StreamingCommand, MergingCommand):
    """Merges before running `stats`.
    """

    _aliases_ = ['_pre_stats_merge',]

    async def target(self, event, pipeline):
        yield event


class PostStatsMerge(StreamingCommand, MergingCommand):
    """Merges `stats` results.
    """

    _aliases_ = ['_post_stats_merge',]

    async def target(self, event, pipeline):
        yield event


class PostStatsBuffer(DequeBufferingCommand):
    """Buffer events yield by `stats`.
    """

    _aliases_ = ['_post_stats_buffer',]

    def __init__(self, buffer: int = 10000, *args, **kwargs):
        """
        :param buffer:  Internal buffer size (i.e. the amount of
                        different event to keep in buffer before
                        yielding them).
        """
        super().__init__(buffer)
        self.buffer_size = Field(buffer, type=int, default=10000)

    async def setup(self, event, pipeline):
        await super().setup(
            event,
            pipeline,
            maxsize=await self.buffer_size.read(event, pipeline)
        )

    # async def target(self, pipeline):
    #     async for event in super().target(pipeline):
    #         yield event


class Stats(StreamingCommand):
    """Stats command entry point.
    """

    _about_   = 'Performs statistical operations on an events stream'
    _syntax_  = '<function> [as <field>], ... by <field>, ... [with ...]'
    _aliases_ = ['stats', 'aggr', 'aggregate']

    _grammar_ = OrderedDict(StreamingCommand._grammar_)
    #_grammar_.pop('collections_rules')
    #_grammar_.pop('arguments_rules')
    _grammar_['stats_rules'] = dedent('''\
        stats_function_name     : NAME
        stats_function_body     : ( "(" field? ")" )?
        stats_function_alias    : ("as" field)?
        stats_function          : stats_function_name stats_function_body stats_function_alias
        stats_functions         : (stats_function ","?)+
        stats_fields            : (field ","?)+
    ''')
    _grammar_['start'] = dedent('''\
        start   : stats_functions ("by" stats_fields)? ("with" kwargs)?
    ''')

    class Transformer(StreamingCommand.Transformer):
        stats_function_name     = lambda self, items: str(items[0])
        stats_function_body     = lambda self, items: len(items) and str(items[0]) or None
        stats_function_alias    = lambda self, items: len(items) and str(items[0]) or None
        stats_function          = tuple
        stats_functions         = list
        field                   = str
        stats_fields            = list
        # start           = lambda self, items: (tuple(), {
        #                         'functions': items[0],
        #                         'fields': len(items) > 1 and items[1] or []
        #                     })
        
        def start(self, items):
            # print(f'stats --> {items}')
            kwargs = {}
            if len(items) > 2:
                for kwarg in items[2]:
                    kwargs.update(kwarg)
            return (), {
                **{
                    'functions': items[0],
                    'fields': len(items) > 1 and items[1] or []
                },
                **kwargs
            }

    def __new__(cls, *args, **kwargs):
        """Builds and returns the stats commands chain.
        
        The `stats` command is split into three subcommands:

        * `StreamStats` performs the actual statistical operations.
          Ultimately, I should switch to NumPy or Pandas instead of
          using a self-made implementation of the statistical functions.
        * `PostStatsMerge` receives the events yields by each parallel
          `StreamStats` commands and aggregates them.
        * `PostStatsBuffer` buffers and keep the latest iteration of
          each unique event to reduce the pressure over the next
          commands.
        """
        return (
            PreStatsMerge(),
            StreamStats(*args, **kwargs),
            # PostStatsMerge(),
            # PostStatsBuffer(**kwargs)
        )
