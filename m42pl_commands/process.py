from collections import OrderedDict
from textwrap import dedent
import subprocess
import asyncio

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field
from m42pl.event import Event


class Process(GeneratingCommand):
    _about_     = 'Runs a process and yields its output line by line'
    _aliases_   = ['process', ]
    _syntax_    = '<command name> [arg, ...]'
    _grammar_   = OrderedDict(GeneratingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        start : args
    ''')
    
    class Transformer(GeneratingCommand.Transformer):
        def start(self, items):
            if len(items) and len(items[0]):
                print(items[0])
                return (), {
                    'command': items[0][0],
                    'args': len(items[0]) > 1 and items[0][1:] or []
                }

    def __init__(self, command: str, args: list = []):
        super().__init__(self, command, args)
        print(f'Process --> {command}, {args}')
        self.command = Field(command)
        self.args = [ Field(arg) for arg in args ]

    async def target(self, event, pipeline):
        cmd = await self.command.read(event, pipeline)
        print(f'Process --> cmd --> {cmd}')
        args = [ await arg.read(event, pipeline) for arg in self.args ]
        print(self.args)
        print(f'--> {[cmd, ] + args}')
        # ---
        process = subprocess.Popen([cmd, ] + args, stdout=subprocess.PIPE)
        for row in iter(process.stdout.readline, b''):
            yield Event(data={
                # "chunk": self._chunk,
                'line': row.rstrip().decode('UTF-8')
            })
        process.terminate()
