import unittest
import json
import importlib

import m42pl


class ParseToJson(unittest.TestCase):
    source = '''
    | test_void
    | test_args 42 21.12 arg 'single quotes string' "double quotes string" {jspath.string}
    | test_kwargs integer=42 float=21.12 inline=arg string_sq='single quotes string' string_dq="double quotes string" jspath={jspath.string}
    | test_subc1 [
        | test_subc1_void
        | test_subc1_args 42 21.12 arg 'single quotes string' "double quotes string" {jspath.string}
        | test_subc1_kwargs integer=42 float=21.12 inline=arg string_sq='single quotes string' string_dq="double quotes string" jspath={jspath.string}
        | test_subc2 [
            | test_subc2_void
            | test_subc2_args 42 21.12 arg 'single quotes string' "double quotes string" {jspath.string}
            | test_subc2_kwargs integer=42 float=21.12 inline=arg string_sq='single quotes string' string_dq="double quotes string" jspath={jspath.string}
        ]
    ]
    '''

    def test_load_modules(self):
        module = importlib.import_module('m42pl_commands.script')
        m42pl.load_modules(paths=[module.__file__, ])
    
    def test_parse(self):
        return list(m42pl.command('script')(script=self.source, mode='json', parse_commands=False)())[0]
    
    def test_structure(self):
        script = json.loads(self.test_parse())
        self.assertEqual(len(script), 3)


class ParseToPipeline(unittest.TestCase):
    source = '''
        | echo 42 21.12 arg 'single quotes string' "double quotes string" {some stupid data}
    '''

    def test_load_modules(self):
        for module in ['script', 'echo']:
            m = importlib.import_module(f'm42pl_commands.{module}')
            m42pl.load_modules(paths=[m.__file__, ])

    def test_parse(self):
        _ = list(m42pl.command('script')(script=self.source, mode='json', parse_commands=True)())[0]
        print(_)
