import regex
from collections import OrderedDict
from textwrap import dedent

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Regex(StreamingCommand):
    _about_   = 'Parse a field with a regular expression'
    _syntax_  = '{src} with <regular expression> [as|to {dest}]'
    _aliases_ = ['regex', 'rex', 'rx']
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

    def __init__(self, expression: str, src: str, dest: str = None,
                    update: bool = False):
        """
        :param expression: Regular expression with named groups
        :param src: Source field name
        :param dest: Destination field name
        :param update: Update the source field instead
        """
        super().__init__(expression, src, dest, update)
        self.expression = Field(expression)
        self.source_field = Field(src)
        self.dest_field = dest and Field(dest).name or ''
        self.update = Field(update, default=update)
        self.compiled = None

    async def setup(self, event, pipeline, context):
        if self.expression.literal:
            self.compiled = regex.compile(await self.expression.read(event, pipeline, context))
        self.update = await self.update.read(event, pipeline, context)

    async def target(self, event, pipeline, context):
        try:
            # ---
            # Run regex or compile-then-run regex
            if self.compiled:
                results = self.compiled.match(await self.source_field.read(event)).groupdict()
            else:
                expression = regex.compile(await self.expression.read(event, pipeline, context))
                results = expression.match(await self.source_field.read(event)).groupdict()
            # ---
            # Assign reslts fields
            if self.update:
                await self.source_field.write(event, results)
            else:
                for field, value in results.items():
                    await Field(f'{self.dest_field}.{field}').write(event, value)
        # ---
        # Handle exceptions
        # - AttributeError is raised when regex fails and `.groupdict()`
        #   does not exists.
        except AttributeError:
        # except Exception:
            pass
        yield event
