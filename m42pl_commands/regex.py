import regex

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Regex(StreamingCommand):
    _about_   = 'Parse a source field using a regular expression with named groups'
    _syntax_  = '[expression=]<regex> [src=]<source_field> [[dest=]<dest_field>] [[update=](yes|no)]'
    _aliases_ = ['regex', 'rex', 'rx']
    
    def __init__(self, expression: str, src: str, dest: str = None,
                    update: bool = False):
        """
        :param expression:  Regular expression with named groups
        :param src:         Source field name
        :param dest:        Destination field name
        :param update:      Update the source field instead
        """
        super().__init__(expression, src, dest, update)
        self.expression = Field(expression)
        self.source_field = Field(src)
        self.dest_field = dest and Field(dest).name or ''
        self.update = Field(update, default=update)
        self.compiled = None

    async def setup(self, event, pipeline):
        if self.expression.literal:
            self.compiled = regex.compile(await self.expression.read(event, pipeline))
        self.update = await self.update.read(event, pipeline)

    async def target(self, event, pipeline):
        try:
            # ---
            # Run regex or compile-then-run regex
            if self.compiled:
                results = self.compiled.match(await self.source_field.read(event)).groupdict()
            else:
                expression = regex.compile(await self.expression.read(event, pipeline))
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
            pass
        yield event
