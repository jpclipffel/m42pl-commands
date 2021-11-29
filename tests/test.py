import unittest
from textwrap import dedent

from m42pl.utils.unittest import Command
import m42pl.commands


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
    base class `m42pl.utils.unittest.Command` (we just care about the
    generic tests).

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
        if command.__name__ not in commands:
            commands.append([command.__name__])
            tests.append(
                type(command.__name__, (unittest.TestCase, Command), {
                    'command_alias': command._aliases_[0]
                })
            )
            suite.addTests(loader.loadTestsFromTestCase(tests[-1]))
    # ---
    return suite



if __name__ == '__main__':
    unittest.main()
