import regex

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class ExtractKV(StreamingCommand):
    _about_     = 'Extract keys/values pairs from a given field'
    _syntax_    = (
        '[field=]<source field> '
        '[[kvdelim=]<key/value delimiter>] '
        '[[pairdelim=]<key/value pairs delimiter>] '
        '[[dest=]<dest field>]'
    )
    _aliases_   = ['extract_kv', 'extract_kvs']

    def __init__(self, field, kvdelim: str = '=', pairdelim: str = ',',
                    dest: str = None):
        """
        :param field:       Source field
        :param kvdelim:     Key and value delimiter regex
                            Defaults to an equal sign (=)
        :param pairdelim:   Key/value pairs delimiter regex
                            Defaults to a comma ( , )
        :param dest:        Destination field
                            Default to source field
        """
        super().__init__(field, kvdelim, pairdelim, dest)
        self.field = Field(field)
        self.kvdelim = Field(kvdelim, type=str, default='=')
        self.pairdelim = Field(pairdelim, type=str, default=',')
        self.dest = dest and Field(dest) or self.field
    
    async def setup(self, event, pipeline):
        self.kvdelim = regex.compile(
            await self.kvdelim.read(event, pipeline)
        )
        self.pairdelim = regex.compile(
            await self.pairdelim.read(event, pipeline)
        )

    async def target(self, event, pipeline):
        line = await self.field.read(event, pipeline)
        pairs = [
            kv for kv in [
                self.kvdelim.split(pair) for pair
                in filter(None, self.pairdelim.split(line))
            ] if len(kv) == 2
        ]
        yield await self.dest.write(event, dict(pairs))
