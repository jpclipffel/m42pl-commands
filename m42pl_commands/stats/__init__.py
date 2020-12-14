from textwrap import dedent
from itertools import chain
from collections import OrderedDict

from m42pl.commands import StreamingCommand, MergingCommand
from m42pl.event import Event
from m42pl.fields import Field

# Stats functors
from . import functions as stats_functions



class StreamStats(StreamingCommand):
    _aliases_ = ['_streamstats', ]

    def __init__(self, functions: list, fields: list):
        '''
        :param functions:   Aggregation functions list.
                            Ex: `[('function_name', 'source_field', 'dest_field')]`
        :param fields:      Aggregation fields list.
        '''
        super().__init__(functions, fields)
        self.aggr_fields = [Field(f) for f in fields]
        self.aggregates = {} # type: dict
        # ---
        # Build stated fields map (== functions calling map)
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
    _aliases_ = ['_poststats', ]

    async def target(self, event, pipeline):
        yield event


class Stats(StreamingCommand):
    _about_   = 'Performs statistical operations on an event stream'
    _syntax_  = 'stats ( <function> [ as <field> ] [, ...] ) by ( <field> [, ...] )'
    _aliases_ = ['stats', 'aggr', 'aggregate', ]

    # __grammar_blocks__ = StreamingCommand.__base_grammar_blocks__
    # __grammar_blocks__['start'] = dedent('''\
    #     function_name   : NAME
    #     function_body   : ( "(" eval_expression? ")" )?
    #     function_alias  : ("as" field)?
    #     function        : function_name function_body function_alias
    #     functions       : function (","? function)*
    #     fields          : field+
    #     start           : functions "by" fields
    # ''')

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
        '''Command's Lark transformer.
        '''
        function_name   = lambda self, items: str(items[0])
        function_body   = lambda self, items: len(items) and str(items[0]) or None
        function_alias  = lambda self, items: len(items) and str(items[0]) or None
        function        = tuple
        functions       = list
        field           = str
        fields          = list
        start           = lambda self, items: (tuple(), { 'functions': items[0], 'fields': items[1] })  # type: ignore

    def __new__(self, *args, **kwargs):
        return StreamStats(*args, **kwargs), PostStats()
