from copy import deepcopy

from m42pl.commands import StreamingCommand
from m42pl.fields import Field
from m42pl.event import Event


class Split(StreamingCommand):
    """Splits a event's field's values into new events.
    """

    _about_     = 'Returns one new event per value for the given field'
    _syntax_    = '[field=]{field name}'
    _aliases_   = ['split', 'mvsplit']
    _schema_    = {
        'additionalProperties': {
            'description': 'Source event properties'
        }
    }

    def __init__(self, field: str, keys: list = []):
        """
        :param field: Field to split on
        :param keys: New field names
        """
        super().__init__(field, keys)
        self.field = Field(field, default=[], seqn=True)
        self.keys = Field(keys, default=[], seqn=True)

    async def target(self, event, pipeline, context):
        keys = await self.keys.read(event, pipeline, context)
        for i, item in enumerate(await self.field.read(event, pipeline, context)):
            if isinstance(item, dict):
                yield Event(data=item)
            elif isinstance(item, (list, tuple)):
                if len(keys):
                    if i < len(keys):
                        yield Event(data={
                            keys[i]: item
                        })
                else:
                    yield Event(data={
                        await self.key.read(event, pipeline, context): item
                    })
