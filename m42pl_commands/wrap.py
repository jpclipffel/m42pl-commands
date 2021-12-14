from m42pl.commands import StreamingCommand
from m42pl.fields import Field
from m42pl.event import Event


class Wrap(StreamingCommand):
    """Encapsulates (wraps) all fields into a new field.
    """

    _about_     = 'Wraps all fields into another field'
    _syntax_    = '[field=]{field name}'
    _aliases_   = ['wrap',]

    def __init__(self, field = 'wrapped'):
        """
        :param field:   New field to wrap to.
        """
        self.field = field and Field(field, default=field) or None

    async def target(self, event, pipeline, context):
        if self.field:
            yield await self.field.write(Event(), event['data'])
        else:
            yield event
