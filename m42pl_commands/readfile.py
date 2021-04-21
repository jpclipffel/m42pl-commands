from m42pl.commands import GeneratingCommand
from m42pl.event import Event
from m42pl.fields import Field


class ReadFile(GeneratingCommand):
    _about_     = 'Read a local file'
    _aliases_   = ['readfile']
    _syntax_    = '[path=]{file path} [dest=]{dest field} [[mode=](file|line)]'
    
    def __init__(self, path: str, field: str = 'file', mode: str = 'line'):
        """
        :param path:    File path
        :param field:   Destination field
        :param mode:    Read mode
                        If mode is 'line', yields file line by line.
                        If mode is 'file', yields file at once.
                        Defaults to 'line'.
        """
        super().__init__(path)
        self.path = Field(path)
        self.field = Field(field, default=field)
        self.mode = Field(mode, default=mode)
    
    async def target(self, event, pipeline):
        path = await self.path.read(event, pipeline)
        mode = await self.mode.read(event, pipeline)
        try:
            with open(path, 'r') as fd:
                if mode == 'line':
                    for chunk in fd.readlines():
                        for line in chunk.splitlines():
                            yield await self.field.write(event.derive(), line)
                        # yield event.derive(data={
                        #     'path': path,
                        #     'line': line
                        # })
                elif mode == 'file':
                    yield await self.field.write(event.derive(), fd.read())
                    # yield event.derive(data={
                    #     'path': path,
                    #     'file': fd.read()
                    # })
        except Exception:
            yield event.derive()
