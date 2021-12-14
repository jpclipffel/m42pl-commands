from __future__ import annotations

import zmq

from .__base__ import Consumer


class Pull(Consumer):
    """Receives ZMQ messages and yields events.
    """

    _aliases_   = ['zmq_pull',]
    _about_     = 'Pull events from ZMQ'
    _schema_    = {
        'properties': {
            'topic': {'type': 'string', 'description': 'ZMQ topic'},
            'chunk': {'type': 'array', 'description': 'Dispatcher chunk ID and chunks count'}
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup(self, event, pipeline, context):
        await super().setup(zmq.PULL, event, pipeline)
    
    async def target(self, event, pipeline, context):
        while True:
            try:
                yield await self.field.write(event, {
                    'frames': await self.socket.recv_multipart(),
                    'chunk': self.chunk
                })
            except Exception:
                raise
