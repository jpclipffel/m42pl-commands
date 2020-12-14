from collections import OrderedDict
from textwrap import dedent
from lxml import etree

from m42pl.event import Event
from m42pl.commands import StreamingCommand
from m42pl.fields import Field, BaseField


class XPath(StreamingCommand):
    _about_     = 'Evaluate XPath expressions and assign results to fields'
    _syntax_    = '<[expression=]expression> <[field=]source field> [[dest=]dest field]'
    _aliases_   = ['xpath', ]

    def __init__(self, expression: str, src: str, dest: str):
        super().__init__(expression, src, dest)
        # Initialize fields
        self.xpath = Field(expression)
        self.src = Field(src)
        self.dest = Field(dest)
        # Initialize parser
        self.parser = etree.HTMLParser()

    async def setup(self, event, pipeline):
        self.xpath = etree.XPath(await self.xpath.read(event, pipeline))

    async def target(self, event, pipeline):
        tree = etree.fromstring(await self.src.read(event, pipeline), parser=self.parser)
        matches = self.xpath(tree)
        if matches:
            event = await self.dest.write(event, matches)
        # for element in matches:
        #     if isinstance(element, etree._ElementUnicodeResult):
        #         self.dest.write(event.data, )
        #         yield Event(data={
        #             'xpath': element
        #         })
            # print(type(m), m, m.attrib)
        yield event
