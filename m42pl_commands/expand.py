from copy import deepcopy

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Expand(StreamingCommand):
    _about_     = 'Returns one new event per value for the given field'
    _syntax_    = '[field=]<field name>'
    _aliases_   = ['expand', 'mvexpand']

    def __init__(self, field: str):
        self.field = Field(field, default=[], cast=[])

    async def target(self, event, pipeline):
        for item in await self.field.read(event):
            # Copy source event
            _event = deepcopy(event)
            # Copied events shares the same signature;
            # Ensure copied events have a unique signature by signing 
            # them individually
            _event.sign()
            # Set expanded field value to copied event and yield
            yield await self.field.write(_event, item)
