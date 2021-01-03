import asyncio

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Sleep(StreamingCommand):
    _about_     = 'Sleep for the given amount of seconds (defaults to 1 second)'
    _syntax_    = '<seconds>'
    _aliases_   = ['sleep',]

    def __init__(self, seconds: int = 1):
        super().__init__(seconds)
        self.seconds = Field(seconds, default=seconds)

    async def setup(self, event, pipeline):
        self.seconds = await self.seconds.read(event, pipeline)

    async def target(self, event, pipeline):
        await asyncio.sleep(self.seconds)
        yield event
