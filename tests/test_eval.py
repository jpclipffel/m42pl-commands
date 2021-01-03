import unittest
from textwrap import dedent

from m42pl.utils.unittest import StreamingCommand, TestScript
from m42pl.event import Event


class Eval(unittest.TestCase, StreamingCommand):
    """Test unit for the `eval` command.
    """

    command_alias = 'eval'
    expected_success = [

        TestScript(
            name='single_value',
            source=dedent('''\
                | eval simple_int = 42
            '''),
            expected=[Event({
                'simple_int': 42
            })]
        ),

        TestScript(
            name='multi_values',
            source=dedent('''\
                | eval mv_foo = 1, mv_bar = 2
            '''),
            expected=[Event({
                'mv_foo': 1,
                'mv_bar': 2
            })]
        ),
        
        TestScript(
            name='syntax_operator',
            source=dedent('''\
                | eval rounded = 40 + 2.0
            '''),
            expected=[Event({
                'rounded': 42.0
            })]
        ),

        TestScript(
            name='syntax_function',
            source=dedent('''\
                | eval rounded = round(42.21, 1)
            '''),
            expected=[Event({
                'rounded': 42.2
            })]),

        TestScript(
            name='syntax_complex_functions',
            source=dedent('''\
                | eval result = tostring(toint(round(40 + 1.0, 1)) + 1) + ' is the answer'
            '''),
            expected=[Event({
                'result': '42 is the answer'
            })]
        )

    ]


if __name__ == '__main__':
    unittest.main()
