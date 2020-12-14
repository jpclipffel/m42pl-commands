from m42pl.commands import GeneratingCommand
from m42pl.event import Event
from m42pl.fields import Field


class Read(GeneratingCommand):
    _about_     = 'Read a file content at once or line by line'
    _aliases_   = ['read', ]
    _syntax_    = '<[path=]path> [[mode=]{file|line}]'
    
    def __init__(self, path: str, mode: str = 'line'):
        super().__init__(path)
        self.path = Field(path)
        self.mode = Field(mode, default=mode)
    
    async def target(self, event, pipeline):
        mode = await self.mode.read(event, pipeline)
        with open(await self.path.read(event, pipeline), 'r') as fd:
            if mode == 'line':
                for line in fd.readlines():
                    yield Event(data={'line': line})
            elif mode == 'file':
                yield Event(data={'file': fd.read()})
