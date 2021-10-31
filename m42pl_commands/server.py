import asyncio
from asyncio import transports
from asyncio import protocols
from asyncio.protocols import DatagramProtocol

from collections import OrderedDict
from textwrap import dedent

from m42pl.commands import GeneratingCommand
from m42pl.pipeline import InfiniteRunner
from m42pl.fields import Field, FieldsMap
from m42pl.event import Event, derive


class UDPProtocol(DatagramProtocol):
    """UDP protocol handler.
    """

    @classmethod
    async def get_transport(cls, queue, fields):
        """Returns a 'transport' instance to be used by the `server` command.
        """
        transport, protocol = await asyncio.get_running_loop().create_datagram_endpoint(
            lambda: cls(queue),
            local_addr=(fields.host, fields.port)
        )
        return transport

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        asyncio.get_running_loop().create_task(
            self.queue.put((data, addr))
        )


class TCPProtocol(asyncio.Protocol):
    """TCP protocol handler.
    """

    @classmethod
    async def get_transport(cls, queue, fields):
        """Returns a 'transport' instance to be used by the `server` command.
        """
        return await asyncio.get_running_loop().create_server(
            lambda: cls(queue),
            fields.host,
            fields.port,
            start_serving=True
        )

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        asyncio.get_running_loop().create_task(
            self.queue.put((data, (None, None)))
        )


class Server(GeneratingCommand):
    """Receives data on a given protocol, host IP and port.

    The current implementation support two protocols:
    * tcp
    * udp

    To add support for another protocol, write a new `Protocol` class
    which will implements the `get_transport` static method.
    """

    _about_     = 'Receives data on a given protocol, host IP and port'
    _aliases_   = ['server', 'serve', 'listen']
    _syntax_    = '[[protocol=]<tcp|udp>] [[host=]<ip>] [[port=]<port>]'
    _schema_    = {
        'properties': {
            'msg': {
                'type': 'object',
                'properties': {
                    'data': { 'description': 'received data' },
                    'host': { 'description': 'client host' },
                    'port': { 'description': 'client port' }
                }
            }
        }
    }

    # Protocol name/class mapping
    protocols = {
        'udp': UDPProtocol,
        'tcp': TCPProtocol
    }

    def __init__(self, protocol: str = 'tcp', host: str = 'host', port: str = 'port'):
        """
        :param protocol:    Protocol to use, defaults to TCP
        :param host:        Host IP to bind, default to localhost / 127.0.0.1
        :param port:        Host port to bind, default to 9999
        """
        self.fields = FieldsMap(**{
            'protocol': Field(protocol, default=protocol),
            'host': Field(host, default='127.0.0.1'),
            'port': Field(port, default=9999)
        })

    async def target(self, event, pipeline):
        fields = await self.fields.read(event, pipeline)
        # Shared queue to receive and forwards data to pipeline
        queue = asyncio.Queue(1)
        # Get new transport instance
        protocol = self.protocols.get(fields.protocol.lower())
        if not protocol:
            raise Exception(
                f'Protocol "{fields.protocol}" is unknown, '
                f'please use one of {", ".join(self.protocols.keys())}'
            )
        self.transport = await protocol.get_transport(queue, fields)
        # Run forever
        self.logger.info(
            f'start listening on '
            f'{fields.protocol.lower()}/{fields.host}:{fields.port}'
        )
        while True:
            data, hostport = await queue.get()
            yield derive(event, data={
                'msg': {
                    'data': data,
                    'host': hostport[0],
                    'port': hostport[1]
                }
            })

    async def __aexit__(self, *args, **kwargs):
        try:
            self.transport.close()
        except Exception:
            pass
