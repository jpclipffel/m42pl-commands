import zmq
import zmq.asyncio


class Base:
    """Base ZMQ socket wrapper class.
    """
    def __init__(self, *args, **kwargs) -> None:
        self.context = None
        self.socket = None

    async def setup(self, event, pipeline) -> None:
        """Setup ZMQ.
        """
        self.context = zmq.asyncio.Context.instance()
    
    async def __aexit__(self, *args, **kwargs) -> None:
        """Teardown ZMQ.
        """
        self.socket.close()
        self.context.destroy()
