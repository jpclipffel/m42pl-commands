from __future__ import annotations

from typing import List

import zmq

from .__base__ import Producer


class Push(Producer):
    """Pushes event or event field to a ZMQ queue.

    If no field(s) is/are given, the full event's data will be encoded
    as a single frame using the given encoder (defaults to `msgpack`).
    Otherwise, each field will be encoded and send as a frame.
    """

    _aliases_   = ['zmq_push', 'zmq_ventilate',]
    _about_     = 'Push events or events field(s) to ZMQ'
    _schema_    = {'properties': {}} # type: ignore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup(self, event, pipeline, context):
        await super().setup(zmq.PUSH, event, pipeline, context)

    async def build_frames(self, event, pipeline, context) -> List[str|bytes]:
        """Returns a list of frames to be sent through ZMQ.
        """
        frames = []
        fields = await self.fields.read(event, pipeline, context)
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
                await self.build_frames(event, pipeline, context)
            )
        yield event
