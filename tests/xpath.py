import unittest
from textwrap import dedent

from m42pl.utils.unittest import StreamingCommand, TestScript
from m42pl.event import Event


class XPath(unittest.TestCase, StreamingCommand):
    command_alias = 'xpath'
    script_begin = dedent('''\
        | read files/xpath/plant_catalog.xml mode='file'
    ''')
    expected_success = [

        TestScript(
            name='simple_int',
            source=dedent('''\
                | xpath '//PLANT[ZONE = 4]'
            '''),
            expected=[
                Event({
                    'simple_int': 42
                })
            ]
        ),

    ]


if __name__ == '__main__':
    unittest.main()
