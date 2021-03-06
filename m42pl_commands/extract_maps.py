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

    def __init__(self, field, headers: list = [], prefix: str = '_',
                    delim: str = ',', dest: str = None):
        """
        :param field:       Source field
        :param headers:     Values keys (names)
        :param prefix:      Values keys prefix (if no or not enough 
                            header provided)
                            Default to 'N' where N is the key count
        :param delim:       Values delimiter regex
                            Defaults to a comma ( , )
        :param dest:        Destination field
                            Default to source field
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

    async def setup(self, event, pipeline):
        self.headers = await self.headers.read(event, pipeline)
        self.prefix = await self.prefix.read(event, pipeline)
        self.delim = regex.compile(
            await self.delim.read(event, pipeline)
        )

    async def target(self, event, pipeline):
        line = await self.field.read(event, pipeline)
        yield await self.dest.write(
            event, 
            dict(zip(
                self.get_header(),
                filter(None, self.delim.split(line))
            ))
        )
