import os
import json

import m42pl
from m42pl.fields import Field
from m42pl.commands import DequeBufferingCommand, MergingCommand
from m42pl.utils import formatters


class Output(DequeBufferingCommand, MergingCommand):
    """Prints events on the standard output.

    :ivar count:            Number of received events
    :ivar term_columns:     Terminal's columns count
    """

    _about_     = 'Prints events'
    _syntax_    = '[[format=](hjson|raw|...)] [[buffer=]<number>]'
    _aliases_   = ['output', 'print']

    def __init__(self, format: str = 'hjson', header: bool = False,
                    buffer: int = 0):
        """
        :param format:  Output format
        :param header:  Display header (`True`) or not (`False`)
        :param buffer:  Buffer max size; Defaults to 1
        """
        super().__init__(format, header, buffer)
        # ---
        self.format = Field(format, default=format, type=str, seqn=False)
        self.header = Field(header, default=False, type=bool, seqn=False)
        self.buffer = Field(buffer, default=1, type=int, seqn=False)
        # ---
        self.counter = 0
        # ---
        # Note: os.get_terminal_size() may fails if redirecting output
        # to smtg. else than stdout / stderr.
        # Fallback to standard terminal width (80) in case of error.
        try:
            self.term_columns = int(os.get_terminal_size().columns)
        except OSError:
            self.term_columns = 80

    def printer(self, event):
        """Print event on the standard output.

        :param event:   Event to print.
        """
        if self.header:
            header = f'[{self.counter}] [{event.signature}]'
            print(f'{header} {"-" * (self.term_columns - (len(header)+1))}')
        print(self.encoder.encode(event.data))
        self.counter += 1

    async def setup(self, event, pipeline):
        # Setup current instance
        self.format = await self.format.read(event, pipeline)
        self.header = await self.header.read(event, pipeline)
        # Setup parent instance
        await super().setup(
            event,
            pipeline, 
            await self.buffer.read(event.data, pipeline)
        )
        # Prepare formatter
        try:
            self.encoder = m42pl.encoder(self.format)(indent=2)
        except Exception as error:
            raise error
            self.encoder = m42pl.encoder('raw')()

        # if self.format.lower() == 'json':
        #     print(f'using "json" formatter')
        #     self.formatter = formatters.JsonTextColor(indent=2)
        # else:
        #     print(f'using "raw" formatter')
        #     self.formatter = formatters.Raw()

    async def target(self, pipeline):
        async for event in super().target(pipeline):
            self.printer(event)
            yield event


class NoOut(Output):
    """Fake output command.
    """

    _about_     = 'Mimics output syntax but does not prints events'
    _aliases_   = ['noout', 'nooutput', 'noprint']

    async def target(self, pipeline):
        async for event in super(Output, self).target(pipeline):
            yield event
