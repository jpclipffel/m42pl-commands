from re import L
from textwrap import dedent
from itertools import chain
from collections import OrderedDict

from hashlib import blake2b
# import xxhash

from tabulate import tabulate
import curses

from typing import Any

from m42pl.commands import StreamingCommand, MergingCommand, BufferingCommand, DequeBufferingCommand
from m42pl.fields import Field, FieldsMap
from m42pl.event import Event, signature

# Stats functors
# Each stats functions (aka. functors) is defined in its own module.
# The module 'functions' (imported here as 'stats_functions') holds a
# a dict named 'names' which map a stats function name with its class.
from . import functions as stats_functions


class PreStatsMerge(StreamingCommand, MergingCommand):
    """Force-merges the pipeline before running ``StreamStats``.
    """

    _about_     = 'Force-merges the pipeline before running StreamStats'
    _syntax_    = ''
    _aliases_   = ['_pre_stats_merge',]
    _schema_    = {'properties': {}} # type: ignore


class StreamStats(StreamingCommand):
    """Aggregates events over functions results by fields values.

    ``StreamStats`` performs a *streaming aggregation* on the incoming
    events. Since it is working on a data stream, events yields by 
    ``StreamStats`` are partial statistical results (event ``n`` may
    be replaced by a future event ``n+x``).

    In order to track the latest result, all events sharing the same
    aggregation fields values also share the same signature: if we
    receive an event with the same signature as a previous one, we
    should update our calculation to take this new event value into
    account.
    """

    _about_     = 'Performs statistical operations on an events stream'
    _syntax_    = '<function> [as <field>], ... by <field>, ... [with ...]'
    _aliases_   = ['_stream_stats',]
    _schema_    = {
        'additionalProperties': {
            'description': 'Aggregates and aggregation fields'
        }
    }

    def __init__(self, functions: list, fields: list, **kwargs):
        """
        :param functions: Aggregation functions list
            e.g. `[('function_name', 'source_field', 'dest_field')]`
        :param fields: Aggregation fields list
        :kwargs merge: ``True`` when merging stats results
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
            # Post stats use dest_field as source
            if kwargs.get('merge', False):
                source_field = dest_field
            # Add destination field and function call
            if function_name in stats_functions.names:
                self.stated_fields[dest_field] = stats_functions.names[function_name](source_field, self.aggr_fields, dest_field, self.aggregates)
            else:
                raise Exception(f'Unknown stats function: {function_name}')

    # async def setup(self, event, pipeline, context):
    #     await super().setup(event, pipeline, context)

    async def target(self, event, pipeline, context, *args, **kwargs):
        # ---
        # Create new event which will holds the aggregated values
        stated_event = Event(meta={
            'stats': {}
        })
        # ---
        # Prepare event signature
        signature = blake2b()
        # signature = xxhash.xxh64()
        # ---
        # Read aggregation fields values and update signature
        for field in self.aggr_fields:
            # Read aggregation field value
            value = await field.read(event, pipeline, context)
            # Update signature
            signature.update(str(value).encode())
            # Write aggregation field value to new event
            await field.write(stated_event, value)
        # ---
        # Update source event and new event signatures
        # event['sign'] = signature.hexdigest()
        # stated_event['sign'] = signature.hexdigest()
        event['sign'] = stated_event['sign'] = signature.hexdigest()
        # ---
        # Compute and add the stated fields to the new event
        for field, function in self.stated_fields.items():
            await field.write(stated_event, await function(event, pipeline, context))
        # ---
        # Done
        yield stated_event


class PostStatsBuffer(DequeBufferingCommand):
    """Buffers events yields by ``StreamStats``.
    """

    _about_     = 'Buffers StreamStats events'
    _syntax_    = '[[size=]<buffer size>] [[showchunk=]<yes|no>]'
    _aliases_   = ['_post_stats_buffer', ]
    _schema_    = {'properties': {}}

    def __init__(self, *args, **kwargs):
        super().__init__()

    async def setup(self, event, pipeline, context):
        await super().setup(
            event,
            pipeline,
            context,
            10
        )

    async def target(self, pipeline):
        async for event in super().target(pipeline):
            yield event


class PostStatsMerge(StreamStats, MergingCommand):
    """Force-merges the pipeline after running ``StreamStats``.
    """

    _about_     = 'Force-merges the pipeline after running StreamStats'
    _syntax_    = ''
    _aliases_   = ['_post_stats_merge',]
    _schema_    = {'properties': {}} # type: ignore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, merge=True, **kwargs)


class Stats(StreamingCommand):
    """Returns a viable ``stats`` commands set.

    This command returns other commands instances uppon calling, each
    one being a part of the ``stats`` pipeline.
    """

    # _about_     = 'Performs statistical operations on an events stream'
    # _syntax_    = '<function> [as <field>], ... by <field>, ... [with ...]'
    # _aliases_   = ['stats', 'aggr', 'aggregate']
    # _schema_    = {
    #     'additionalProperties': {
    #         'description': 'Aggregates and aggregation fields'
    #     }
    # }

    _about_     = StreamStats._about_
    _syntax_    = StreamStats._syntax_
    _aliases_   = ['stats', 'aggr', 'aggregate']
    _schema_    = StreamStats._schema_

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
        
        The `stats` command is split into several subcommands:

        * `PreStatsMerge` forces pipeline merge before performing
          the statistical operations.
        * `StreamStats` performs the actual statistical operations.
          Ultimately, we should switch to NumPy or Pandas instead of
          using a self-made implementation of the statistical functions.
        * `PostStatsMerge` receives the events yields by each parallel
          `StreamStats` commands and aggregates them.
        * `PostStatsBuffer` buffers and keep the latest iteration of
          each unique event to reduce the pressure over the next
          commands.
        """
        return (
            # PreStatsMerge(),
            StreamStats(*args, **kwargs),
            # PostStatsBuffer(*args, **kwargs),
            PostStatsMerge(*args, **kwargs),
            # PostStatsBuffer(**kwargs)
        )


class StatsTable(BufferingCommand):
    """Prints stats table on the standard output.
    """

    _about_     = 'Prints statistical table'
    _syntax_    = '[[buffer=]<buffer size>]'
    _aliases_   = [
        'print_stats',
        'output_stats',
        'stats_output',
        'stats_print'
    ]
    _schema_    = {'properties': {}} # type: ignore

    def __init__(self, buffer: int = 126):
        """
        :param buffer: Internal buffer size
        """
        super().__init__(buffer)
        self.buffer = Field(buffer, default=126)
        self.events: dict[str, Any] = {}

    async def setup(self, event, pipeline, context):
        await super().setup(
            event,
            pipeline, 
            await self.buffer.read(event, pipeline, context)
        )
        # Init curses
        self.logger.info('initialize curses')
        self.stdscr = curses.initscr()
        curses.noecho()
        self.stdscr.clear()
        # Init view
        self.stdscr.addstr(0, 0, 'Pipeline running')

    async def target(self, pipeline, *args, **kwargs):
        # Get new events from queue and update table
        async for event in super().target(pipeline):
            self.events[signature(event)] = event
            yield event
        # Update table
        table = []
        for _, event in self.events.items():
            table.append(event.get('data', {}))
        # Print table
        self.stdscr.addstr(2, 0, tabulate(table, headers='keys'))
        self.stdscr.refresh()
        # Yield events for further processing
        for _, event in self.events.items():
            yield event

    async def __aexit__(self, *args, **kwargs) -> None:
        try:
            # Wait for user to quit
            self.stdscr.addstr(
                0, 0, 'Pipeline complete, press any key to leave'
            )
            self.stdscr.getch()
            # Reset curses and terminal
            self.logger.info('reset curses')
            curses.nocbreak()
            self.stdscr.keypad(False)
            self.stdscr.clear()
            curses.echo()
            curses.endwin()
        except Exception:
            pass
