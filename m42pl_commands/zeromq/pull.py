from __future__ import annotations

import zmq

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field

from .__base__ import Consumer


class Pull(Consumer):
    """Receives ZMQ messages and yields events.
    """

    _aliases_   = ['zmq_pull',]
    _about_     = 'Pull events from a ZMQ socket'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup(self, event, pipeline):
        await super().setup(zmq.PULL, event, pipeline)
    
    async def target(self, event, pipeline):
        while True:
            try:
                yield await self.field.write(event, {
                    'frames': await self.socket.recv_multipart(),
                    'chunk': self.chunk
                })
            except Exception:
                raise
