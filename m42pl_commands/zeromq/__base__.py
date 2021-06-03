from __future__ import annotations

import zmq
import zmq.asyncio
from asyncio import sleep

import m42pl
from m42pl.commands import StreamingCommand, GeneratingCommand, MergingCommand
from m42pl.fields import Field, FieldsMap


class Base:
    """Generic ZMQ class.
    """

    _syntax_ = (
        '[[url=]<url>] [[code=]<codec>] '
        '[[field=]{field}|({field}, ...)]'
    )

    def __init__(self, url: str = 'tcp://127.0.0.1:5555',
                    codec: str = 'msgpack', **kwargs):
        """
        :param url:     ZMQ url (including protocol, address and port)
        :param codec:   Encoder name (defaults to 'msgpack')
        """
        self.args = FieldsMap(**{
            'url': Field(url, default='tcp://127.0.0.1:5555'),
            'codec': Field(codec, default='msgpack'),
        })


class Producer(StreamingCommand, MergingCommand):
    """Generic ZMQ producer.

    This class cannot be used as-is and must be inherited to implement
    a pub(lisher) or a push(er) class.
    """

    def __init__(self, field: str|list = [], *args, **kwargs):
        """
        :param url:     ZMQ URL as ``<protocol>://host:port``
        :param codec:   Encoder name; Defaults to ``msgpack``
        :param field:   Field(s) to send; Defaults to an empty list,
                        meaning the full event will be sent.
        """
        for parent in [Base, StreamingCommand, MergingCommand]:
            parent.__init__(self, *args, field=field, **kwargs)
        self.fields = Field(field, default=[], seqn=True)

    async def setup(self, sock_type, event, pipeline):
        """Setup the instance.

        This parent method has to be called by the child first.

        :param sock_type:   ZMQ socket type.
        """
        # Publishers does not support parallel processing (yet ?)
        # TODO: Check for SOCK_REUSE_PORT with ZMQ
        if not self.first_chunk:
            return
        # ---
        self.args = await self.args.read(event, pipeline)
        self.encoder = m42pl.encoder(self.args.codec)()
        self.context = zmq.asyncio.Context.instance()
        # Create and bind socket
        self.socket = self.context.socket(sock_type)
        self.socket.bind(self.args.url)
        await sleep(0.25)

    def encode(self, data):
        """Encode the given :param:`data`.

        Data is encoded only if it's not a string or a byte array.
        Encoding is done using the class' encoder (defaults to msgpack).

        :param data:    Data to encode, typically a frame content.
        """
        if not isinstance(data, (str, bytes)):
            return self.encoder.encode(data)
        return data

    async def __aexit__(self, *args, **kwargs) -> None:
        """Teardown ZMQ.
        """
        if self.first_chunk:
            self.socket.close() # type: ignore
            self.context.destroy()


class Consumer(Base, GeneratingCommand):
    """Generic ZMQ consumer.

    This class cannot be used as-is and must be inherited to implement
    a sub(scriber) or a pull(er) class.
    """

    def __init__(self, field: str = 'zmq', *args, **kwargs):
        for parent in [Base, GeneratingCommand, MergingCommand]:
            parent.__init__(self, *args, field=field, **kwargs)
        self.field = Field(field, default='zmq')

    async def setup(self, sock_type, event, pipeline):
        """Setup the instance.

        This parent method has to be called by the child first.

        :param sock_type:   ZMQ socket type.
        """
        self.args = await self.args.read(event, pipeline)
        self.encoder = m42pl.encoder(self.args.codec)()
        self.context = zmq.asyncio.Context.instance()
        # Create and connect socket
        self.socket = self.context.socket(sock_type)
        self.socket.connect(self.args.url)

    async def __aexit__(self, *args, **kwargs) -> None:
        """Teardown ZMQ.
        """
        self.socket.close() # type: ignore
        self.context.destroy()
