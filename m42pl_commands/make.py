from asyncio import sleep

from m42pl.commands import GeneratingCommand
from m42pl.event import Event
from m42pl.fields import Field


class Make(GeneratingCommand):
    _about_     = 'Generates and returns new events'
    _syntax_    = '[[count=]<number of events>] [[showcount=](yes|no)] [[frequency=]<events generation frequency in seconds (float)>]'
    _aliases_   = ['make', 'makeevent', 'makeevents']

    def __init__(self, count: int = 1, showinfo: bool = False, frequency: float = 0.0):
        '''
        :param count:       Number of events to generate.
        :param showinfo:    If set to `True`, add event ID and chunks
                            information. Defaults to `False`.
        :param frequency:   Amount of time to wait in seconds before
                            generating a new event. Defaults to `0`
                            (no wait).
        '''
        super().__init__(count, showinfo, frequency)
        self.count = Field(count, 1, int)
        self.showinfo = Field(showinfo, False, bool)
        self.frequency = Field(frequency, 0.0, float)

    async def setup(self, event, pipeline):
        self.count = await self.count.read(event, pipeline)
        self.showinfo = await self.showinfo.read(event, pipeline)
        self.frequency = await self.frequency.read(event, pipeline)

        chunk_size, remain = divmod(self.count, self._chunks)

        # First chunk
        if self.first_chunk:
            self.begin_count = 0
            self.end_count = chunk_size
            self.chunk_type = 'first'
        # Intermediate chunk
        elif self.inter_chunk:
            self.begin_count = self._chunk * chunk_size
            self.end_count = self.begin_count + chunk_size
            self.chunk_type = 'inter'
        # Last chunk
        else:
            self.begin_count = self._chunks * chunk_size
            self.end_count = (self._chunk * chunk_size) + remain
            self.chunk_type = 'last'

    async def target(self, event, pipeline):
        print(f'===============  {self.chunk_type}: {self.begin_count}, {self.end_count} ==============')
        for i in range(self.begin_count, self.end_count):
            yield Event(
                self.showinfo and {
                    'id': i,
                    'chunk': {
                        'chunk': self._chunk,
                        'chunks': self._chunks,
                        'type': self.chunk_type
                    },
                    'count': {
                        'begin': self.begin_count,
                        'end': self.end_count
                    }
                }
                or {}
            )
            if self.frequency > 0:
                await sleep(self.frequency)
