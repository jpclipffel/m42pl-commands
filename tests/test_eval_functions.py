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
                    test.cast.tofloat               = tofloat('42.21'),
                    test.string.clean               = clean('  sp lit ed   ! '),
                    test.path.basename              = basename('/one/two/three'),
                    test.path.dirname               = dirname('/one/two/three'),
                    test.path.joinpath              = joinpath('one', 'two', 'three'),
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
                    },
                    'string': {
                        'clean': 'splited!'
                    },
                    'path': {
                        'basename': 'three',
                        'dirname': '/one/two',
                        'joinpath': 'one/two/three'
                    }
                }
            })]
        ),


    ]


if __name__ == '__main__':
    unittest.main()
