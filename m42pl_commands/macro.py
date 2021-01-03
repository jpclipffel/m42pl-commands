from m42pl.fields import Field
from m42pl.commands import MetaCommand, StreamingCommand


class RecordMacro(MetaCommand):
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
    def __init__(self, name: str):
        """
        :param name:    Macro name.
        """
        self.name = Field(name, default=name)

    async def setup(self, event, pipeline):
        self.pipeline = pipeline.context.pipelines[pipeline.macros[await self.name.read(event, pipeline)]]

    async def target(self, event, pipeline):
        async for _event in self.pipeline(event):
            yield event


class Macro(MetaCommand):
    _aliases_ = ['macro',]
    _syntax_ = '<name> [pipeline]'

    def __new__(self, *args, **kwargs):
        if len(args) > 1 or len(kwargs) > 1 or 'pipeline' in kwargs:
            return RecordMacro(*args, **kwargs)
        else:
            return RunMacro(*args, **kwargs)
