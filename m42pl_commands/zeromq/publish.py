from asyncio import sleep
import zmq

from m42pl.commands import StreamingCommand
from m42pl.fields import Field
from m42pl.utils import formatters

from .__base__ import Base


class Publish(Base, StreamingCommand):
    _aliases_   = ['zmq_pub', 'zmq_publish']
    _syntax_    = '[url=]<url> [[topic=]{topic}] [[field=]<field>]'
    _about_     = 'Publish events to a ZMQ queue and topic'

    def __init__(self, url: str = 'tcp://127.0.0.1:5555',
                    topic: str = 'default', field: str = None):
        """
        :param url:     ZMQ URL
        :param topic:   ZMQ topic
        :param field:   Optional field selector
        """
        super().__init__(url, topic, field)
        self.url = Field(url, default='tcp://127.0.0.1:5555')
        self.topic = Field(topic, default='default')
        self.field = field and Field(field, default={}) or None
        self.formatter = formatters.Json()

    async def setup(self, event, pipeline):
        # Common setup
        await super().setup(event, pipeline)
        # Create socket
        self.socket = self.context.socket(zmq.PUB) # pylint: disable=no-member
        # Bind socket
        self.socket.bind(await self.url.read(event, pipeline))
        await sleep(1)

    async def get_payload(self, event, pipeline) -> bytes:
        if self.field:
            return str(await self.field.read(event, pipeline)).encode()
        return self.formatter(event).encode()

    async def target(self, event, pipeline):
        await self.socket.send_multipart([
            (await self.topic.read(event, pipeline)).encode(),
            await self.get_payload(event, pipeline)
        ])
        yield event
