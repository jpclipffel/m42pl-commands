from __future__ import annotations

import zmq

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field, FieldsMap

from .__base__ import Consumer


class Proxy(GeneratingCommand):
    """Receives ZMQ messages and yields events.
    """

    _aliases_   = ['zmq_proxy', ]
    _about_     = 'Receives and forwards ZMQ messages'
    _syntax_    = '[[frontend=]<frontend URL>] [[backend=]<bakend URL>]'
    _schema_    = {
        'properties': {
            'topic': {'type': 'string', 'description': 'ZMQ topic'},
            'frames': {'type': 'array', 'description': 'Message frames'}
        }
    }

    def __init__(self, frontend: str = 'frontend',
                    backend: str = 'backend',
                    codec: str = 'msgpack', **kwargs):
        """
        :param frontend: Proxy input url (protocol, address, port)
        :param backend: Proxy output url (protocol, address, port)
        """
        self.args = FieldsMap(**{
            'frontend': Field(frontend, default='tcp://127.0.0.1:6666'),
            'backend': Field(backend, default='tcp://127.0.0.1:7777')
        })

    # def __init__(self, topic: str|list = [], *args, **kwargs):
    #     """
    #     :param topic: ZMQ topic name or list of names
    #     """
    #     super().__init__(*args, topic=topic, **kwargs)
    #     # NB: In PUB/SUB, the client socket must subscribe at least to an
    #     # empty topic (''), meaning it will receive all messages (no filter).
    #     self.args.update(**{
    #         'topic': Field(topic, default=['', ], seqn=True)
    #     })

    async def setup(self, event, pipeline, context):
        self.args = await self.args.read(event, pipeline, context)
        self.context = zmq.asyncio.Context.instance()
        # Setup frontend
        self.frontend = self.context.socket(zmq.SUB)
        self.frontend.bind(self.args.frontend)
        # Setup backend
        self.backend = self.context.socket(zmq.PUB)
        self.backend.bind(self.args.backend)

    async def target(self, event, pipeline, context):
        self.proxy = zmq.proxy(self.frontend, self.backend)
        yield event
