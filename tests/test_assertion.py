import unittest
from textwrap import dedent

from m42pl.utils.unittest import StreamingCommand, TestScript
from m42pl.event import Event


class Assert(unittest.TestCase, StreamingCommand):
    """Test unit for the `assertion` command.
    """

    command_alias = 'rename'
    script_begin = dedent('''\
        | make count=1 showinfo=yes
    ''')
    expected_success = [

        TestScript(
            name='valid',
            source=dedent('''\
                | assert id == 0
            '''),
            expected=[
                Event({
                    'id': 0
                })
            ],
            fields_in=['id',]
        )

    ]



if __name__ == '__main__':
    unittest.main()
