from mpi4py import MPI

import m42pl
from m42pl.commands import StreamingCommand, GeneratingCommand


class MPISend(StreamingCommand):
    """...
    """

    _aliases_ = ['mpi-send', ]

    def __init__(self, comm):
        """
        :param comm: MPI communication channel
        """
        super().__init__()
        self.comm = comm
    
    async def target(self, event, pipeline, context):
        self.comm.send(event, dest=0)
        yield event

    async def __aexit__(self, *args, **kwargs):
        self.comm.send(None, dest=0)


class MPIReceive(GeneratingCommand):
    """...
    """

    _aliases_ = ['mpi-receive', ]

    def __init__(self, comm, size: int):
        """
        :param comm: MPI communication channel
        :param size: Number of workers
        """
        super().__init__()
        self.comm = comm
        self.size = size

    async def target(self, event, pipeline, context):
        while self.size > 0:
            _event =  self.comm.recv(source=MPI.ANY_SOURCE)
            if _event is not None:
                yield _event
            else:
                self.size -= 1
