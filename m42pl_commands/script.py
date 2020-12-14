from textwrap import dedent
import json
import uuid
from collections import OrderedDict

from lark import Transformer as _Transformer, Discard

import m42pl
from m42pl.commands import Command
from m42pl.pipeline import Pipeline
from m42pl.context import Context


class ScriptBuilder(Command):
    '''The `script` command parse a M42PL script using two
    :param:`mode`s:

    * `context` (default): The source :param:`script` is parsed and
    returned as a new :class:`Context` instance.
    
    * `json`: The source :param:`script` is parsed and returned as a
    list of JSON-serializable :class:`dict` instances. This is useful
    mostly for testing purposes.

    The parameter :param:`parse_commands` determines if a pipeline's
    commands are parsed or not: If set to `False`, only the pipeline
    structure is parsed, and the commands are rendered as string.
    This is useful mostly for testing purposes.
    '''

    _about_     = 'Parses a M42PL script'
    _syntax_    = '[script=]<script> [mode={{ pipeline|json}}]'
    _aliases_   = ['script',]
    _grammar_   = OrderedDict({
        'directives': dedent('''\
            %import common.WS
            %import common.NEWLINE
            %ignore NEWLINE
        '''),
        # ---
        'fields_terminals': Command._grammar_['fields_terminals'],
        # ---
        'script_terminals': dedent('''\
            SYMBOL      : ( "+" | "-" | "*" | "/" | "%" | "^" | ":" | "!" | "<" | ">" | "{" | "}" | "(" | ")" | "," | "=" | "==" | ">=" | "<=" | "!=" )
        '''),
        # ---
        'fields_rules': Command._grammar_['fields_rules'],
        # ---
        # 'script_rules': dedent('''\
        #     space       : WS+
        #     body        : (field | WS | SYMBOL)+
        #     block       : "[" (space | commands)? "]"
        #     blocks      : (block space? ","? space?)+
        #     command     : space? "|" space? NAME body? blocks?
        #     commands    : command+
        #     pipeline    : commands
        #     start       : pipeline
        # ''')
        'script_rules': dedent('''\
            space       : WS+
            body        : (field | WS | SYMBOL)+
            block       : "[" (space | commands)? "]"
            blocks      : (block space? ","? space?)+
            command     : space? "|" space? NAME (body | blocks)*
            commands    : command+
            pipeline    : commands
            start       : pipeline
        ''')
    })


    class Transformer(_Transformer):
        '''Base script transformer.
        '''

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.pipelines = OrderedDict()

        def _discard(self, _):
            raise Discard

        def space(self, _):
            raise Discard

        float       = lambda self, items: str(items[0])
        integer     = lambda self, items: str(items[0])
        boolean     = lambda self, items: str(items[0].lower())
        name        = lambda self, items: str(items[0])
        string      = lambda self, items: str(items[0])
        eval        = lambda self, items: str(items[0])
        jspath      = lambda self, items: str(items[0])
        dotpath     = lambda self, items: str(items[0])
        body        = lambda self, items: ''.join(items) \
                                            .lstrip(' ') \
                                            .rstrip(' ')

    class ContextTransformer(Transformer):
        '''Returns a new :class:`Context` from the parsed script.
        '''

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.context = Context()

        def command(self, items):
            # print(f'command --> {items}')
            command_name = str(items[0])
            command_body = ' '.join(
                filter(
                    None,
                    len(items) > 1 and items[1:] or []
                )
            )
            return m42pl.command(command_name).from_script(command_body)
        
        def commands(self, items):
            return items

        def pipeline(self, items):
            pipeline_name = str(uuid.uuid4())
            self.pipelines[pipeline_name] = Pipeline(
                commands=items[0],
                context=self.context,
                name=pipeline_name
            )

        def block(self, items):
            pipeline_name = str(uuid.uuid4())
            self.pipelines[pipeline_name] = Pipeline(
                commands=len(items) > 0 and items[0] or [], 
                context=self.context,
                name=pipeline_name
            )
            return f'@{pipeline_name}'
        
        def blocks(self, items):
            return ', '.join(items)

        def start(self, items):
            self.context.add_pipelines(self.pipelines)
            return self.context


    class JsonTransformer(Transformer):
        '''Returns a JSON string from the parsed script.
        '''
        
        def __init__(self, parse_commands: bool = True,
                     *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.parse_commands = parse_commands

        def command(self, items):
            command_name = str(items[0])
            command_body = ' '.join(filter(None, items[1:])) or ''
            if self.parse_commands:
                command = m42pl.command(command_name) \
                          .from_script(command_body)
                if type(command) in [list, tuple]:
                    return [c.to_dict() for c in command]
                return command.to_dict()
            else:
                return {
                    'name': command_name,
                    'body': command_body
                }

        def blocks(self, items):
            return ', '.join(items)

        def commands(self, items):
            def flatten_command(items):
                _commands = []
                for i in items:
                    if type(i) in [list, tuple]:
                        _commands += flatten_command(i)
                    else:
                        _commands.append(i)
                return _commands
            return flatten_command(items)

        def pipeline(self, items):
            pipeline_name = str(uuid.uuid4())
            self.pipelines[pipeline_name] = {
                'name': pipeline_name,
                'commands': items[0]
            }

        def block(self, items):
            pipeline_name = str(uuid.uuid4())
            self.pipelines[pipeline_name] = {
                'name': pipeline_name,
                'commands': len(items) > 0 and items[0] or []
            }
            return f'@{pipeline_name}'

        def start(self, items):
            return json.dumps(self.pipelines)


    def __init__(self, source: str, mode: str = 'context',
                 parse_commands: bool = True):
        '''
        :param source:          Source script
        :param mode:            Parsing mode ('pipeline' or 'json').
                                Defaults to 'pipeline'.
        :param parse_commands:  Parses commands if `True` (default).
        '''
        self.source = source
        if mode == 'context':
            self._transformer_ = self.ContextTransformer() # type: ignore
        elif mode == 'json':
            self._transformer_ = self.JsonTransformer(parse_commands) # type: ignore
        else:
            raise Exception(f'unknow parsing mode: {mode}')

    def target(self):
        # Cleanup source and add a leading '|' if necessary.
        source = self.source.lstrip(' ')
        if source[0] != '|':
            source = f'| {source}'
        # Parse and transform source.
        return self._transformer_.transform(
            self._parser_.parse(source)
        )
    
    def __call__(self, *args, **kwargs):
        return self.target()
