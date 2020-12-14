from collections import OrderedDict
from textwrap import dedent

import asyncio

from m42pl.commands import StreamingCommand
from m42pl.pipeline import Pipeline
from m42pl.fields import Field


class Foreach(StreamingCommand):
    _about_     = 'Run the given pipeline(s) for each event.'
    _syntax_    = 'foreach <script>'
    _aliases_   = ['foreach', ]
    _grammar_   = OrderedDict(StreamingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        start : piperefs
    ''')

    class Transformer(StreamingCommand.Transformer):
        def start(self, items):
            return items, {}

    def __init__(self, pipelines: list):
        super().__init__()
        print(f'Foreach --> pipelines --> {pipelines}')
        self.pipelines = [ Field(f) for f in pipelines ]

    async def setup(self, event, pipeline):
        self.pipelines = [
            pipeline.context.pipelines[field.name]
            for field in self.pipelines
        ]

    async def target(self, event, pipeline):
        for _pipeline in self.pipelines:
            async for _event in _pipeline(event):
                pass

        # await asyncio.gather(*[
        #     _pipeline(event, pipeline)
        #     for _pipeline in self.pipelines
        # ])
        # sub_pipeline = pipeline.context.pipelines[self.pipeline_id]
        # sub_pipeline.set_chunk(self._chunk, self._chunks)
        # async for e in sub_pipeline(event):
        #     yield e
        yield event
