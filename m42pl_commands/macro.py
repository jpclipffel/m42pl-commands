from m42pl.fields import Field
from m42pl.commands import MetaCommand, StreamingCommand


class RecordMacro(MetaCommand):
    """Record (define and save) a macro.

    This command is returned the command `| macro` (:class:`Macro`)
    when it deduces a macro should be recorded.
    """
    def __init__(self, name: str, pipeline: str):
        """
        :param name:        Macro name.
        :param pipeline:    Macro pipeline.
        """
        self.name = Field(name, default=name)
        self.pipeline = Field(pipeline)
    
    async def setup(self, event, pipeline):
        pipeline.macros[await self.name.read(event, pipeline)] = self.pipeline.name


class RunMacro(StreamingCommand):
    """Run a macro.

    This command is returned the command `| macro` (:class:`Macro`)
    when it deduces a macro should be run.
    """
    def __init__(self, name: str):
        """
        :param name:    Macro name.
        """
        self.name = Field(name, default=name)

    async def setup(self, event, pipeline):
        self.pipeline = pipeline.context.pipelines[pipeline.macros[await self.name.read(event, pipeline)]]

    async def target(self, event, pipeline):
        async for _event in self.pipeline(event):
            yield _event


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
