from collections import OrderedDict
from textwrap import dedent
import asyncio

from m42pl.commands import StreamingCommand
from m42pl.pipeline import InfiniteRunner, PipelineRunner
from m42pl.fields import Field
from m42pl.event import derive


class Limit(StreamingCommand):
    """Runs a sub-pipeline until a given a number of events are yield.
    """

    _about_     = 'Run a sub-pipeline for a limited amount of event'
    _syntax_    = '[count=]<event count> <pipeline>'
    _aliases_   = ['limit',]
    _schema_    = {'properties': {}} # type: ignore

    def __init__(self, count, pipeline):
        """
        :param count:       Event count limit
        :param pipeline:    Pipeline reference
        """
        super().__init__(count, pipeline)
        self.count = Field(count)
        self.pipeline = Field(pipeline)

    async def setup(self, event, pipeline, context):
        self.count = await self.count.read(event, pipeline, context)
        self.runner = PipelineRunner(context.pipelines[self.pipeline.name])

    async def __call__(self, event, pipeline, context, ending, *args, **kwargs):
        received = 0
        if not ending:
            self.runner._ready = True
            async for next_event in self.runner(context, event):
                yield next_event
                received += 1
                if received >= self.count:
                    self.runner._ready = False
