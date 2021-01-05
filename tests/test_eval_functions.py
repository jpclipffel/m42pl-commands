import unittest
from textwrap import dedent

from m42pl.utils.unittest import StreamingCommand, TestScript
from m42pl.event import Event


class EvalFunctions(unittest.TestCase, StreamingCommand):
    """Test unit for the `eval` command functions.
    """

    command_alias = 'eval'
    expected_success = [

        TestScript(
            name='single_value',
            source=dedent('''\
                | eval
                    test.misc.field                 = field(unexistent, 42),
                    test.cast.tostring              = tostring(42),
                    test.cast.toint                 = toint('42'),
                    test.cast.tofloat               = tofloat('42.21')
            '''),
            expected=[Event({
                'test': {
                    'misc': {
                        'field': 42
                    },
                    'cast': {
                        'tostring': '42',
                        'toint': 42,
                        'tofloat': 42.21
                    }
                }
            })]
        ),


    ]


if __name__ == '__main__':
    unittest.main()
