from copy import deepcopy

from m42pl.commands import StreamingCommand
from m42pl.fields import Field
from m42pl.event import derive


class Expand(StreamingCommand):
    """Duplicates an event for each given field's value.
    """

    _about_     = 'Duplicate event for each value of the given field'
    _syntax_    = '[field=]{field name}'
    _aliases_   = ['expand', 'mvexpand']
    _schema_    = {'properties': {}}

    def __init__(self, field: str):
        """
        :param field:   Field to expand on
        """
        super().__init__(field)
        self.field = Field(field, default=[], seqn=True)

    async def target(self, event, pipeline, context):
        for item in await self.field.read(event):
            yield await self.field.write(derive(event), item)
