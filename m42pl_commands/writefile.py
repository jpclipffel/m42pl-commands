from textwrap import dedent
from collections import OrderedDict

from m42pl.commands import StreamingCommand
from m42pl.event import Event
from m42pl.fields import Field
from m42pl.utils import formatters


class _Write(StreamingCommand):
    """Base class for `write` commands.

    Effective commands are defined at the end of this module.

    This basic implementation does a simple caching of the open file
    descriptors in :ivar:`cache`. As soon as it tries to open more file
    than allowed by the OS, `target` catches an `OSError`, proceeds to
    cleanup the open FD and retry.

    The cache is also cleaned-up at the command's `__aexit__`.

    Furthermore, the file open mode is defined as follow:

    * If command is `write` or `writefile`, open mode starts with `w`
      (write and truncate)
    * If command is `write-append` or `writefile-append`, open mode
      starts with 'a' (write and append)
    * If the first event or event field written to a given path is
      `bytes`, `b` (binary) is added to mode; otherwise, the mode is
      not changed.

    :ivar mode:         Write mode
    :ivar formatter:    Event formatter; Default to `JsonFormatter`
    :ivar cache:        File descriptors cache
    """

    _syntax_    = '({field name} to) {file path}'

    _grammar_ = OrderedDict(StreamingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        start: (field "to")? field
    ''')

    # Real mode is defined by children commands
    mode = ''

    class Transformer(StreamingCommand.Transformer):
        def start(self, items):
            return (), {
                'path':  len(items) > 1 and items[1] or items[0],
                'field': len(items) > 1 and items[0] or None
            }

    def __init__(self, path: str, field: str = None):
        """
        :param path:    File path
        :param field:   Field to write; If None, write complete event
        """
        super().__init__(path, field)
        self.path = Field(path)
        self.field = field and Field(field, default='') or None
        self.formatter = formatters.Json()
        self.cache = {}

    async def format(self, event, pipeline):
        if self.field:
            return await self.field.read(event, pipeline)
        return self.formatter(event)

    async def target(self, event, pipeline):
        # Get data and deduce open mode first
        data = await self.format(event, pipeline)
        mode = isinstance(data, bytes) and self.mode + 'b' or self.mode
        # Get path
        path = await self.path.read(event, pipeline)
        # Open given file at `path` and add it to cache
        if path not in self.cache:
            try:
                # pylint: disable=bad-open-mode
                self.cache[path] = open(path, mode)
            except OSError:
                self.cleanup()
                # pylint: disable=bad-open-mode
                self.cache[path] = open(path, mode)
        # Write to file
        if isinstance(data, bytes):
            self.cache[path].write(data)
        else:
            print(data, file=self.cache[path])
        # Done
        yield event

    def cleanup(self):
        """Closes the open file descriptors.
        """
        for _, fd in self.cache.items():
            try:
                fd.close()
            except Exception:
                pass

    async def __aexit__(self, *args, **kwargs):
        self.cleanup()


class Write(_Write):
    _about_     = 'Write events or events field to a file (truncate)'
    _aliases_   = ['write', 'writefile']
    mode = 'w'


class WriteAppend(_Write):
    _about_     = 'Write events or events field to a file (append)'
    _aliases_   = ['write-append', 'writefile-append']
    mode = 'a'
