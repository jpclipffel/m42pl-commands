from __future__ import annotations

import asyncio
from typing import Any
import aiohttp

from typing import Any

from m42pl.commands import StreamingCommand
from m42pl.fields import Field, FieldsMap
import m42pl


class WSBroadcaster(StreamingCommand):
    """Broadcast events to websockets.
    """

    _about_     = 'Broadcast events to websocket clients'
    _syntax_    = '[[path]={path}] [[encoder=]<encoder name>] [[host=]<ip/hostname>] [[port=]<port>]'
    _aliases_   = ['ws_bcast', 'ws_broadcast']

    def __init__(self, path: str = 'path', encoder: str = 'encoder',
                    host: str = 'host', port: str|int = 'port'):
        """
        :param path:    Event's field name indicating on which path the
                        event should be broadcasted
        :param encoder: Encoder name
        :param host:    Websocket server host
        :param port:    Websocket server port
        """
        super().__init__(path)
        self.path = Field(path, default='/')
        self.fields = FieldsMap(**{
            'encoder': Field(encoder, default='json'),
            'host': Field(host, default='127.0.0.1'),
            'port': Field(port, default=8888)
        })
        self.paths: dict[str, Any] = {}

    async def setup(self, event, pipeline):

        async def websocket_handler(request: Any):
            """Handles an http client.

            :param request:     Connection request
            """
            self.logger.info(f'new connection: remote="{request.remote}", url="{request.url}"')
            # Setup websocket instance
            self.logger.info(f'setup websocket: remote="{request.remote}", url="{request.url}"')
            ws = aiohttp.web.WebSocketResponse()
            await ws.prepare(request)
            # Extract client's path to emulate the subscription mechanism
            # and add clients to subscriber list
            path = request.path.strip('/')
            self.logger.info(f'remote subscription: path="{path}", remote="{request.remote}", url="{request.url}"')
            if not path in self.paths:
                self.paths[path] = [ws,]
            else:
                self.paths[path].append(ws)
            # Wait for the client to close.
            # In the meantime, the calling loop will continuously send
            # events as they arrive. 
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close':
                        self.logger.info(f'closing websocket: remote="{request.remote}", url="{request.url}"')
                        await ws.close()
            # Remove client
            self.logger.info(f'removing websocket: remote="{request.remote}", url="{request.url}"')
            self.paths[path].remove(ws)
            return ws

        # Process fields
        self.fields = await self.fields.read(event, pipeline)
        # Setup encoder
        self.encoder = m42pl.encoder(self.fields.encoder)()
        # Setup aiohttp app
        self.app = aiohttp.web.Application()
        # Setup catch-all route
        # Clients can 'subscribe' to specific event using a path.
        self.app.add_routes([
            aiohttp.web.get('/{tail:.*}', websocket_handler),
        ])
        # Setup and start aiohttp runner
        runner = aiohttp.web.AppRunner(self.app)
        await runner.setup()
        site = aiohttp.web.TCPSite(
            runner,
            self.fields.host,
            self.fields.port,
            reuse_port=True
        )
        await site.start()

    async def target(self, event, pipeline):
        # Get event path
        path = (await self.path.read(event, pipeline)).strip('/')
        # Encode event once for all clients before broadcast
        encoded = self.encoder.encode(event)
        # Notify clients subscribed to the event's path
        tasks = [
            ws.send_str(encoded) for ws in self.paths.get(path, [])
        ]
        if len(tasks) > 0:
            await asyncio.wait(tasks)
        # Done
        yield event
