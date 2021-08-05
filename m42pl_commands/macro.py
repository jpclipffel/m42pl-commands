from m42pl.pipeline import Pipeline, InfiniteRunner
from m42pl.event import derive
from m42pl.fields import Field
from m42pl.commands import MetaCommand, StreamingCommand, GeneratingCommand
from m42pl.utils.time import now
from m42pl.errors import CommandError


class BaseMacro:
    """Base macros-related command class.

    :ivar kvstore_prefix:   KVStore keys prefix
    :ivar macros_index:     List of macros in the KVStore 
    """

    kvstore_prefix = 'macros:'
    macros_index = f'{kvstore_prefix}current'

    def macro_fqdn(self, name: str) -> str:
        """Returns a full macro name, i.e. with correct prefix.

        :param name:    Macro name as defined by user
        """
        return f'{self.kvstore_prefix}{name}'


class RecordMacro(BaseMacro, MetaCommand):
    """Record (define and save) a global macro.
    """

    _about_     = '''Record a global macro (use the 'macro' command instead)'''
    _syntax_    = '<name> [ ... ] [notes]'
    _aliases_   = ['_recordmacro',]

    def __init__(self, name: str, pipeline: str, notes: str = None):
        """
        :param name:        Macro name
        :param pipeline:    Macro pipeline
        :param notes:       Macro's notes
        """
        super().__init__(name, pipeline)
        self.name = Field(name, default=name)
        self.pipeline = Field(pipeline)
        self.notes = Field(notes, default='')

    async def setup(self, event, pipeline):
        # Get macro name
        macro_name = await self.name.read(event, pipeline)
        # Write macro to KVStore
        await pipeline.context.kvstore.write(
            self.macro_fqdn(macro_name),
            pipeline.context.pipelines[self.pipeline.name].to_dict()
        )
        # Write macro reference to KVStore macros list
        # macros = await pipeline.context.kvstore.read(self.macros_index) or []
        # await pipeline.context.kvstore.write(
        #     self.macros_index,
        #     macros + [macro_name,]
        # )
        macros = await pipeline.context.kvstore.read(self.macros_index, default={})
        await pipeline.context.kvstore.write(
            self.macros_index,
            {
                **macros,
                **{
                    macro_name: {
                        'notes': await self.notes.read(event, pipeline),
                        'timestamp': now().timestamp(),
                        'author': ''
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

    def __init__(self, name: str, **kwargs):
        """
        :param name:    Macro name.
        """
        super().__init__(name)
        self.name = Field(name, default=name)
        self.kwargs = kwargs

    async def setup(self, event, pipeline):
        macro_name = await self.name.read(event, pipeline)
        macro_fqdn = self.macro_fqdn(macro_name)
        macro_dict = await pipeline.context.kvstore.read(macro_fqdn)
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
        event['data'].update(self.kwargs)
        # Init runner
        self.runner = InfiniteRunner(
            self.pipeline,
            pipeline.context,
            event
        )
        await self.runner.setup()

    async def target(self, event, pipeline):
        async for _event in self.runner(event):
            yield _event


class GetMacros(BaseMacro, GeneratingCommand):
    """Returns the list of defined macros.
    """

    _about_     = 'Returns available macros'
    _syntax_    = ''
    _aliases_   = ['macros',]

    key_name    = 'macro'

    async def target(self, event, pipeline):
        macros = await pipeline.context.kvstore.read(self.macros_index, default={})
        for name, macro in macros.items():
            if macro:
                yield derive(event, {
                    self.key_name: {**{'name': name}, **macro}
                })


class DelMacro(BaseMacro, MetaCommand):
    """Removes a macro.
    """
    _about_     = 'Remove a macro'
    _syntax_    = '{name}'
    _aliases_   = ['delmacro',]

    def __init__(self, name: str):
        """
        :param name:    Macro name.
        """
        super().__init__(name)
        self.name = Field(name, default=name)

    async def target(self, event, pipeline):
        macro_name = await self.name.read(event, pipeline)
        # Remove macro from KVStore
        await pipeline.context.kvstore.remove(
            self.macro_fqdn(macro_name)
        )
        # Remove macro reference from KVStore macros list
        macros = await pipeline.context.kvstore.read(self.macros_index, default={})
        macros.pop(macro_name)
        await pipeline.context.kvstore.write(
            self.macros_index,
            macros
        )


class PurgeMacros(BaseMacro, MetaCommand):
    """Purges all macros.
    """
    _about_     = 'Purges all macros'
    _syntax_    = ''
    _aliases_   = ['purgemacro', 'purgemacros']

    async def target(self, event, pipeline):
        await pipeline.context.kvstore.remove(self.kvstore_prefix)
        await pipeline.context.kvstore.remove(self.macros_index)


class Macro(MetaCommand):
    """Record or run a macro.
    
    This command returns an instance of :class:`RecordMacro`,
    :class:`RunMacro` or :class:`GteMacros` depending on what
    parameters are given.
    """
    _about_     = 'Record a macro, run a macro or return macros list'
    _syntax_    = '[<name> [pipeline]]'
    _aliases_   = ['macro',]

    def __new__(self, *args, **kwargs):
        if len(args) > 1 or len(kwargs) > 1 or 'pipeline' in kwargs:
            return RecordMacro(*args, **kwargs)
        elif len(args) == 1 or len(kwargs) == 1:
            return RunMacro(*args, **kwargs)
        else:
            return GetMacros()
