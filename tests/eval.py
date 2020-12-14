import unittest
from textwrap import dedent

from m42pl.utils.unittest import StreamingCommand, TestScript
from m42pl.event import Event


class Eval(unittest.TestCase, StreamingCommand):
    command_alias = 'eval'
    expected_success = [

        TestScript(
            name='simple_int',
            source=dedent('''\
                | eval simple_int = 42
            '''),
            expected=[
                Event({
                    'simple_int': 42
                })
            ]
        ),

        TestScript(
            name='multi_values',
            source=dedent('''\
                | eval mv_foo = 1, mv_bar = 2
            '''),
            expected=[
                Event({
                    'mv_foo': 1,
                    'mv_bar': 2
                })
            ])
    ]


if __name__ == '__main__':
    unittest.main()
