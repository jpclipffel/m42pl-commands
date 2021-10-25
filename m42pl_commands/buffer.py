from m42pl.commands import DequeBufferingCommand
from m42pl.fields import Field


class Buffer(DequeBufferingCommand):
    """Simple buffer command example.

    The command simply buffers the given amount of events before
    yielding them.
    """

    _about_     = 'Delays events processing'
    _syntax_    = '[[size=]<buffer size>] [[showchunk=]<yes|no>]'
    _aliases_   = ['buffer', ]
    _schema_    = {'properties': {}}

    def __init__(self, size: int = 128, showchunk: bool = False,
                    chunkfield: str = 'chunk'):
        super().__init__(size)
        self.size = Field(size, default=128)
        self.showchunk = Field(showchunk, default=False)
        self.chunkfield = Field(chunkfield, default='chunk')
        self.chunks = 1

    async def setup(self, event, pipeline):
        await super().setup(
            event,
            pipeline,
            await self.size.read(event, pipeline)
        )
        self.showchunk = await self.showchunk.read(event, pipeline)

    async def target(self, pipeline):
        async for event in super().target(pipeline):
            if self.showchunk:
                yield await self.chunkfield.write(event, self.chunks)
            else:
                yield event
        self.chunks += 1
