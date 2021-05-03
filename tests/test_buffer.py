import unittest
from textwrap import dedent

from m42pl.utils.unittest import BufferingCommand, TestScript
from m42pl.event import Event


class Buffer(unittest.TestCase, BufferingCommand):
    """Test unit for the `buffer` command.
    """

    command_alias = 'buffer'
    script_begin = dedent('''\
        | make count=11
    ''')
    expected_success = [

        TestScript(
            name='simple_one',
            source=dedent('''\
                | buffer size=5 showchunk=yes
            '''),
            expected=[
                *[Event({'chunk': 1}),] * 5,
                *[Event({'chunk': 2}),] * 5,
                *[Event({'chunk': 3}),] * 1,
            ],
        ),


    ]


if __name__ == '__main__':
    unittest.main()
