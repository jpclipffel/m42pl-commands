import unittest
from textwrap import dedent

from m42pl.utils.unittest import StreamingCommand, TestScript
from m42pl.event import Event


class Cut(unittest.TestCase, StreamingCommand):
    """Test unit for the `cut` command.
    """
    command_alias = 'cut'
    expected_success = [

        TestScript(
            name='comma',
            source=dedent('''\
                | eval data = 'one,two,three'
                | cut data ','
            '''),
            expected=[
                Event({'data': ['one', 'two', 'three']})
            ],
        ),

        TestScript(
            name='redundant_commas',
            source=dedent('''\
                | eval data = ',,,,,one,two,,three,,,,'
                | cut data ','
            '''),
            expected=[
                Event({'data': ['one', 'two', 'three']})
            ],
        ),

        TestScript(
            name='no_clean',
            source=dedent('''\
                | eval data = 'one,two,,four'
                | cut data ',' clean=no
            '''),
            expected=[
                Event({'data': ['one', 'two', '', 'four']})
            ],
        ),

    ]


if __name__ == '__main__':
    unittest.main()
