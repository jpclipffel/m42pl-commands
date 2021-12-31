import regex

from m42pl.commands import StreamingCommand
from m42pl.fields import Field, FieldsMap


class Cut(StreamingCommand):
    """Cuts (splits) a field using a regular expression.
    """

    _about_     = 'Cut (split) a field using a regular expression'
    _syntax_    = '[field=]{field} [expr=]<regex> [[clean=]<yes|no>]'
    _aliases_   = ['cut', 'split']
    _schema_    = {
        'properties': {
            '{field}': {
                'type': 'array',
                'description': 'Cut field'
            }
        }
    }

    def __init__(self, field, expr: str, clean: bool = True):
        """
        :param field: Source field to cut
        :param expr: Regular expression
        """
        super().__init__(field, expr, clean)
        self.field = Field(field)
        self.fields = FieldsMap(**{
            'expr': Field(expr),
            'clean': Field(clean, default=True)
        })
        # self.expr = Field(expr)
        # self.clean = Field(clean, default=False)

    async def cut_filter(self, event, pipeline, context):
        return list(filter(
            None, 
            self.expr.split(await self.field.read(event, pipeline, context))
        ))
    
    async def cut_nofilter(self, event, pipeline, context):
        return self.expr.split(await self.field.read(event, pipeline, context))

    async def setup(self, event, pipeline, context):
        fields = await self.fields.read(event, pipeline, context)
        self.expr = regex.compile(fields.expr)
        self.cutter = fields.clean and self.cut_filter or self.cut_nofilter

    async def target(self, event, pipeline, context):
        yield await self.field.write(
            event,
            await self.cutter(event, pipeline, context)
        )
