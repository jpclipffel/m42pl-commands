from sys import maxsize
import jsonpath_ng
import json

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class JSONPath(StreamingCommand):
    _about_     = 'Evaluate an JSONPath expression'
    _syntax_    = '<[expression=]expression> <[field=]source field> [[dest=]dest field]'
    _aliases_   = ['jsonpath', 'jspath']

    def __init__(self, expression: str, src: str = None, dest: str = 'jsonpath'):
        """
        :param expression:  JSONPath epxression
        :param src:         Source field
        :param dest:        Destination field
        """
        super().__init__(expression, src, dest)
        # Initialize fields
        self.jspath = Field(expression, default=expression)
        self.src = Field(src, default=src)
        self.dest = Field(dest, default=dest)

    async def setup(self, event, pipeline):
        self.jspath = jsonpath_ng.parse(
            await self.jspath.read(event, pipeline)
        )

    async def target(self, event, pipeline):
        matched = []
        # Read source field
        field = await self.src.read(event, pipeline)
        # Match JSONPath
        if not field:
            matched = self.jspath.find(event.data)
        elif isinstance(field, dict):
            matched = self.jspath.find(field)
        elif isinstance(field, str):
            matched = self.jspath.find(json.load(field))
        # Write matched items
        if len(matched) == 1:
            yield await self.dest.write(event, matched[0].value)
        elif len(matched) > 1:
            yield await self.dest.write(event, [
                match.value 
                for match
                in matched
            ])
        else:
            yield event
