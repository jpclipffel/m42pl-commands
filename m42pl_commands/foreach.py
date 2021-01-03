from collections import OrderedDict
from textwrap import dedent

from m42pl.commands import StreamingCommand
from m42pl.pipeline import Pipeline
from m42pl.fields import Field


class Foreach(StreamingCommand):
    _about_     = 'Run the given pipeline for each event'
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
        self.pipeline = pipeline.context.pipelines[self.pipeline.name]

    async def target(self, event, pipeline):
        async for _event in self.pipeline(event):
            yield _event
