from textwrap import dedent
from collections import OrderedDict

from m42pl.commands import StreamingCommand
from m42pl.utils.eval import Evaluator
from m42pl.fields import Field
from m42pl.errors import CommandError


class Assertion(StreamingCommand):
    """Assert an Python `eval` expression.
    """

    _about_     = 'Fails the pipeline if the given expression is false'
    _aliases_   = ['assert',]
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
        :param expression: Expression to assert
        """
        super().__init__(expression)
        self.expr = Evaluator(expression)

    async def target(self, event, *args, **kwargs):
        if not self.expr(event['data']):
            raise Exception('assertion failed')
        yield event
