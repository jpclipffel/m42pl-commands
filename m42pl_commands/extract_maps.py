import regex

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class ExtractMap(StreamingCommand):
    _about_     = 'Extract values from a given field.'
    _syntax_    = (
        '[field=]<source field> '
        '[[headers=](headers)] '
        '[[prefix=]<key prefix>] '
        '[[delim=]<values delimiter>] '
        '[[dest=]<dest field>]'
    )
    _aliases_   = ['extract_map', 'extract_maps']
    _schema_    = {'properties': {}} # type: ignore

    def __init__(self, field, headers: list = [], prefix: str = '_',
                    delim: str = ',', dest: str = None):
        """
        :param field: Source field
        :param headers: Values keys (names)
        :param prefix: Values keys prefix if no or not enough header
            are provided; Defaults to 'the keys count
        :param delim: Values delimiter regex;
            Defaults to a comma ``,``
        :param dest: Destination field;
            Default to the source field
        """
        super().__init__(field, headers, delim, dest)
        self.field = Field(field)
        self.headers = Field(headers, seqn=True, default=[])
        self.prefix = Field(prefix, default='_')
        self.delim = Field(delim, type=str, default='=')
        self.dest = dest and Field(dest) or self.field

    def get_header(self):
        # First, yield headers
        # `self.headers` have been solved in `setup` at this step
        yield from self.headers
        # Then, yield enumerated headers with prefix and count
        # `self.prefix` have been solved in `setup` at this step
        count = -1
        while True:
            count += 1
            yield f'{self.prefix}{count}'

    async def setup(self, event, pipeline, context):
        self.headers = await self.headers.read(event, pipeline, context)
        self.prefix = await self.prefix.read(event, pipeline, context)
        self.delim = regex.compile(
            await self.delim.read(event, pipeline, context)
        )

    async def target(self, event, pipeline, context):
        line = await self.field.read(event, pipeline, context)
        yield await self.dest.write(
            event, 
            dict(zip(
                self.get_header(),
                filter(None, self.delim.split(line))
            ))
        )
