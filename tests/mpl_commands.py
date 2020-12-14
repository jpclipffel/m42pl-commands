import unittest
from textwrap import dedent

from m42pl.utils.unittest import GeneratingCommand, TestScript
from m42pl.event import Event


class MPLCommands(unittest.TestCase, GeneratingCommand):
    command_alias = 'mpl_commands'
    expected_success = [

        TestScript(
            name='single_command',
            source=dedent('''\
                | mpl_commands "mpl_commands"
            '''),
            expected=[
                Event({
                    'command': {
                        'alias': 'mpl_commands',
                        'aliases': ['mpl_commands', 'mpl_command']
                    }
                })
            ],
            fields_in=['command']
        )
    ]



if __name__ == '__main__':
    unittest.main()