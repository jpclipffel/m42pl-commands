import json

from m42pl.pipeline import Pipeline
from m42pl.fields import Field
from m42pl.commands import MetaCommand, StreamingCommand, GeneratingCommand


class BaseMacro:
    kvstore_prefix = 'm42pl.macros'


class RecordMacro(BaseMacro, MetaCommand):
    """Record (define and save) a global macro.
    """

    _about_     = '''Record a global macro (use the 'macro' command instead)'''
    _syntax_    = '<name> [ ... ]'
    _aliases_   = ['_recordmacro',]

    def __init__(self, name: str, pipeline: str):
        """
        :param name:        Macro name.
        :param pipeline:    Macro pipeline ID.
        """
        super().__init__(name, pipeline)
        self.name = Field(name, default=name)
        self.pipeline = Field(pipeline)

    async def setup(self, event, pipeline):
        # Get macro name
        name = f'{self.kvstore_prefix}.{await self.name.read(event, pipeline)}'
        # Write macro to KVStore
        await pipeline.context.kvstore.write(
            name,
            pipeline.context.pipelines[self.pipeline.name].to_dict()
        )
        # Add macros to macros map
        await pipeline.context.kvstore.write(
            self.kvstore_prefix,
            await pipeline.context.kvstore.read(self.kvstore_prefix, list()).append(name)
        )


class RunMacro(BaseMacro, StreamingCommand):
    """Run a macro.

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
                await self.name.read(event, pipeline)
            )
        )
        self.pipeline.context = pipeline.context

    async def target(self, event, pipeline):
        async for _event in self.pipeline(event):
            yield _event


class GetMacros(BaseMacro, GeneratingCommand):
    """Returns the list of defined macros.
    """

    _about_     = 'Lists the available macros'
    _syntax_    = ''
    _aliases_   = ['_getmacros',]

    async def target(self, event, pipeline):
        async for 


class Macro(MetaCommand):
    """Record or run a macro.
    
    This command returns an instance of :class:`RecordMacro` or
    :class:`RunMacro` depending on what parameters are given.
    """
    _about_     = 'Record or run a macro'
    _syntax_    = '<name> [pipeline]'
    _aliases_   = ['macro',]

    def __new__(self, *args, **kwargs):
        if len(args) > 1 or len(kwargs) > 1 or 'pipeline' in kwargs:
            return RecordMacro(*args, **kwargs)
        else:
            return RunMacro(*args, **kwargs)
