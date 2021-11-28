import unittest
from textwrap import dedent

from m42pl.utils.unittest import StreamingCommand, TestScript
from m42pl.event import Event


class Expand(unittest.TestCase, StreamingCommand):
    """Test unit for the `expand` command.
    """

    command_alias = 'expand'
    expected_success = [

        TestScript(
            name='expand_list',
            source=dedent('''\
                | eval data = list(1, 'two')
                | expand data
            '''),
            expected=[
                Event({'data': 1}),
                Event({'data': 'two'})
            ]
        ),

        TestScript(
            name='expand_single',
            source=dedent('''\
                | eval data = 1
                | expand data
            '''),
            expected=[
                Event({'data': 1})
            ]
        ),

        TestScript(
            name='expand_unexistent',
            source=dedent('''\
                | expand data
            '''),
            expected=[]
        ),

    ]


if __name__ == '__main__':
    unittest.main()
