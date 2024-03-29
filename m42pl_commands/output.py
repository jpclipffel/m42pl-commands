import os

import m42pl
from m42pl.fields import Field
from m42pl.commands import DequeBufferingCommand, MergingCommand


class Output(DequeBufferingCommand, MergingCommand):
    """Prints events on the standard output.

    :ivar count: Number of received events
    :ivar term_columns: Terminal's columns count
    """

    _about_     = 'Prints events'
    _syntax_    = '[[format=]<hjson|raw|...>] [[header=]<yes|no>] [[buffer=]<number>]'
    _aliases_   = ['output', 'print']
    _schema_    = {'properties': {}} # type: ignore

    def __init__(self, format: str = 'hjson', header: str|bool = False,
                    buffer: str|int = 1):
        """
        :param format: Output format
        :param header: Display header (``True``) or not (``False``)
        :param buffer: Buffer max size; Defaults to 1
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

        :param event: Event to print
        """
        if self.header:
            header = f'[{self.counter}] [{event["sign"]}]'
            print(f'{header} {"-" * (self.term_columns - (len(header)+1))}')
        print(self.encoder.encode(event['data']))
        self.counter += 1

    async def setup(self, event, pipeline, context):
        # Setup current instance
        self.format = await self.format.read(event, pipeline, context)
        self.header = await self.header.read(event, pipeline, context)
        # Setup parent instance
        await super().setup(
            event,
            pipeline,
            context,
            await self.buffer.read(event, pipeline, context)
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

    def __init__(self, *args, **kwargs):
        super().__init__()

    async def setup(self, *args, **kwargs):
        pass

    async def __call__(self, event, *args, **kwargs):
        yield event

    async def target(self, event, *args, **kwargs):
        yield event
