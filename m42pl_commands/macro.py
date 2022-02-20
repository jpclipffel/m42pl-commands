from m42pl.pipeline import Pipeline, InfiniteRunner
from m42pl.event import derive
from m42pl.fields import Field, FieldsMap
from m42pl.commands import MetaCommand, StreamingCommand, GeneratingCommand
from m42pl.utils.time import now
from m42pl.errors import CommandError


class BaseMacro:
    """Base macros-related command class.

    :ivar kvstore_prefix: KVStore keys prefix
    :ivar macros_index: Key to the list of macros
    """

    kvstore_prefix = 'macros:'
    macros_index = f'{kvstore_prefix}current'

    def macro_fqdn(self, name: str) -> str:
        """Returns a macro full name (prefix + name)

        :param name: Macro name as defined by user
        """
        return f'{self.kvstore_prefix}{name}'


class RecordMacro(BaseMacro, MetaCommand):
    """Records a macro.
    """

    _about_     = '''Record a global macro (use the 'macro' command instead)'''
    _syntax_    = '<name> [ ... ] [notes]'
    _aliases_   = ['_recordmacro',]
    _schema_    = {'properties': {}} # type: ignore

    def __init__(self, name: str, pipeline: str, notes: str = None):
        """
        :param name: Macro name
        :param pipeline: Macro code
        :param notes: Macro notes
        """
        super().__init__(name, pipeline)
        self.name = Field(name, default=name)
        self.pipeline = Field(pipeline)
        self.notes = Field(notes, default='')

    async def setup(self, event, pipeline, context):
        # Get macro name
        macro_name = await self.name.read(event, pipeline, context)
        # Renders macros dict
        macro_dict = context.pipelines[self.pipeline.name].to_dict()
        # Write macro to KVStore
        await context.kvstore.write(
            self.macro_fqdn(macro_name),
            macro_dict
        )
        # Write macro reference to KVStore macros list
        # macros = await context.kvstore.read(self.macros_index) or []
        # await context.kvstore.write(
        #     self.macros_index,
        #     macros + [macro_name,]
        # )
        macros = await context.kvstore.read(self.macros_index, default={})
        await context.kvstore.write(
            self.macros_index,
            {
                **macros,
                **{
                    macro_name: {
                        'notes': await self.notes.read(event, pipeline, context),
                        'timestamp': now().timestamp(),
                        'author': '',
                        'json': macro_dict
                    }
                }
            }
        )


class RunMacro(BaseMacro, StreamingCommand):
    """Runs a macro.

    This command is returned the command `| macro` (:class:`Macro`)
    when it deduces a macro should be run.
    """

    _about_     = '''Run a macro (use 'macro' command instead )'''
    _syntax_    = '[name=]<name> [{field}=<value>, ...]'
    _aliases_   = ['_macrorun', ]
    _schema_    = {'additionalProperties': True}

    def __init__(self, name: str, macro_kwargs: dict = {}):
        """
        :param name:    Macro name.
        """
        super().__init__(name)
        self.name = Field(name, default=name)
        self.params = FieldsMap(**dict([
            (name, Field(field))
            for name, field
            in macro_kwargs.items()]
        ))

    async def setup(self, event, pipeline, context):
        macro_name = await self.name.read(event, pipeline, context)
        macro_fqdn = self.macro_fqdn(macro_name)
        macro_dict = await context.kvstore.read(macro_fqdn)
        if macro_dict is None:
            raise CommandError(
                self,
                f'requested macro "{macro_name}" not found: macro_fqdn="{macro_fqdn}"'
            )
        # Init macro
        self.pipeline = Pipeline.from_dict(
            macro_dict
        )
        # Init macro event
        self.params = await self.params.read(event, pipeline, context)
        event['data'].update(self.params.__dict__)
        # Init runner
        self.runner = InfiniteRunner(
            self.pipeline,
            context,
            event
        )
        await self.runner.setup()

    async def target(self, event, pipeline, context):
        async for _event in self.runner(event):
            yield _event


class GetMacros(BaseMacro, GeneratingCommand):
    """Returns the list of defined macros.
    """

    _about_     = 'Returns available macros'
    _syntax_    = ''
    _aliases_   = ['macros',]
    _schema_    = {
        'properties': {
            'macro': {'description': 'Macro definition'}
        }
    }

    key_name    = 'macro'

    async def target(self, event, pipeline, context):
        macros = await context.kvstore.read(self.macros_index, default={})
        for name, macro in macros.items():
            if macro:
                yield derive(event, {
                    self.key_name: {**{'name': name}, **macro}
                })


class DelMacro(BaseMacro, MetaCommand):
    """Deletes a macro.
    """

    _about_     = 'Remove a macro'
    _syntax_    = '{name}'
    _aliases_   = ['delmacro',]
    _schema_    = {'properties': {}} # type: ignore

    def __init__(self, name: str):
        """
        :param name: Macro name.
        """
        super().__init__(name)
        self.name = Field(name, default=name, seqn=True)

    async def target(self, event, pipeline, context):
        macro_names = await self.name.read(event, pipeline, context)
        for macro_name in macro_names:
            # Remove macro from KVStore
            try:
                await context.kvstore.delete(
                    self.macro_fqdn(macro_name)
                )
            except Exception:
                pass
            # Remove macro reference from KVStore macros list
            try:
                macros = await context.kvstore.read(self.macros_index, default={})
                macros.pop(macro_name)
                await context.kvstore.write(
                    self.macros_index,
                    macros
                )
            except Exception:
                pass


class PurgeMacros(BaseMacro, MetaCommand):
    """Deletes all macros.
    """

    _about_     = 'Purges all macros'
    _syntax_    = ''
    _aliases_   = ['purgemacro', 'purgemacros']
    _schema_    = {'properties': {}} # type: ignore

    async def target(self, event, pipeline, context):
        await context.kvstore.remove(self.kvstore_prefix)
        await context.kvstore.remove(self.macros_index)


class CloseMacro(StreamingCommand):
    pass


class Macro(MetaCommand):
    """Record or run a macro.
    
    This command returns an instance of :class:`RecordMacro`,
    :class:`RunMacro` or :class:`GetMacros` depending on what
    parameters are given.
    """
    
    _about_     = 'Record a macro, run a macro or return macros list'
    _syntax_    = '[<name> [pipeline]]'
    _aliases_   = ['macro',]
    _schema_    = {'properties': {}} # type: ignore

    def __new__(self, *args, **kwargs):
        if len(args) > 1 or len(kwargs) > 1 or 'pipeline' in kwargs:
            return RecordMacro(*args, **kwargs), CloseMacro()
        elif len(args) == 1 or len(kwargs) == 1:
            return RunMacro(*args, macro_kwargs=kwargs), CloseMacro()
        else:
            return GetMacros(), CloseMacro()
