import os
import json

from pygments import highlight
# pylint: disable=no-name-in-module
from pygments.lexers import JsonLexer
# pylint: disable=no-name-in-module
from pygments.formatters import TerminalFormatter

from m42pl.fields import Field
from m42pl.commands import DequeBufferingCommand


class JSONDecoder(json.JSONEncoder):
    """Custom JSON decoder to handle non-generic event fields.

    Simply returns the item (`o`) representation as a string.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def default(self, o):
        return repr(o)


class RawFormatter:
    """Format event as a string.
    """
    def __call__(self, event):
        return str(event.data)


class JSONFormatter:
    """Format event as a highlighted JSON string.
    """
    def __init__(self):
        self.lexer = JsonLexer()
        self.formatter = TerminalFormatter()
    
    def __call__(self, event):
        try:
            return highlight(
                json.dumps(event.data, indent=2, cls=JSONDecoder),
                self.lexer,
                self.formatter
            )
        except Exception as error:
            return json.dumps({'error': str(error)}, indent=2)


class Output(DequeBufferingCommand):
    _about_     = 'Prints events'
    _syntax_    = '[[format=]{raw|json}] [[buffer=]<number>]'
    _aliases_   = ['output', 'print']

    def __init__(self, format: str = 'json', header: bool = False,
                    buffer: int = 0):
        """
        :param format:  Output format
        :param buffer:  Buffer max size. Defaults to 1.
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
        print(self.formatter(event))
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
        if self.format.lower() == 'json':
            self.formatter = JSONFormatter()
        else:
            self.formatter = RawFormatter()

    async def target(self, pipeline):
        async for event in super().target(pipeline):
            self.printer(event)
            yield event
