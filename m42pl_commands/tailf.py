from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Tailf(StreamingCommand):
    _about_     = 'Ignore the firsts events'
    _syntax_    = '[[count=]<count>]'
    _aliases_   = ['tailf',]
    _schema_    = {
        'additionalProperties': {
            'description': 'Source event properties'
        }
    }

    def __init__(self, count: int = 1):
        """
        :param count: Number or events to ignore (defaults to 1)
        """
        super().__init__(count)
        self.count = Field(count, default=1)
    
    async def setup(self, event, pipeline, context):
        self.count = await self.count.read(event, pipeline, context)
    
    async def target(self, event, pipeline, context):
        if self.count > 0:
            self.count -= 1
        else:
            yield event
