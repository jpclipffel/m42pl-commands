from textwrap import dedent
import asyncio
from aiohttp import web
import json

from collections import OrderedDict
from attr.setters import pipe

from m42pl.pipeline import InfiniteRunner, PipelineRunner
from m42pl.commands import GeneratingCommand
from m42pl.fields import Field, FieldsMap
from m42pl.event import Event


class HTTPServer(GeneratingCommand):
    """Simple HTTP server based on aiohttp.
    """

    _about_     = 'Runs an HTTP server'
    _syntax_    = (
        '''[[host=]{host}] [[port]={port}] (<pipeline> '''
        '''| with 'method' on 'path' as <pipeline>, ...)'''
    )
    _aliases_   = ['http_server', 'server_http']
    _schema_    = {
        'properties': {
            'request': {
                'type': 'object',
                'properties': {
                    'url': {'type': 'string', 'description': 'Requested URL'},
                    'host': {'type': 'string', 'description': 'Server host'},
                    'path': {'type': 'string', 'description': 'Requested path'},
                    'scheme': {'type': 'string', 'description': 'Requested URL scheme'},
                    'jsdata': {'type': 'object', 'description': 'Request JSON data'},
                    'query_string': {'type': 'string', 'description': 'Requested URL query'},
                    'content_type': {'type': 'string', 'description': 'Request content type'},
                    'content_length': {'type': 'number', 'description': 'Request size'}
                }
            }
        },
        'additionalProperties': {
            'description': 'Response fields'
        }
    }

    _grammar_   = OrderedDict(GeneratingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        rule    : STRING "on" field "as" piperef
        rules   : "with" rule (","? rule)*
        start   : arguments? (piperef | rules)
    ''')

    class Transformer(GeneratingCommand.Transformer):

        def rule(self, items):
            return items[0][1:-1], items[1][1:-1], items[2]
        
        def rules(self, items):
            return items

        def start(self, items):
            args = []
            kwargs = {}
            # No argument is given
            if len(items) == 1:
                rulepos = 0
            # Some arguments are given
            elif len(items) > 1:
                args = items[0][0]
                kwargs = items[0][1]
                rulepos = 1
            # ---
            # Set of rules
            if isinstance(items[rulepos], list):
                kwargs['rules'] = items[rulepos]
            # Single rule
            else:
                kwargs['piperef'] = items[rulepos]
            # ---
            return args, kwargs

    async def create_handler(self, context, piperef):
        """Instanciates, setups and returns an AIOHTTP handler.

        :param context: Current context
        :param piperef: handler's pipeline
        """

        class Handler:
            """AIOHTTP handler.
            """

            def __init__(self, context, piperef):
                """
                :param context: Current context
                :param piperef: handler's pipeline
                """
                self.context = context
                self.runner = PipelineRunner(
                    context.pipelines[piperef]
                )

            async def __call__(self, request):
                """Handles an AIOHTTP request.

                :param request: AIOHTTP request
                """
                try:
                    jsdata = await request.json()
                except Exception as error:
                    jsdata = {}
                resp = []
                # ---
                # Process request in sub-pipeline (== handler's pipeline)
                async for next_event in self.runner(self.context, Event(data={
                    'request': {
                        'url': str(request.url),
                        'host': request.host,
                        'path': request.path,
                        'scheme': request.scheme,
                        'jsdata': jsdata,
                        'query_string': request.query_string,
                        'content_type': request.content_type,
                        'content_length': request.content_length
                    }})):
                    if next_event is not None:
                        resp.append(next_event['data'])
                # ---
                # Format and return response
                if len(resp) == 0:
                    return web.Response(text='{}')
                elif len(resp) == 1:
                    return web.Response(text=json.dumps(resp[0]))
                else:
                    return web.Response(text=json.dumps(resp))

        # Create and return handler
        return Handler(context, piperef)


    def __init__(self, host: str = 'localhost', port: int = 8080,
                    rules: list = [], piperef: str = None):
        """
        :param host: Server host; Defaults to ``localhost``
        :param port: Server port; Defaults to ``8080``
        :param rules: AIOHTTP routes rules;
            List of tuples as (method, path, pipeline);
            Mutually-exclusive with ``piperef``
        :param piperef: Default pipeline to run;
            Mutually-exclusive with ``rules``
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

    async def target(self, event, pipeline, context):
        # Read fields
        self.fields = await self.fields.read(event, pipeline, context)
        # ---
        # Setup routes
        routes = []
        # 1 - Create routes from rules
        if len(self.rules):
            for method, path, piperef in self.rules:
                routes.append(web.route(
                    method,
                    path, 
                    await self.create_handler(context, Field(piperef).name)
                ))
        # 2 - If no rules are given, use the default pipeline
        else:
            routes.append(web.route(
                '*',
                '/',
                await self.create_handler(context, self.piperef.name)
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
