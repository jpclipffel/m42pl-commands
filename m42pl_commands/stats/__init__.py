from textwrap import dedent
from itertools import chain
from collections import OrderedDict

from m42pl.commands import StreamingCommand, MergingCommand
from m42pl.event import Event
from m42pl.fields import Field

# Stats functors
# Each stats functions (aka. functors) is defined in its own module.
# The module 'functions' (imported here as 'stats_functions') holds a
# a dict named 'names' which map a stats function name with its class.
from . import functions as stats_functions


class StreamStats(StreamingCommand):
    """Handle the statistical operations.
    """
    _aliases_ = ['_streamstats',]

    def __init__(self, functions: list, fields: list):
        """
        :param functions:   Aggregation functions list.
                            Ex: `[('function_name', 'source_field', 'dest_field')]`
        :param fields:      Aggregation fields list.
        """
        super().__init__(functions, fields)
        self.aggr_fields = [Field(f) for f in fields]
        self.aggregates = {} # type: dict
        # ---
        # Build the stated fields map (== functions calling map)
        self.stated_fields = {}
        for function in functions:
            # Extract and format function name, source field and destination field names
            function_name, source_field, dest_field , *_ = chain(function, [None] * 3)
            source_field = Field(source_field)
            dest_field = dest_field and Field(dest_field) or Field(f'{function_name}({source_field.name or ""})')
            # Add destination field and function call
            if function_name in stats_functions.names:
                self.stated_fields[dest_field] = stats_functions.names[function_name](source_field, self.aggr_fields, dest_field, self.aggregates)
            else:
                raise Exception(f'No such stats function: {function_name}')

    async def target(self, event, pipeline):
        # Sign source event
        event.sign(self.aggr_fields)
        # Create new event which will hold the aggregated values
        stated_event = Event(signature=event.signature)
        # Compute and add the stated fields to the new event
        for field, function in self.stated_fields.items():
            await field.write(stated_event, await function(event, pipeline))
        # Add the aggregated-by fields to the new event
        for field in self.aggr_fields:
            await field.write(stated_event, await field.read(event))
        # Done
        stated_event.sign(self.aggr_fields)
        yield stated_event


class PostStats(MergingCommand):
    """PostStats *will* be used to aggregate stats results.
    """
    _aliases_ = ['_poststats',]

    async def target(self, event, pipeline):
        yield event


class Stats(StreamingCommand):
    """Stats command entry point.
    """

    _about_   = 'Performs statistical operations on an event stream'
    _syntax_  = 'stats <function> [as <field>], ... by <field>, ...'
    _aliases_ = ['stats', 'aggr', 'aggregate']
    _grammar_ = OrderedDict(StreamingCommand._grammar_)
    _grammar_.pop('collections_rules')
    _grammar_['stats_rules'] = dedent('''\
        function_name   : NAME
        function_body   : ( "(" field? ")" )?
        function_alias  : ("as" field)?
        function        : function_name function_body function_alias
        functions       : (function ","?)+
        fields          : (field ","?)+
    ''')
    _grammar_['start'] = dedent('''\
        start       : functions "by" fields
    ''')

    class Transformer(StreamingCommand.Transformer):
        function_name   = lambda self, items: str(items[0])
        function_body   = lambda self, items: len(items) and str(items[0]) or None
        function_alias  = lambda self, items: len(items) and str(items[0]) or None
        function        = tuple
        functions       = list
        field           = str
        fields          = list
        start           = lambda self, items: (tuple(), { 'functions': items[0], 'fields': items[1] })  # type: ignore

    def __new__(self, *args, **kwargs):
        """Create the required stats commands instances.
        
        The `stats` commands works with two subcommands:

        * `_streamstats` performs the actual statistical operations.
          Ultimately, I must switch to NumPy or Pandas instead of
          using a self-made implementation of the stats functors.
        * `_postats` collect the stat-ed events and performs the late
          operations / functors. This will be needed for instance when
          calculating a mean using a pipeline dispatched among multiple
          processes.
        """
        return StreamStats(*args, **kwargs), PostStats()
