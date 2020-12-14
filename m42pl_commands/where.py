from textwrap import dedent
from collections import OrderedDict

from m42pl.commands import StreamingCommand
from m42pl.utils.eval import Evaluator
from m42pl.fields import Field


class Where(StreamingCommand):
    _about_     = 'Filter events with an eval expression'
    _aliases_   = ['where',]
    _syntax_    = '<expression>'
    _grammar_   = {'start': dedent('''\
        start   : /.+/
    ''')}

    class Transformer(StreamingCommand.Transformer):
        def start(self, items):
            return (), {'expression': str(items[0])}
        
    def __init__(self, expression: str):
        super().__init__(expression)
        self.expr = Evaluator(expression)

    async def target(self, event, piepline):
        try:
            if self.expr(event.data):
                yield event
        except Exception as error:
            print(error)
            raise
            # pass
