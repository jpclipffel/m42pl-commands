from textwrap import dedent
from collections import OrderedDict

from m42pl.commands import StreamingCommand
from m42pl.utils.eval import Evaluator
from m42pl.fields import Field


class Where(StreamingCommand):
    """Filters event using an evaluation expression.
    """

    _about_     = 'Filter events using an eval expression'
    _aliases_   = ['where', 'filter']
    _syntax_    = '<expression>'
    _schema_    = {'properties': {}} # type: ignore

    _grammar_   = {'start': dedent('''\
        start   : /.+/
    ''')}

    class Transformer(StreamingCommand.Transformer):
        def start(self, items):
            return (), {'expression': str(items[0])}
        
    def __init__(self, expression: str):
        """
        :param expression: Conditional expression
        """
        super().__init__(expression)
        self.expr = Evaluator(expression)

    async def target(self, event, pipeline, context):
        try:
            if self.expr(event['data']):
                yield event
        except Exception:
            raise
