from __future__ import annotations

from typing import List

import zmq

from m42pl.fields import Field
from .__base__ import Producer


class Publish(Producer):
    """Publishes event or event field to a ZMQ queue.

    If no field(s) is/are given, the full event's data will be encoded
    as a single frame using the given encoder (defaults to `msgpack`).
    Otherwise, each field will be encoded and send as a frame.
    """

    _aliases_   = ['zmq_pub', 'zmq_publish']
    _about_     = 'Publish events or events field(s) to ZMQ'

    def __init__(self, topic: str = None, *args, **kwargs):
        super().__init__(*args, topic=topic, **kwargs)
        self.args.update(**{
            'topic': Field(topic, default=b'')
        })

    async def setup(self, event, pipeline, context):
        await super().setup(zmq.PUB, event, pipeline)
        # Encode topic
        if not isinstance(self.args.topic, bytes):
            try:
                self.args.topic = self.args.topic.encode()
            except Exception:
                pass

    async def build_frames(self, event, pipeline) -> List[str|bytes]:
        """Returns a list of frames to be sent through ZMQ.
        """
        frames = []
        fields = await self.fields.read(event, pipeline, context)
        if self.args.topic:
            frames.append(self.args.topic)
        if len(fields) > 0:
            for field in fields:
                frames.append(self.encode(field))
        else:
            frames.append(self.encode(event['data']))
        return frames

    async def target(self, event, pipeline, context):
        """Sends data through ZMQ.
        """
        if self.first_chunk:
            await self.socket.send_multipart(
                await self.build_frames(event, pipeline)
            )
        yield event
