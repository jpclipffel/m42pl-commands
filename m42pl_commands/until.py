from copy import deepcopy

from m42pl.commands import StreamingCommand, GeneratingCommand
from m42pl.pipeline import Pipeline, InfiniteRunner
from m42pl.fields import Field


# class Until(StreamingCommand):
class Until(GeneratingCommand):
    """Run a sub-pipeline until a field become true.

    Only the latest event (where the given conditional field is `True`)
    is yield.
    """

    _about_     = 'Run a sub-pipeline until a field become true'
    _syntax_    = '<field> <pipeline>'
    _aliases_   = ['until',]

    def __init__(self, field: str, pipeline: str):
        """
        :param field:       Conditional field
        :param pipeline:    Pipeline ID
        """
        super().__init__(field, pipeline)
        self.field = Field(field)
        self.pipeline = Field(pipeline)

    async def setup(self, event, pipeline, context):
        self.runner = InfiniteRunner(
            pipeline.context.pipelines[self.pipeline.name],
            pipeline.context,
            event
        )
        await self.runner.setup()

    async def target(self, event, pipeline, context):
        source_event = event
        while True:
            async for next_event in self.runner(source_event):
                if (await self.field.read(next_event, pipeline)):
                    yield next_event
                    return
                latest_event = next_event
            source_event = latest_event
