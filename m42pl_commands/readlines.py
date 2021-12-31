from m42pl.commands import GeneratingCommand
from m42pl.event import Event, derive
from m42pl.fields import Field


class ReadLines(GeneratingCommand):
    """Reads a text file line by line.

    To read a whole text file at once, see ``ReadFile``.
    """

    _about_     = 'Read a file line by line'
    _aliases_   = ['readlines', 'readline']
    _syntax_    = '[path=]{file path} [field=]{dest field}'
    _schema_    = {
        'properties': {
            '{dest field}': {
                'type': 'object',
                'properties': {
                    'text': {'type': 'string', 'description': 'Read line'},
                    'line': {'type': 'number', 'description': 'Line count'}
                }
            }
        }
    }
    
    def __init__(self, path: str, field: str = 'line'):
        """
        :param path: Source file path
        :param dest: Destination field
        """
        super().__init__(path, field)
        self.path = Field(path)
        self.field = Field(field, default='line')

    async def target(self, event, pipeline, context):
        try:
            with open(await self.path.read(event, pipeline, context), 'r') as fd:
                line = 0
                for chunk in fd.readlines():
                    for text in chunk.splitlines():
                        yield await self.field.write(
                            derive(event),
                            {
                                'text': text,
                                'line': line
                            }
                        )
                        line += 1
        except Exception:
            yield event
