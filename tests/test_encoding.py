import unittest
from textwrap import dedent

from m42pl.utils.unittest import StreamingCommand, TestScript
from m42pl.event import Event


class Encode(unittest.TestCase, StreamingCommand):
    """Test unit for the `encoding` command.
    """

    command_alias = 'encode'
    script_begin = dedent('''\
        | make showinfo=yes count=1
    ''')
    expected_success = [

        TestScript(
            name='encode_simplesyntax_event',
            source=dedent('''\
                | encode with 'msgpack'
            '''),
            expected=[
                Event({
                    'encoded': b'\x84\xa2id\x00\xa5chunk\x82\xa5chunk\x00\xa6chunks\x01\xa5count\x82\xa5begin\x00\xa3end\x01\xa8pipeline\x81\xa4name\xa4main'
                })
            ],
            fields_in=['encoded']
        ),

        TestScript(
            name='encode_simplesyntax_field',
            source=dedent('''\
                | encode pipeline with 'msgpack' as pipeline_encoded
            '''),
            expected=[
                Event({
                    'pipeline_encoded': b'\x81\xa8pipeline\x81\xa4name\xa4main'
                })
            ],
            fields_in=['pipeline_encoded']
        ),

        TestScript(
            name='encode_longsyntax_event',
            source=dedent('''\
                | encode codec='msgpack'
            '''),
            expected=[
                Event({
                    'encoded': b'\x84\xa2id\x00\xa5chunk\x82\xa5chunk\x00\xa6chunks\x01\xa5count\x82\xa5begin\x00\xa3end\x01\xa8pipeline\x81\xa4name\xa4main'
                })
            ],
            fields_in=['encoded']
        ),

        TestScript(
            name='encode_longsyntax_field',
            source=dedent('''\
                | encode src="pipeline" codec='msgpack' dest="pipeline_encoded"
            '''),
            expected=[
                Event({
                    'pipeline_encoded': b'\x81\xa8pipeline\x81\xa4name\xa4main'
                })
            ],
            fields_in=['pipeline_encoded']
        )

    ]


if __name__ == '__main__':
    unittest.main()
