import m42pl.commands
from m42pl.event import Event
from m42pl.fields import Field
import m42pl


class MPLCommands(m42pl.commands.GeneratingCommand):
    _about_     = 'Returns the list of available commands'
    _syntax_    = '[[command=]command_name]'
    _aliases_   = ['mpl_commands', 'mpl_command']
    
    types = [
        m42pl.commands.GeneratingCommand,
        m42pl.commands.StreamingCommand,
        m42pl.commands.BufferingCommand,
        m42pl.commands.MetaCommand,
        m42pl.commands.Command
    ]
    
    def __init__(self, command: str = None):
        '''
        :param command: Returns only this `command` information.
        '''
        self.command_name = Field(command, default=command)

    async def target(self, event, pipeline):
        command_name = await self.command_name.read(event, pipeline)
        print(f'command_name --> {command_name}')
        if command_name:
            try:
                command = m42pl.command(command_name)
                print(f'command --> {command}')
                source = {
                    command_name: command
                }
            except Exception:
                source = {}
        else:
            source = m42pl.commands.ALIASES
        # ---
        for alias, command in source.items():
            yield Event(data={
                'command': {
                    'alias': alias,
                    'aliases': command._aliases_,
                    'about': command._about_,
                    'syntax': command._syntax_,
                    'type': list(filter(None, map(lambda t: issubclass(command, t) and t.__name__ or None, self.types)))[0],
                    'ebnf': getattr(command, '_ebnf_', '')
                }
            })
