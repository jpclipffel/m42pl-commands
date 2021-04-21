from collections import OrderedDict
from textwrap import dedent
import msgpack

from m42pl.commands import StreamingCommand
from m42pl.fields import Field
from m42pl.event import Event


class MsgPack(StreamingCommand):
    """Base class for *msgpack* commands.
    """

    _syntax_    = '[<field>] [as <field>]'
    _grammar_   = OrderedDict(StreamingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        src_field   : field
        dst_field   : field
        start       : src_field? ("as" dst_field)?
    ''')

    class Transformer(StreamingCommand.Transformer):
        def src_field(self, items):
            return ('src_field', items[0])
        
        def dst_field(self, items):
            return ('dest_field', items[0])

        def start(self, items):
            return (), dict(items)


class Pack(MsgPack):
    _aliases_   = ['msgpack',]
    _about_     = 'Pack an event or and event field'

    def __init__(self, src_field: str = None, dest_field: str = 'packed'):
        """
        :param src_field:   Source field.
        :param dest_field:  Destination field.
        """
        super().__init__(src_field, dest_field)
        self.src_field  = src_field and Field(src_field, default='') or None
        self.dest_field = Field(dest_field, default='packed')

    async def target(self, event, pipeline):
        yield await self.dest_field.write(
            event,
            msgpack.packb(
                self.src_field and (await self.src_field.read(event, pipeline))
                or event.data
            )
        )


class Unpack(MsgPack):
    _aliases_   = ['msgunpack',]
    _about_     = 'Unpack an event field'

    def __init__(self, src_field: str = 'packed', dest_field: str = None):
        """
        :param src_field:   Source field
        :param dest_field:  Destination field
        """
        super().__init__(src_field, dest_field)
        self.src_field  = Field(src_field, default=bytes())
        self.dest_field = dest_field and Field(dest_field, default='unpacked') or None

    async def target(self, event, pipeline):
        unpacked = msgpack.unpackb(await self.src_field.read(event, pipeline))
        if self.dest_field:
            yield await self.dest_field.write(event, unpacked)
        elif isinstance(unpacked, dict):
            event.data = unpacked
            yield event
