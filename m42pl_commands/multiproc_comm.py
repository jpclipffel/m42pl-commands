from multiprocessing.queues import Queue
from multiprocessing.connection import Connection

import m42pl
from m42pl.commands import StreamingCommand, GeneratingCommand

from typing import Any, Union

# pylint: disable=unsubscriptable-object
Channel = Union[Connection, Queue]


class MultiprocBase:
    """Base class for MPI send & receive commands.

    :ivar msgpack_field: Message pack fields name
    """

    msgpack_field = '__multiproc__'

    def __init__(self, chan: Channel):
        """
        :param chan: Multiprocessing's Pipe connection or Queue
        :ivar read: Channel read method (receive data)
        :ivar write: Channel write method (send data)
        """
        self.chan = chan
        if isinstance(chan, Connection):
            self.read = self.read_pipe
            self.write = self.write_pipe
        elif isinstance(chan, Queue):
            self.read = self.read_queue
            self.write = self.write_queue
        else:
            raise Exception(f'Invalid channel type: {type(chan)}')

    def read_pipe(self) -> bytes:
        """Receives data from a pipe's connection.
        """
        return self.chan.recv_bytes() # type: ignore
    
    def write_pipe(self, data: Any):
        """Sends data to a pipe's connection.
        """
        return self.chan.send_bytes(data) # type: ignore
    
    def read_queue(self) -> bytes:
        """Receives data from a queue.
        """
        return self.chan.get() # type: ignore
    
    def write_queue(self, data: Any):
        """Sends data to a queue.
        """
        return self.chan.put(data) # type: ignore


class MultiprocSend(MultiprocBase, StreamingCommand):
    """Encodes and send events to a multiprocessing pipe or queue.
    """
    
    _aliases_ = ['multiproc-send',]
    
    # def __new__(cls, *args, **kwargs) -> tuple:
    #     """Returns a new (encode, send) commands tuple.
    #     """
    #     self = super(MultiprocSend, cls).__new__(cls)
    #     self.__init__(*args, **kwargs)
    #     return (
    #         m42pl.command('encode')(
    #             codec='msgpack',
    #             dest=self.msgpack_field
    #         ),
    #         self
    #     )
    
    def __init__(self, chan: Channel):
        """
        :param chan: Multiprocessing's Pipe connection or Queue
        """
        super().__init__(chan)
        self.encoder = m42pl.encoder('msgpack')()

    async def target(self, event, pipeline, context):
        try:
            # self.write(event['data'][self.msgpack_field])
            self.write(
                self.encoder.encode(event)
            )
        except Exception as error:
            self.logger.exception(error)
            pass
        yield event
    
    async def __aexit__(self, *args, **kwargs):
        """Sends a sentinel event at the pipeline's end.
        """
        self.logger.info(f'sending sentinel event')
        self.write(self.chunk)


class MultiprocReceive(MultiprocBase, GeneratingCommand):
    """Receives and decodes events from a multiprocessing pipe.

    :ivar producers_count: Number of producers sending data
    :ivar producers_closed: Number of closed producers
    """
    
    _aliases_ = ['multiproc-receive',]
    
    # def __new__(cls, *args, **kwargs) -> tuple:
    #     """Returns a new (receive, decode) commands tuple.
    #     """
    #     self = super(MultiprocReceive, cls).__new__(cls)
    #     self.__init__(*args, **kwargs)
    #     return (
    #         self,
    #         m42pl.command('decode')(
    #             codec='msgpack',
    #             src=self.msgpack_field
    #         )
    #     )
    
    def __init__(self, chan: Channel):
        """
        :param chan:    Multiprocessing's Pipe connection or Queue
        """
        super().__init__(chan)
        self.encoder = m42pl.encoder('msgpack')()
        self.producers_count = 0
        self.producers_closed = 0
    
    async def target(self, event, pipeline, context):
        while True:
            try:
                data = self.read()
                # If data is a sentinel event (a tuple of two integers),
                # update and check producers status
                if isinstance(data, tuple) and len(data) == 2:
                    self.logger.info(f'Received sentinel event')
                    if data[1] > self.producers_count:
                        self.producers_count = data[1]
                    self.producers_closed += 1
                    # If all the producers have been closed, terminate the command
                    if (self.producers_closed > 0 and self.producers_count > 0 
                        and self.producers_closed == self.producers_count):
                        self.logger.info(f'All producers closed, terminating')
                        return
                # Otherwise, process event
                elif data:
                    # yield {
                    #     'data': {
                    #         self.msgpack_field: data
                    #     },
                    #     'meta': {},
                    #     'sign': None
                    # }
                    yield self.encoder.decode(data)
            except EOFError:
                self.logger.info(f'Channel has been closed')
                break
            except Exception as error:
                self.logger.info(f'Invalid event or sentinel received')
                self.logger.exception(error)
                break
