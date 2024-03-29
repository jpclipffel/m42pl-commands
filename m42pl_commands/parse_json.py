import json

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class ParseJson(StreamingCommand):
    _about_     = 'Parse a JSON string'
    _syntax_    = '[field=]<field>'
    _aliases_   = ['parse_json', 'json_parse']
    _schema_    = {
        'properties': {
            '{field}': {
                'type': 'object',
                'description': 'String parsed as object'
            }
        }
    }

    def __init__(self, field: str):
        """
        :param field:   Field name to parse.
        """
        super().__init__(field)
        self.field = Field(field)

    async def target(self, event, pipeline, context):
        try:
            yield await self.field.write(
                event,
                json.loads(await self.field.read(event, pipeline, context))
            )
        except Exception:
            raise
            yield event
