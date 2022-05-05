from collections import OrderedDict
from textwrap import dedent

from m42pl.commands import StreamingCommand
from m42pl.fields import Field
from m42pl.utils import grok


class Grok(StreamingCommand):
    _about_     = 'Parse a field with a Grok expression'
    _syntax_    = '{src} with <grok expression> [as|to {dest}]'
    _aliases_   = ['grok',]
    _schema_    = {
        'properties': {
            '{dest}': {
                'type': 'object'
            }
        }
    }

    _grammar_ = OrderedDict(StreamingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        start:  field "with" field (("as"|"to") field)?
    ''')

    class Transformer(StreamingCommand.Transformer):
        def start(self, items):
            return (), {
                'expression': items[1],
                'src': items[0],
                'dest': len(items) > 2 and items[2] or None,
            }

    def __init__(self, expression, src, dest):
        super().__init__(expression, src, dest)
        self.expression = Field(expression)
        self.src = Field(src)
        self.dest = dest and Field(dest).name or ''
        self.compiled = None
    
    async def setup(self, event, pipeline, context):
        if self.expression.literal:
            self.compiled = grok.Grok(
                await self.expression.read(event, pipeline, context),
                keep_nameless=True,
                ignore_failed=True
            )
    
    async def target(self, event, pipeline, context):
        if self.compiled:
            results = self.compiled(await self.src.read(event, pipeline, context))
        else:
            results = grok.Grok(await self.expression.read(event, pipeline, context),
                keep_nameless=True,
                ignore_failed=True
            )(await self.src.read(event, pipeline, context))
        # ---
        for field, value in results.items():
            await Field(f'{self.dest}.{field}').write(event, value)
        yield event
        # yield await self.dest.write(
        #     event,
        #     self.compiled(await self.src.read(event, pipeline, context))
        # )
