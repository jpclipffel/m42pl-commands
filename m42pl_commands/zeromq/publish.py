from __future__ import annotations

from typing import List

import zmq

import m42pl
from m42pl.commands import StreamingCommand, MergingCommand
from m42pl.fields import Field

from .__base__ import Producer


class Publish(Producer):
    """Publishes event or event field to a ZMQ queue.

    If no field(s) is/are given, the full event's data will be encoded
    as a single frame using the given encoder (defaults to msgpack).
    Otherwise, each field will be encoded end send as a frame.
    """

    _aliases_   = ['zmq_pub', 'zmq_publish']
    _about_     = 'Publish events or events field(s) to a ZMQ socket'

    def __init__(self, topic: str = None, *args, **kwargs):
        super().__init__(*args, topic=topic, **kwargs)
        self.args.update(**{
            'topic': Field(topic, default=b'')
        })

    async def setup(self, event, pipeline):
        await super().setup(zmq.PUB, event, pipeline)
        # Encode topic
        if not isinstance(self.args.topic, bytes):
            try:
                self.args.topic = self.args.topic.encode()
            except Exception:
                pass

    # def encode(self, data):
    #     """Encode the given :param:`data`.

    #     Data is encoded only if it's not a string or a byte array.
    #     Encoding is done using the class' encoder (defaults to msgpack).

    #     :param data:    Data to encode, typically a frame content.
    #     """
    #     if not isinstance(data, (str, bytes)):
    #         return self.encoder.encode(data)
    #     return data

    async def build_frames(self, event, pipeline) -> List[str|bytes]:
        """Returns a list of frames to be sent through ZMQ.
        """
        frames = []
        if self.args.topic:
            frames.append(self.args.topic)
        for field in await self.fields.read(event, pipeline):
            frames.append(self.encode(field))
        else:
            frames.append(self.encode(event['data']))
            # frames.append(self.encode(event))
        return frames

    async def target(self, event, pipeline):
        """Sends data through ZMQ.
        """
        if self.first_chunk:
            await self.socket.send_multipart(
                await self.build_frames(event, pipeline)
            )
        yield event
