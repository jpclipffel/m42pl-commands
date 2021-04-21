from m42pl.commands import StreamingCommand
from m42pl.event import Event
from m42pl.fields import Field
from m42pl.utils import formatters


class WriteFile(StreamingCommand):
    _about_     = 'Write events to a file'
    _syntax_    = '[path=]{path} [[mode=](replace|append)]'
    _aliases_   = ['writefile',]

    def __init__(self, path: str, mode: str = 'replace', *args):
        """
        :param path:    File path
        :param mode:    Write mode (`replace` or `append`)
                        Defaults to `replace`.
        """
        super().__init__(path, mode, *args)
        self.path = Field(path)
        self.mode = Field(mode, default='replace')
        self.modes = {'replace': 'w', 'append': 'w+'}
        self.cache = {}
        self.formatter = formatters.Json(indent=2)

    async def setup(self, event, pipeline):
        # Setup file write mode
        self.mode = self.modes.get(
            (await self.mode.read(event, pipeline)).lower(),
            'replace'
        )

    async def format(self, event, pipeline):
        return self.formatter(event)

    async def target(self, event, pipeline):
        path = await self.path.read(event, pipeline)
        # Open given file at `path` and add it to cache
        if path not in self.cache:
            self.cache[path] = open(path, self.mode)
        # Write event to file
        self.cache[path].write(await self.format(event, pipeline))
        # Done
        yield event

    async def __aexit__(self, *args, **kwargs):
        for _, fd in self.cache.items():
            try:
                fd.close()
            except Exception:
                pass


class WriteFileField(WriteFile):
    _about_     = 'Write a single field to a file'
    _syntax_    = f'{WriteFile._syntax_} [field=]<field>'
    _aliases_   = ['writefile_field',]

    def __init__(self, path: str, field: str, mode: str = 'replace'):
        super().__init__(path, mode, field)
        self.field = Field(field, default='')

    async def format(self, event, pipeline):
        return await self.field.read(event, pipeline)
