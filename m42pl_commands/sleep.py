import asyncio

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Sleep(StreamingCommand):
    _about_     = 'Sleep for the given amount of seconds (defaults to 1 second)'
    _syntax_    = '<seconds>'
    _aliases_   = ['sleep',]
    _schema_    = {'properties': {}} # type: ignore

    def __init__(self, seconds: int = 1):
        """
        :param seconds: Time to wait in seconds
        """
        super().__init__(seconds)
        self.seconds = Field(seconds, default=seconds)

    async def setup(self, event, pipeline, context):
        self.seconds = await self.seconds.read(event, pipeline, context)

    async def target(self, event, pipeline, context):
        await asyncio.sleep(self.seconds)
        yield event
