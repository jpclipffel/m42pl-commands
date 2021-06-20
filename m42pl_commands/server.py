import asyncio
from asyncio.protocols import DatagramProtocol

from collections import OrderedDict
from textwrap import dedent

from m42pl.commands import GeneratingCommand
from m42pl.pipeline import InfiniteRunner
from m42pl.fields import Field, FieldsMap
from m42pl.event import Event


class UDP(DatagramProtocol):

    def __init__(self, runner):
        super().__init__()
        self.runner = runner

    async def run(self, data, addr):
        async for _ in self.runner(event=Event({
            'data': data,
            'addr': addr
        })):
            pass

    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        loop = asyncio.get_running_loop()
        loop.create_task(self.run(data, addr))


class UDPServer(GeneratingCommand):
    _about_     = 'Runs a socket server'
    _syntax_    = '[[protocol=]<tcp|udp>] [[host=]{server address}] [[port=]{server port}] [...]'
    _aliases_   = ['server',]

    _grammar_   = OrderedDict(GeneratingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        start   : arguments? piperef
    ''')

    class Transformer(GeneratingCommand.Transformer):
        def start(self, items):
            print(f'start --> {items}')
            args = []
            kwargs = {}
            # No arguments
            if len(items) == 1:
                kwargs['piperef'] = items[0]
            # Some arguments
            else:
                args = items[0][0]
                kwargs = items[0][1]
                kwargs['piperef'] = items[1]
            # ---
            print(f'start --> {args}, {kwargs}')
            return args, kwargs

    def __init__(self, protocol: str = 'tcp', host: str = '127.0.0.1', port: int = 9000, piperef: str = None):
        super().__init__(protocol, host, port, piperef)
        self.fields = FieldsMap(**{
            'protocol': Field(protocol, default='tcp'),
            'host': Field(host, default='127.0.0.1'),
            'port': Field(port, default=9000)
        })
        self.piperef = Field(piperef)

    async def target(self, event, pipeline):

        runner = InfiniteRunner(
            pipeline.context.pipelines[self.piperef.name],
            pipeline.context,
            Event()
        )
        await runner.setup()

        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDP(runner),
            local_addr=('127.0.0.1', 9999))
        try:
            await asyncio.sleep(3600)  # Serve for 1 hour.
        finally:
            transport.close()
        yield None