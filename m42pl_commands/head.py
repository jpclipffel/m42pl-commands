from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Head(StreamingCommand):
    _about_     = 'Keep only the firsts events'
    _syntax_    = '[[count=]<count>]'
    _aliases_   = ['head',]
    _schema_    = {'properties': {}} # type: ignore

    def __init__(self, count: int = 1):
        """
        :param count:   Number of events to keep.
                        Defaults to 1.
        """
        self.count = Field(count, default=1)
    
    async def setup(self, event, pipeline, context):
        self.count = await self.count.read(event, pipeline, context)
    
    async def target(self, event, pipeline, context):
        if self.count > 0:
            self.count -= 1
            yield event
        else:
            yield None
