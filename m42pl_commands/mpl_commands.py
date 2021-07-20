from copy import deepcopy

import m42pl.commands
from m42pl.event import derive
from m42pl.fields import Field
import m42pl


class MPLCommands(m42pl.commands.GeneratingCommand):
    _about_     = 'Returns the list of available commands'
    _syntax_    = '[[command=]command_name] [[ebnf=]yes|no]'
    _aliases_   = ['mpl_commands', 'mpl_command', 'commands', 'command']
    _schema_    = {
        'properties': {
            'command': {
                'type': 'object',
                'properties': {
                    'alias': {},
                    'aliases': {},
                    'schema': {},
                    'about': {},
                    'syntax': {},
                    'type': {},
                    'ebnf': {}
                }
            }
        }
    }
    
    types = [
        m42pl.commands.GeneratingCommand,
        m42pl.commands.StreamingCommand,
        m42pl.commands.BufferingCommand,
        m42pl.commands.MetaCommand,
        m42pl.commands.Command
    ]
    
    def __init__(self, command: str = None, ebnf: bool = False):
        """
        :param command: Returns only the given command information
        :param ebnbf:   Includes the command ENBF
        """
        super().__init__(command)
        self.command_name = Field(command, default=command)
        self.ebnf = Field(ebnf, default=ebnf)

    async def target(self, event, pipeline):
        command_name = await self.command_name.read(event, pipeline)
        ebnf = await self.ebnf.read(event, pipeline)
        #  ---
        if command_name:
            try:
                command = m42pl.command(command_name)
                source = {
                    command_name: command
                }
            except Exception:
                source = {}
        else:
            source = m42pl.commands.ALIASES
        # ---
        for alias, command in source.items():
            yield derive(event, data={
                'command': {
                    'alias': alias,
                    'aliases': command._aliases_,
                    'schema': command._schema_,
                    'about': command._about_,
                    'syntax': command._syntax_,
                    'type': list(filter(None, map(lambda t: issubclass(command, t) and t.__name__ or None, self.types)))[0],
                    'ebnf': ebnf is True and getattr(command, '_ebnf_', '') or ''
                }
            })
