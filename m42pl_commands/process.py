from collections import OrderedDict
from textwrap import dedent
import subprocess

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field
from m42pl.event import Event, derive


class Process(GeneratingCommand):
    _about_     = 'Runs a process and yields its output line by line'
    _aliases_   = ['process',]
    _syntax_    = '{command name} [argument, ...]'
    _grammar_   = OrderedDict(GeneratingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        start : args
    ''')
    
    class Transformer(GeneratingCommand.Transformer):
        def start(self, items):
            if len(items) and len(items[0]):
                return (), {
                    'command': items[0][0],
                    'params': len(items[0]) > 1 and items[0][1:] or []
                }

    def __init__(self, command: str, params: list = []):
        """
        :param command: Command name  (e.g. 'ls')
        :param args:    Command arguments
        """
        super().__init__(command, params)
        self.command = Field(command, default=command)
        self.args = [ Field(param) for param in params ]

    async def target(self, event, pipeline, context):
        cmd = await self.command.read(event, pipeline, context)
        args = [ await arg.read(event, pipeline, context) for arg in self.args ]
        # ---
        process = subprocess.Popen([cmd, ] + args, stdout=subprocess.PIPE)
        for row in iter(process.stdout.readline, b''):
            yield derive(event, {
                'line': row.rstrip().decode('UTF-8')
            })
        process.terminate()
