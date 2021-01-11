from copy import deepcopy

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Expand(StreamingCommand):
    _about_     = 'Returns one new event per value for the given field'
    _syntax_    = '[field=]<field name>'
    _aliases_   = ['expand', 'mvexpand']

    def __init__(self, field: str):
        """
        :param field:   Field to expand.
        """
        super().__init__(field)
        # ---
        # Field setup
        # - If not found, the field is an empty list
        # - If found, the field is casted to a list
        self.field = Field(field, default=[], seqn=True)

    async def target(self, event, pipeline):
        for item in await self.field.read(event):
            # Copy source event
            _event = deepcopy(event)
            _event.signature = None
            # Copied events shares the same signature;
            # Ensure copied events have a unique signature by signing 
            # them individually
            # _event.sign()
            # Set expanded field value to copied event and yield
            yield await self.field.write(_event, item)
