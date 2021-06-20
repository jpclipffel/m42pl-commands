import json

from m42pl.pipeline import Pipeline, InfiniteRunner
from m42pl.fields import Field
from m42pl.commands import MetaCommand, StreamingCommand, GeneratingCommand
from m42pl.utils.time import now


class BaseMacro:
    kvstore_prefix = 'macros:'
    kvstore_macros = f'{kvstore_prefix}current'

    def macro_name(self, name: str) -> str:
        """Returns a full macro name, i.e. with correct prefix.

        :param name:    Macro name as defined by user.
        """
        return f'{self.kvstore_prefix}{name}'


class RecordMacro(BaseMacro, MetaCommand):
    """Record (define and save) a global macro.
    """

    _about_     = '''Record a global macro (use the 'macro' command instead)'''
    _syntax_    = '<name> [ ... ]'
    _aliases_   = ['_recordmacro',]

    def __init__(self, name: str, pipeline: str, notes: str = None):
        """
        :param name:        Macro name
        :param pipeline:    Macro pipeline
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
            self.macro_name(macro_name),
            pipeline.context.pipelines[self.pipeline.name].to_dict()
        )
        # Write macro reference to KVStore macros list
        # macros = await pipeline.context.kvstore.read(self.kvstore_macros) or []
        # await pipeline.context.kvstore.write(
        #     self.kvstore_macros,
        #     macros + [macro_name,]
        # )
        macros = await pipeline.context.kvstore.read(self.kvstore_macros, default={})
        await pipeline.context.kvstore.write(
            self.kvstore_macros,
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
    _syntax_    = '<name>'
    _aliases_   = ['_macrorun', ]

    def __init__(self, name: str):
        """
        :param name:    Macro name.
        """
        super().__init__(name)
        self.name = Field(name, default=name)

    async def setup(self, event, pipeline):
        self.pipeline = Pipeline.from_dict(
            await pipeline.context.kvstore.read(
                self.macro_name(await self.name.read(event, pipeline))
            )
        )
        # self.pipeline.context = pipeline.context
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

    async def target(self, event, pipeline):
        macros = await pipeline.context.kvstore.read(self.kvstore_macros, default={})
        for name, macro in macros.items():
            yield derive(event, {
                'macro': {**{'name': name}, **macro}
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
        macro_name = self.macro_name(await self.name.read(event, pipeline))
        await pipeline.context.kvstore.remove(
            macro_name
        )
        # Remove macro reference from KVStore macros list
        macros = await pipeline.context.kvstore.read(self.kvstore_macros) or []
        await pipeline.context.kvstore.write(
            self.kvstore_macros,
            macros.remove(macro_name)
        )


class PurgeMacros(BaseMacro, MetaCommand):
    """Purges all macros.
    """
    _about_     = 'Purges all macros'
    _syntax_    = ''
    _aliases_   = ['purgemacro', 'purgemacros']

    async def target(self, event, pipeline):
        await pipeline.context.kvstore.remove(self.kvstore_prefix)
        await pipeline.context.kvstore.remove(self.kvstore_macros)


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
