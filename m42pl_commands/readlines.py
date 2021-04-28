from m42pl.commands import GeneratingCommand
from m42pl.event import Event
from m42pl.fields import Field


class ReadFile(GeneratingCommand):
    _about_     = 'Read an file line by line'
    _aliases_   = ['readlines', 'readline']
    _syntax_    = '[src=]{file path} [dest=]{dest field}'
    
    def __init__(self, src: str, dest: str = 'line'):
        """
        :param src:     Source file path
        :param dest:    Destination field
        """
        super().__init__(src, dest)
        self.src  = Field(src)
        self.dest = Field(dest, default='line')

    async def target(self, event, pipeline):
        try:
            with open(await self.src.read(event, pipeline), 'r') as fd:
                for chunk in fd.readlines():
                    for line in chunk.splitlines():
                        yield await self.dest.write(event.derive(), line)
        except Exception:
            yield event.derive()
