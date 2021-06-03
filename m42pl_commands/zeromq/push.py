from __future__ import annotations

from typing import List

import zmq

import m42pl
from m42pl.commands import StreamingCommand, MergingCommand
from m42pl.fields import Field

from .__base__ import Producer


class Push(Producer):
    """Pushes event or event field to a ZMQ queue.

    If no field(s) is/are given, the full event's data will be encoded
    as a single frame using the given encoder (defaults to msgpack).
    Otherwise, each field will be encoded end send as a frame.
    """

    _aliases_   = ['zmq_push', 'zmq_ventilate',]
    _about_     = 'Push events or events field(s) to a ZMQ socket'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup(self, event, pipeline):
        await super().setup(zmq.PUSH, event, pipeline)

    # async def get_payload(self, event, pipeline) -> str|bytes:
    #     # Select data
    #     if self.field:
    #         data = await self.field.read(event, pipeline)
    #     else:
    #         data = event.data
    #     # Encode and return data if not bytes or str
    #     if not isinstance(data, (str, bytes)):
    #         return self.encoder.encode(data)
    #     # Return data
    #     return data

    async def build_frames(self, event, pipeline) -> List[str|bytes]:
        """Returns a list of frames to be sent through ZMQ.
        """
        frames = []
        for field in await self.fields.read(event, pipeline):
            frames.append(self.encode(field))
        else:
            frames.append(self.encode(event.data))
        return frames

    async def target(self, event, pipeline):
        """Sends data through ZMQ.
        """
        if self.first_chunk:
            print(f'sending')
            await self.socket.send_multipart(
                await self.build_frames(event, pipeline)
            )
        yield event
