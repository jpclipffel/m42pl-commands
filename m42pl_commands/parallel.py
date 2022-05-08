from collections import OrderedDict
from textwrap import dedent
import asyncio

from m42pl.commands import StreamingCommand
from m42pl.pipeline import InfiniteRunner
from m42pl.fields import Field
from m42pl.event import derive


class Parallel(StreamingCommand):
    """Runs multiple sub-pipelines using `asyncio`.
    """

    _about_     = 'Run multiple sub-pipelines'
    _syntax_    = '<pipeline> [, ...]'
    _aliases_   = ['parallel', 'tee', ]
    _schema_    = {'properties': {}}
    _grammar_   = OrderedDict(StreamingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        start : piperef (","? piperef)*
    ''')

    class Transformer(StreamingCommand.Transformer):
        def start(self, items):
            return (), {'pipelines': items}

    def __init__(self, pipelines: list):
        """
        :param pipelines:   Pipelines ID
        """
        super().__init__(pipelines)
        self.runners = []
        self.pipelines = Field(pipelines)

    async def setup(self, event, pipeline, context):
        for piperef in self.pipelines.name:
            # Add new pipeline runner
            self.runners.append(InfiniteRunner(
                context.pipelines[piperef.name],
                context,
                event
            ))
            # Setup latest added runner
            await self.runners[-1].setup()

    async def target(self, event, pipeline, context):

        async def drain(runner):
            """Runs a pipeline 'runner' (...).
            """
            async for item in runner(derive(event)):
                await queue.put(item)

        queue = asyncio.Queue(1)
        tasks = [
            asyncio.create_task(drain(runner))
            for runner
            in self.runners
        ]
        while not all(task.done() for task in tasks):
            yield await queue.get()
