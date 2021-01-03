import unittest
from textwrap import dedent

from m42pl.utils.unittest import StreamingCommand, TestScript
from m42pl.event import Event


class Rename(unittest.TestCase, StreamingCommand):
    """Test unit for the `rename` command.
    """

    command_alias = 'rename'
    script_begin = dedent('''\
        | make showinfo=yes
    ''')
    expected_success = [

        TestScript(
            name='single_existing_field',
            source=dedent('''\
                | rename chunk as renamed_chunk
            '''),
            expected=[
                Event({
                    'renamed_chunk': {
                        'chunk': 1,
                        'chunks': 1
                    }
                })
            ],
            fields_in=['renamed_chunk']
        )
        
    ]


if __name__ == '__main__':
    unittest.main()
