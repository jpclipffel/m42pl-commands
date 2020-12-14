from collections import OrderedDict
from textwrap import dedent

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Rename(StreamingCommand):
    _about_     = 'Rename fields'
    _syntax_    = '<existing field> as <new field> [, ...]'
    _aliases_   = ['rename',]

    _grammar_ = OrderedDict(StreamingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        expr    : field "as" field
        start   : (expr ","?)+
    ''')

    class Transformer(StreamingCommand.Transformer):
        def expr(self, items):
            return (items[0], items[1])
        
        def start(self, items):
            return (), {'fields': items}

    def __init__(self, fields: list):
        self.fields = [
            (Field(old), Field(new))
            for old, new
            in fields
        ]

    async def target(self, event, pipeline):
        for old, new in self.fields:
            # TODO: Add a `pop()` method to the field API
            # This will become:
            # >>> await new.write(event, wait old.pop(event))
            # Instead of:
            await new.write(event, await old.read(event))
            await old.delete(event)
        yield event
