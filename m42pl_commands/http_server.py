from textwrap import dedent
import asyncio
from aiohttp import web
import json

from collections import OrderedDict

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field
from m42pl.event import Event


class HTTPServer(GeneratingCommand):
    _about_     = 'Runs an HTTP server'
    _syntax_    = '[[host=]host] [port=[port]] <pipeline>'
    _aliases_   = ['http_server', ]
    _grammar_   = OrderedDict(GeneratingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        start : arguments ","? piperef
    ''')

    class Transformer(GeneratingCommand.Transformer):
        def start(self, items):
            args = items[0][0]
            kwargs = items[0][1]
            kwargs['pipeline'] = items[1][1:]
            return args, kwargs

    def __init__(self, host: str = '127.0.0.1', port: int = 8080,
                    pipeline: str = None):
        """
        :param host:        Server host
                            Defaults to local host (127.0.0.1)
        :param port:        Server port
                            Defaults to 8080
        :param pipeline:    Sub-pipeline ID
        """
        super().__init__(host, port, pipeline)
        self.host = Field(host, default=host)
        self.port = Field(port, default=port)
        self.sub_pipeline = Field(pipeline, default=pipeline)

    async def target(self, event, pipeline):

        async def handle(request):
            """Handle a single HTTP request.

            :param request:     HTTP request to handle
            """
            jsdata = await request.json()
            resp = []
            async for e in self.sub_pipeline(Event(data=jsdata)):
                resp.append(e.data)
            return web.Response(text=json.dumps(resp))

        # Get sub-pipeline reference
        self.sub_pipeline = pipeline.context.pipelines[self.sub_pipeline.name]
        # Setup AIOHTTP web app
        app = web.Application()
        app.add_routes([web.post('/', handle),])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', await self.port.read(event, pipeline))
        await site.start()
        # Run forever
        while True:
            await asyncio.sleep(3600)
