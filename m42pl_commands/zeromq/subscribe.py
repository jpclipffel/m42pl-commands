from __future__ import annotations

import zmq

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field

from .__base__ import Consumer


class Subscribe(Consumer):
    """Receives ZMQ messages and yields events.
    """

    _aliases_   = ['zmq_sub', 'zmq_subscribe']
    _about_     = 'Subscribe and receive messages from ZMQ'
    _syntax_    = Consumer._syntax_ + ' [[topic=]<topic>]'
    _schema_    = {
        'properties': {
            'topic': {'type': 'string', 'description': 'ZMQ topic'},
            'frames': {'type': 'array', 'description': 'Message frames'}
        }
    }


    def __init__(self, topic: str|list = [], *args, **kwargs):
        """
        :param topic: ZMQ topic name or list of names
        """
        super().__init__(*args, topic=topic, **kwargs)
        # NB: In PUB/SUB, the client socket must subscribe at least to an
        # empty topic (''), meaning it will receive all messages (no filter).
        self.args.update(**{
            'topic': Field(topic, default=['', ], seqn=True)
        })

    async def setup(self, event, pipeline, context):
        await super().setup(zmq.SUB, event, pipeline)
        # Configure topic (envelope filtering)
        self.logger.info(f'registering topics: {self.args.topic}')
        for topic in self.args.topic:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
    
    async def target(self, event, pipeline, context):
        while True:
            try:
                # Read ZMQ frames
                frames = await self.socket.recv_multipart()
                # If there is a topic, try to decode it and set data seek
                # to 2nd frame
                if len(frames) > 1:
                    seek = 1
                    try:
                        topic = frames[0].decode()
                    except Exception:
                        topic = frames[0]
                # If there is no topic, set if to an empty string
                # and set data seek to 1st frame
                else:
                    seek = 0
                    topic = ''
                # Done
                yield await self.field.write(event, {
                    'topic': topic,
                    'frames': frames[seek:]
                })
            except Exception:
                raise
