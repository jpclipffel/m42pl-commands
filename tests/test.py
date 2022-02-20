import unittest
from textwrap import dedent

from m42pl.utils.unittest import Command
import m42pl.commands


EXCLUDED_COMMAND = [
    'm42pl.commands.script.PipelineScript',
    'm42pl.commands.script.JSONScript'
]


class Dummy(unittest.TestCase):
    def test_dummy(self):
        pass


def load_tests(loader, tests, pattern):
    """Custom tests loader.
    
    We start by loading M42PL module: this is necessary to have all
    commands loaded in order to generate their test classes later.

    We then create a new test class for every command class. Unlike
    command-specific tests, we do not care for the command type
    (generating, streaming, etc.) and we directly inherit from the test
    base class ``m42pl.utils.unittest.Command``.

    Unit test custom loader reference:
    https://docs.python.org/3/library/unittest.html#load-tests-protocol
    """

    # Test suite
    suite = unittest.TestSuite()
    # Commands classes and generated tests
    commands = []
    tests: list[type] = []
    # Load commands
    m42pl.load_modules()
    # Generate test classes
    for _, command in m42pl.commands.ALIASES.items():
        cmd_name = f'{command.__module__}.{command.__name__}'
        if cmd_name not in commands and cmd_name not in EXCLUDED_COMMAND:
            commands.append(cmd_name)
            tests.append(
                type(cmd_name, (unittest.TestCase, Command), {
                    'command_alias': command._aliases_[0]
                })
            )
            suite.addTests(loader.loadTestsFromTestCase(tests[-1]))
    # ---
    return suite



if __name__ == '__main__':
    unittest.main()
