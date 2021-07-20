from m42pl.commands import StreamingCommand
from m42pl.fields import Field
from m42pl.utils import grok


class Grok(StreamingCommand):
    _about_     = 'Parse a source field using a Grok expression'
    _syntax_    = '[expression=]<regex> [src=]<source_field> [[dest=]<dest_field>]'
    _aliases_   = ['grok',]
    _schema_    = {
        'properties': {
            '{dest}': {
                'type': 'object'
            }
        }
    }

    def __init__(self, expression, src, dest):
        self.expression = Field(expression)
        self.src = Field(src)
        self.dest = Field(dest)
    
    async def setup(self, event, pipeline):
        self.expression = grok.Grok(
            await self.expression.read(event, pipeline),
            keep_nameless=True,
            ignore_failed=True
        )
    
    async def target(self, event, pipeline):
        yield await self.dest.write(
            event,
            self.expression(await self.src.read(event, pipeline))
        )
