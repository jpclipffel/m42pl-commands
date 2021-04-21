from collections import OrderedDict
from textwrap import dedent

from asyncio import sleep

from m42pl.commands import StreamingCommand
from m42pl.pipeline import Pipeline, InfiniteRunner
from m42pl.fields import Field, pipe


class Foreach(StreamingCommand):
    """Runs a sub-pipeline for each received event.

    This commands shows two unusual behaviours:

    * It hijacks its parent :class:`StreamingCommand.__call__` method
      and let the sub-pipeline handle its own termination
    * It iterates over the sub-pipeline in *infinite* mode
    """

    _about_     = 'Run a sub-pipeline for each event'
    _syntax_    = '<pipeline>'
    _aliases_   = ['foreach',]
    
    _grammar_   = OrderedDict(StreamingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        start : piperef
    ''')

    class Transformer(StreamingCommand.Transformer):
        def start(self, items):
            return items, {}

    def __init__(self, pipeline: str):
        """
        :param pipeline:    Pipeline ID
        """
        super().__init__(pipeline)
        self.pipeline = Field(pipeline)

    async def setup(self, event, pipeline):
        # self.pipeline = pipeline.context.pipelines[self.pipeline.name](pipeline.context, event, infinite=True)
        # await self.pipeline.__anext__()
        self.runner = InfiniteRunner(
            pipeline.context.pipelines[self.pipeline.name],
            pipeline.context,
            event
        )
        await self.runner.setup()

    async def target(self, event, pipeline):
        # try:
        #     next_event = await self.pipeline.asend(event)
        #     while next_event:
        #         yield next_event
        #         next_event = await self.pipeline.asend(None)
        # except StopAsyncIteration:
        #     yield
        async for next_event in self.runner(event):
            yield next_event

    async def __call__(self, event, pipeline, *args, **kwargs):
        async for next_event in self.target(event, pipeline):
            yield next_event
