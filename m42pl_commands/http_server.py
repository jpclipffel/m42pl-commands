from textwrap import dedent
import asyncio
from aiohttp import web
import json

from collections import OrderedDict

from m42pl.pipeline import InfiniteRunner
from m42pl.commands import GeneratingCommand
from m42pl.fields import Field, FieldsMap
from m42pl.event import Event


class HTTPServer(GeneratingCommand):
    """Simple HTTP server based on aiohttp.
    """

    _about_     = 'Runs an HTTP server'
    _syntax_    = (
        '''[[host=]host] [port=[port]] <pipeline> '''
        '''| with 'method' on 'path' = <pipeline>, ...'''
    )
    _aliases_   = ['http_server', ]
    _grammar_   = OrderedDict(GeneratingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        rule    : STRING "on" field "=" piperef
        rules   : "with" rule (","? rule)*
        start   : arguments (piperef | rules)
    ''')

    class Transformer(GeneratingCommand.Transformer):

        def rule(self, items):
            return items[0][1:-1], items[1][1:-1], items[2]
        
        def rules(self, items):
            return items

        def start(self, items):
            args = items[0][0]
            kwargs = items[0][1]
            if isinstance(items[1], list):
                kwargs['rules'] = items[1]
            else:
                kwargs['piperef'] = items[1][1:]
            return args, kwargs

    async def create_handler(self, pipeline, piperef):
        """Returns an AIOHTTP handler from a function template.

        :param pipeline:    Current pipeline
        :param piperef:     Handler's pipeline reference
                            (pipeline to run when handler is called)
        """

        # async def handler(request):
        #     """Handles an AIOHTTP request (function template).

        #     :param request: AIOHTTP request
        #     """
        #     try:
        #         jsdata = await request.json()
        #     except Exception:
        #         jsdata = {}
        #     resp = []
        #     async for event in pipeline.context.pipelines[piperef](
        #         pipeline.context,
        #         Event(data=jsdata)
        #     ):
        #         resp.append(event.data)
        #     return web.Response(text=json.dumps(resp))

        class Handler:
            def __init__(self, runner):
                self.runner = runner

            async def __call__(self, request):
                try:
                    jsdata = await request.json()
                except Exception:
                    jsdata = {}
                resp = []
                async for next_event in self.runner(Event(data=jsdata)):
                    resp.append(next_event.data)
                return web.Response(text=json.dumps(resp))

        runner = InfiniteRunner(
            pipeline.context.pipelines[piperef],
            pipeline.context,
            Event()
        )
        await runner.setup()

        # return handler
        return Handler(runner)


    def __init__(self, host: str = 'localhost', port: int = 8080,
                    rules: list = [], piperef: str = None):
        """
        :param host:        Server host
                            Defaults to local host (localhost)
        :param port:        Server port
                            Defaults to 8080
        :param rules:       AIOHTTP routes rules
                            List of tuples as (method, path, pipeline)
                            Mutually-exclusive with :param:`piperef`
        :param piperef:     Default pipeline to run
                            Mutually-exclusive with :param:`rules`
        """
        super().__init__(host, port, rules, piperef)
        # Base arguments
        self.fields = FieldsMap(**{
            'host': Field(host, default=host),
            'port': Field(port, default=port)
        })
        # Rules
        self.rules = rules
        # Default pipeline reference
        self.piperef = Field(piperef, default=piperef)

    async def target(self, event, pipeline):        # Read fields
        self.fields = await self.fields.read(event, pipeline)
        # ---
        # Setup routes
        routes = []
        # 1 - Create routes from rules
        if len(self.rules):
            for method, path, piperef in self.rules:
                routes.append(web.route(
                    method,
                    path, 
                    await self.create_handler(pipeline, Field(piperef).name)
                ))
        # 2 - If no rules are given, use the default pipeline
        else:
            routes.append(web.route(
                '*',
                '/',
                await self.create_handler(pipeline, self.piperef.name)
            ))
        # ---
        # Create and setup AIOHTTP app, runner and site
        app = web.Application()
        app.add_routes(routes)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(
            runner,
            self.fields.host,
            self.fields.port,
            reuse_port=True
        )
        await site.start()
        # Run forever
        while True:
            await asyncio.sleep(3600)
        # Mark method as a async generator
        yield
        return
