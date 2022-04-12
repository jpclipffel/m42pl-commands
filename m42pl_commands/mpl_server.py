from email.policy import default
import json
import asyncio
from aiohttp import web

from m42pl.commands import GeneratingCommand, StreamingCommand
from m42pl.fields import Field, FieldsMap
from m42pl.event import Event, derive
import m42pl


class MPLServerApi(GeneratingCommand):
    """API server to run M42PL pipelines.
    """

    _about_     = 'M42PL server (API)'
    _syntax_    = '[[host=]<hostname>] [[port=]<port>]'
    _aliases_   = ['mpl-server', 'mpl-serve']
    _schema_    = {}


    class Handler:
        def __init__(self, kvstore, dispatcher):
            self.kvstore = kvstore
            self.dispatcher = dispatcher


    class Dispatch(Handler):
        """Runs a new pipeline.
        """
        async def __call__(self, request):
            jsdata = await request.json()
            identifier = self.dispatcher(
                source=jsdata['source'],
                kvstore=self.kvstore,
                event=Event(jsdata['event'])
            )
            return web.Response(text=json.dumps({'identifier': identifier}))


    class Status(Handler):
        """Returns pipeline(s) staus.
        """
        async def __call__(self, request):
            return web.Response(text=json.dumps({
                'method': 'status',
                'identifier': request.match_info.get('identifier')
            }))


    def __init__(self, host: str = 'host', port: int|str = 'port',
                    kvstore: str = 'kvstore.name', dispatcher: str='dispatcher.name',
                    kvstore_kwargs: str = 'kvstore.kwargs', dispatcher_kwargs: str = 'dispatcher.kwargs'):
        """
        :param host: Server host; Defaults to ``localhost``
        :param port: Server port; Defaults to ``8080``
        :param kvstore: Server KVStore name; Defaults to ``redis``
        :param dispatcher: Server dispatcher; Defaults to ``local_detached``
        :param kvstore_kwargs: KVStore configuration
        :param dispatcher_kwargs: Dispatcher configuration
        """
        super().__init__(host, port)
        self.fields = FieldsMap(**{
            'host': Field(host, default='localhost'),
            'port': Field(port, default=4242),
            'kvstore': Field(kvstore, default='redis'),
            'dispatcher': Field(dispatcher, default='local_detached'),
            'kvstore_kwargs': Field(kvstore_kwargs, default={}),
            'dispatcher_kwargs': Field(dispatcher_kwargs, default={}),
        })

    async def target(self, event, pipeline, context):
        # Read fields
        self.fields = await self.fields.read(event, pipeline, context)
        # Initialize KVStore and dispatcher
        self.logger.info('Initializing kvstore')
        self.kvstore = m42pl.kvstore(self.fields.kvstore)(**self.fields.kvstore_kwargs)
        self.logger.info('Initializing dispatcher')
        self.dispatcher = m42pl.dispatcher(self.fields.dispatcher)(**self.fields.dispatcher_kwargs)
        # Setup routes
        routes = []
        for handler, method, path in [
            (self.Dispatch, 'POST', '/dispatch'),
            (self.Status, 'GET', '/status'),
            (self.Status, 'GET', '/status/{identifier}'),
        ]:
            routes.append(web.route(
                method,
                path,
                handler(self.kvstore, self.dispatcher)
            ))
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



class MPLDispatcher(StreamingCommand):
    """Dispatchs (runs) a M42PL pipeline.
    """

    _about_     = 'M42PL dispatcher'
    _syntax_    = '[source=]{pipeline source} [event=]{initial event}'
    _aliases_   = ['mpl-dispatcher', 'mpl-dispatch']
    _schema_    = {}

    def __init__(self, source: str = 'source', event: str = 'event',
                    kvstore: str = 'kvstore.name', dispatcher: str='dispatcher.name',
                    kvstore_kwargs: str = 'kvstore.kwargs', dispatcher_kwargs: str = 'dispatcher.kwargs'):
        """
        :param source: Pipeline source
        :param event: Pipeline initial event
        :param kvstore: Server KVStore name; Defaults to ``redis``
        :param dispatcher: Server dispatcher; Defaults to ``local_detached``
        :param kvstore_kwargs: KVStore configuration
        :param dispatcher_kwargs: Dispatcher configuration
        """
        super().__init__(source, event, kvstore, dispatcher, kvstore_kwargs, dispatcher_kwargs)
        self.source = Field(source)
        self.event = Field(event)
        self.fields = FieldsMap(**{
            'kvstore': Field(kvstore, default='redis'),
            'dispatcher': Field(dispatcher, default='local_detached'),
            'kvstore_kwargs': Field(kvstore_kwargs, default={}),
            'dispatcher_kwargs': Field(dispatcher_kwargs, default={}),
        })

    async def setup(self, event, pipeline, context):
        # Read fields
        self.fields = await self.fields.read(event, pipeline, context)
        # Initialize KVStore and dispatcher
        self.logger.info('Initializing kvstore')
        self.kvstore = m42pl.kvstore(self.fields.kvstore)(**self.fields.kvstore_kwargs)
        self.logger.info('Initializing dispatcher')
        self.dispatcher = m42pl.dispatcher(self.fields.dispatcher)(**self.fields.dispatcher_kwargs)

    async def target(self, event, pipeline, context):
        identifier = self.dispatcher(
            source=await self.source.read(event, pipeline, context),
            kvstore=self.kvstore,
            event=Event(await self.event.read(event, pipeline, context) or event)
        )
        yield derive(event, {'identifier': identifier})
