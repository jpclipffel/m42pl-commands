import regex

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Cut(StreamingCommand):
    _about_     = 'Cut (split) a field using a regular expression'
    _syntax_    = '{field} <regular expression>'
    _aliases_   = ['cut', 'split']

    def __init__(self, field, expr):
        """
        :param field:   Source field to cut
        :param expr:    Regular expression
        """
        super().__init__(field, expr)
        self.field = Field(field)
        self.expr = Field(expr)

    async def setup(self, event, pipeline):
        self.expr = regex.compile(await self.expr.read(event, pipeline))

    async def target(self, event, pipeline):
        yield await self.field.write(
            event,
            self.expr.split(await self.field.read(event, pipeline))
        )
