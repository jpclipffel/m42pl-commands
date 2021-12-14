from m42pl.commands import GeneratingCommand
from m42pl.fields import Field


class Echo(GeneratingCommand):
    _about_     = 'Returns the received event or an empty event'
    _syntax_    = '[[count=]<count>]'
    _aliases_   = ['echo',]
    _schema_    = {'properties': {}}

    def  __init__(self, count: int = 1):
        super().__init__(count)
        self.count = Field(count, default=count, type=int)
    
    async def target(self, event, pipeline, context):
        count = await self.count.read(event, pipeline, context)
        while count > 0:
            yield event
            count -= 1
