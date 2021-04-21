from asyncio import sleep
import zmq

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field

from .__base__ import Base


class Subscribe(Base, GeneratingCommand):
    _aliases_   = ['zmq_sub', 'zmq_subscribe']
    _syntax_    = '[url=]<url> [[topic=]{topic}]'
    _about_     = 'Receives events from a ZMQ queue and topic'

    def __init__(self, url: str = 'tcp://127.0.0.1:5555', topic: str = 'default', field: str = 'zmq'):
        super().__init__(url, topic, zmq)
        self.url = Field(url, default='tcp://127.0.0.1:5555')
        self.topic = Field(topic, default='default')
        self.field = Field(field, default='zmq')

    async def setup(self, event, pipeline):
        # Common setup
        await super().setup(event, pipeline)
        # Create socket
        self.socket = self.context.socket(zmq.SUB) # pylint: disable=no-member
        # Connect socket
        self.socket.connect(await self.url.read(event, pipeline))
        self.socket.setsockopt_string(
            zmq.SUBSCRIBE, # pylint: disable=no-member
            await self.topic.read(event, pipeline)
        )
    
    async def target(self, event, pipeline):
        while True:
            try:
                topic, data = await self.socket.recv_multipart()
                yield await self.field.write(event.derive(), {
                    'topic': topic,
                    'data': data
                })
            except Exception:
                pass
