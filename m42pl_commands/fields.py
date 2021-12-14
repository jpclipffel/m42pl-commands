from textwrap import dedent
from collections import OrderedDict

from m42pl.commands import StreamingCommand
from m42pl.fields import Field
from m42pl.event import Event


class Fields(StreamingCommand):
    _about_     = 'Keep (+) or remove (-) the selected fields'
    _syntax_    = '[+|-] field_name [, ...]'
    _aliases_   = ['fields',]
    _grammar_   = OrderedDict(StreamingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        MODE    : "+" | "-"
        fields  : (field ","?)+
        start   : MODE? fields
    ''')
    
    class Transformer(StreamingCommand.Transformer):
        MODE    = lambda self, items: str(items[0])
        fields  = list
        
        def start(self, items):
            return (), {
                'mode': len(items) > 1 and items[0] or '+',
                'fields': len(items) > 1 and items[1] or items[0]
            }
    
    def __init__(self, mode: str = '+', fields: list = []):
        """
        :param mode:    If set to '+', keep only the specified fields
                        If set of '-', remove the specified fields
                        Defaults to '+'
        :param fields:  List of fields to keep or remove.
        """
        super().__init__(mode, fields)
        self.mode = Field(mode, default=mode)
        self.fields = [Field(f) for f in fields]
    
    async def setup(self, event, pipeline, context):
        self.mode = await self.mode.read(event, pipeline, context)
        self.filter = self.mode == '+' and self.keep or self.remove

    async def keep(self, event):
        """Keep only the selected fields.
        """
        # WTF: Creating a new event without `data={}` uses current
        # event's data.
        # TODO: Debug and resolve issue
        _event = Event(data={}, sign=event['sign'])
        for field in self.fields:
            _event = await field.write(_event, await field.read(event))
        return _event
    
    async def remove(self, event):
        """Remove the selected fields.
        """
        for field in self.fields:
            await field.delete(event)
        return event
    
    async def target(self, event, pipeline, context):
        yield await self.filter(event)
