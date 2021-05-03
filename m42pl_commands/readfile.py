from collections import OrderedDict
from textwrap import dedent

from m42pl.commands import GeneratingCommand
from m42pl.event import Event
from m42pl.fields import Field


class ReadFile(GeneratingCommand):
    _about_     = 'Read a text file'
    _aliases_   = ['readfile']
    _syntax_    = '{file path} (as {field name})'

    _grammar_ = OrderedDict(GeneratingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        // start: field ("as" field)? arguments
        start: field ("as" field)?
    ''')

    class Transformer(GeneratingCommand.Transformer):
        def start(self, items):
            return items, {}

    def __init__(self, path: str, field: str = 'file'):
        """
        :param path:    Source file path
        :param dest:    Destination field
        """
        super().__init__(path)
        self.path = Field(path)
        self.field = Field(field, default=field)
    
    async def target(self, event, pipeline):
        try:
            with open(await self.path.read(event, pipeline), 'r') as fd:
                yield await self.field.write(event.derive(), fd.read())
        except Exception as _error:
            yield event
