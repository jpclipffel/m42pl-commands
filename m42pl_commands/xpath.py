from lxml import etree

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class XPath(StreamingCommand):
    """Evaluates an XPath expression.
    """

    _about_     = 'Evaluate an XPath expression'
    _syntax_    = '<[expression=]expression> <[field=]source field> [[dest=]dest field]'
    _aliases_   = ['xpath', ]
    _schema_    = {
        'properties': {
            '{dest}': {'description': 'XPath results'}
        }
    }

    def __init__(self, expression: str, src: str, dest: str):
        """
        :param expression: XPath epxression
        :param src: Source field
        :param dest: Destination field
        """
        super().__init__(expression, src, dest)
        # Initialize fields
        self.xpath = Field(expression)
        self.src = Field(src)
        self.dest = Field(dest)
        # Initialize parser
        self.parser = etree.HTMLParser()

    async def setup(self, event, pipeline, context):
        self.xpath = etree.XPath(await self.xpath.read(event, pipeline, context))

    async def target(self, event, pipeline, context):
        # Parse
        tree = etree.fromstring(
            await self.src.read(event, pipeline, context),
            parser=self.parser
        )
        # Process matched items
        # Note: LXML's XPath may returns different object types:
        # - Standard types (bool, int, flot, str)
        # - Complex types (nodes)
        # Reference: https://lxml.de/xpathxslt.html#xpath-return-values
        matched = []
        for match in self.xpath(tree, smart_strings=False):
            # Literals
            if isinstance(match, (bool, int, float, str)):
                matched.append(match)
            # Elements
            else:
                matched.append({
                    'attrib': dict(match.attrib),
                    'text': match.text
                })
        # Done
        yield await self.dest.write(event, matched)
