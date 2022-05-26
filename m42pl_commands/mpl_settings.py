import m42pl
import m42pl.commands
from m42pl.event import derive
from m42pl.fields import FieldsMap, Field


class MPLSettings(m42pl.commands.GeneratingCommand):
    _about_     = 'Returns the list of settings'
    _syntax_    = '<scope>.<name>'
    _aliases_   = ['mpl_settings', 'mpl_setting', 'settings', 'setting']
    _schema_    = {}
    
    def __init__(self, scope: str, name: str):
        """
        :param scope: Setting scope
        :param name: Setting name
        """
        super().__init__(scope, name)
        self.fields = FieldsMap(**{
            'scope': Field(scope, default=scope, type=str),
            'name': Field(name, default=name, type=str)
        })


    async def target(self, event, pipeline, context):
        self.fields = await self.fields.read(event, pipeline, context)
        yield derive(event, data={
            'setting': {
                'scope': self.fields.scope,
                'name': self.fields.name,
                'value': m42pl.setting(self.fields.scope, self.fields.name)
            }
        })
