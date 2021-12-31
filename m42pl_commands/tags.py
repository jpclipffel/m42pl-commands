from m42pl.commands import StreamingCommand
from m42pl.fields import Field, FieldsMap


class Tags(StreamingCommand):
    """Tags event.
    """
    _about_     = 'Tags events with key/value pairs'
    _syntax_    = '<key name>={field} [...]'
    _aliases_   = ['tag', 'tags']
    _schema_    = {
        'properties': {
            'tags': {
                'type': 'object',
                'description': 'Tags as key/value pairs',
            }
        }
    }

    def __init__(self, **kwargs):
        self.fields = FieldsMap(
            **dict([
                (k, Field(v))
                for k, v
                in kwargs.items()
            ])
        )
        self.tags = Field('tags')
    
    async def target(self, event, pipeline, context):
        yield await self.tags.write(
            event,
            (await self.fields.read(event, pipeline, context)).__dict__
        )