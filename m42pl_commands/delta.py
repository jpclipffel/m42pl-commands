from m42pl.commands import StreamingCommand
from m42pl.event import derive
from m42pl.fields import Field


class Delta(StreamingCommand):
    """Computes the difference between the same fields of two consecutive events.
    """

    _aliases_   = ['delta', ]
    _about_     = 'Compute the difference between the same field of two consecutive events'
    _syntax_    = '[field=]<field>'

    def __init__(self, field: str = None):
        self.field = Field(field, default=field, type=(int, float))
        self.delta = Field('delta')
        self.latest = 0
        self.ready = False

    async def target(self, event, pipeline, context):
        current = await self.field.read(event, pipeline, context)
        if self.ready:
            delta = current - self.latest
        else:
            delta = 0
            self.ready = True
        self.latest = current
        yield await self.delta.write(
            event,
            delta
        )
