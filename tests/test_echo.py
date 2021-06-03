import unittest
from textwrap import dedent

from m42pl.utils.unittest import GeneratingCommand, TestScript
from m42pl.event import Event


class Buffer(unittest.TestCase, GeneratingCommand):
    """Test unit for the `buffer` command.
    """

    command_alias = 'echo'
    expected_success = [

        TestScript(
            name='echo',
            source=dedent('''\
                | echo
            '''),
            first_event=Event({
                'hello': 'world'
            }),
            expected=[Event({
                'hello': 'world'
            })],
        ),

    ]


if __name__ == '__main__':
    unittest.main()
