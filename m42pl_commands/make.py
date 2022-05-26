from asyncio import sleep

from m42pl.commands import GeneratingCommand
from m42pl.event import Event, derive
from m42pl.fields import Field, FieldsMap


class Make(GeneratingCommand):
    _about_     = 'Generates and returns new events'
    _syntax_    = (
        '[[count=]<number>] [[showinfo=](yes|no)] '
        '[[frequency=]<seconds>]'
    )
    _aliases_   = ['make', 'makeevent', 'makeevents']
    _schema_    = {
        'properties': {
            'id': {'type': 'number', 'description': 'Event count'},
            'chunk': {
                'type': 'object',
                'properties': {
                    'chunk': {'type': 'number', 'description': 'Current chunk'},
                    'chunks': {'type': 'number', 'description': 'Chunks count'}
                }
            },
            'count': {
                'type': 'object',
                'properties': {
                    'begin': {'type': 'number', 'description': 'Minium event count in chunk'},
                    'end': {'type': 'number', 'description': 'Maximum event count in chunk'}
                }
            },
            'pipeline': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Chunk pipeline name'}
                }
            }
        }
    }

    def __init__(self, count: int = 1, showinfo: bool = False,
                    frequency: float = 0.0, freqdelay: int = 1):
        """
        :param count:       Number of events to generate.
        :param showinfo:    If set to `True`, add event ID and chunks
                            information. Defaults to `False`.
        :param frequency:   Amount of time to wait in seconds before
                            generating a new event. Defaults to `0`
                            (no wait).
        :param freqdelay:   Amount of events to generate before
                            applying `frequency`.
        """
        super().__init__(count, showinfo, frequency)
        self.fields = FieldsMap(**{
            'count'     : Field(count, default=1, type=int),
            'showinfo'  : Field(showinfo, default=False, type=bool),
            'frequency' : Field(frequency, default=0.0, type=(float, int)),
            'freqdelay' : Field(freqdelay, default=1, type=int)
        })

    async def setup(self, event, pipeline, context):
        # Read fields
        self.fields = await self.fields.read(event, pipeline, context)
        # Get chunks
        chunk_size, remain = divmod(self.fields.count, self._chunks)
        # First chunk
        if self.first_chunk:
            self.begin_count = 0
            self.end_count = chunk_size
        # Intermediate chunk
        elif self.inter_chunk:
            self.begin_count = self._chunk * chunk_size
            self.end_count = self.begin_count + chunk_size
        # Last chunk
        else:
            self.begin_count = self._chunk * chunk_size
            self.end_count = self.begin_count + chunk_size + remain

    async def target(self, event, pipeline, context):
        for i in range(self.begin_count, self.end_count):
            yield derive(
                event,
                self.fields.showinfo and {
                    'id': i,
                    'chunk': {
                        'chunk': self._chunk,
                        'chunks': self._chunks,
                    },
                    'count': {
                        'begin': self.begin_count,
                        'end': self.end_count
                    },
                    'pipeline': {
                        'name': pipeline.name
                    }
                }
                or {}
            )
            if self.fields.frequency > 0.0:
                if self.fields.freqdelay == 1 or i % self.fields.freqdelay == 0:
                    await sleep(self.fields.frequency)
