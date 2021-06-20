from __future__ import annotations

import zmq

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field

from .__base__ import Consumer


class Subscribe(Consumer):
    """Receives ZMQ messages and yields events.
    """

    _aliases_   = ['zmq_sub', 'zmq_subscribe']
    _about_     = 'Subscribe and receive messages from a ZMQ socket'

    def __init__(self, topic: str|list = [], *args, **kwargs):
        super().__init__(*args, topic=topic, **kwargs)
        # NB: In PUB/SUB, the client socket must subscribe at least to an
        # empty topic (''), meaning it will receive all messages (no filter).
        self.args.update(**{
            'topic': Field(topic, default=['', ], seqn=True)
        })

    async def setup(self, event, pipeline):
        await super().setup(zmq.SUB, event, pipeline)
        # Configure topic (envelope filtering)
        self.logger.info(f'registering topics: {self.args.topic}')
        for topic in self.args.topic:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
    
    async def target(self, event, pipeline):
        while True:
            try:
                frames = await self.socket.recv_multipart()
                # Try to decode topic as string
                try:
                    topic = frames[0].decode()
                except Exception:
                    topic = frames[0]
                # Done
                yield await self.field.write(event, {
                    'topic': topic,
                    'frames': frames[1:]
                })
                # Done
                # yield {
                #     'topic': topic,
                #     'frames': frames[1:]
                # }
            except Exception:
                raise
