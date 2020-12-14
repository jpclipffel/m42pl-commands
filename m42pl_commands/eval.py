from textwrap import dedent
# from lark import Discard

from collections import OrderedDict
from typing import Dict

from m42pl.commands import StreamingCommand
from m42pl.utils.eval import Evaluator
from m42pl.fields import Field


class Eval(StreamingCommand):
    _aliases_   = ['eval', ]
    _about_     = 'Evaluate Python expressions and assign results to fields'
    _syntax_    = '<field name> = <expression> [, ...]'
    _grammar_   = OrderedDict(StreamingCommand._grammar_)
    # Eval override arguments grammar and does not uses pipelines grammar
    _grammar_.pop('arguments_rules')
    # Custom eval grammar
    # _grammar_['eval_symbols'] = dedent('''\
    #     // eval_symbols
    #     EVAL_SYMBOLS    : ( "+" | "-" | "*" | "/" | "%" | "^" | "!" | "<" | ">" | "==" | ">=" | "<=" | "!=" )
    # ''')
    # ---
    # _grammar_['collections_rules'] = dedent('''\
    #     // collections_rules
    #     function    : FUNC_START ((field | collection | EVAL_SYMBOLS) ","?)* COLLECTION_END
    #     sequence    : SEQN_START ((field | collection | EVAL_SYMBOLS) ","?)* COLLECTION_END
    #     ?collection : function
    #                 | sequence
    # ''')
    # ---
    # _grammar_['eval_rules'] = dedent('''\
    #     // eval_rules
    #     // symbol      : EVAL_SYMBOLS
    #     expression  : field "=" (field | symbol | collection)+
    # ''')
    # ---
    _grammar_['start'] = dedent('''\
        expression  : field "=" (field | symbol | collection)+
        start       : (expression ","?)+
    ''')
    
    class Transformer(StreamingCommand.Transformer):
        # collections_rules
        #function        = lambda self, items: f'{items[0]}{" ".join([str(i) for i in items[1:-1]])}{items[-1]}'  # print(f'function --> {items}')
        #sequence        = function

        # eval_rules
        # symbol      = lambda self, items: str(items[0]) # print(f'symbol --> {items}')
        expression  = lambda self, items: (items[0], len(items) > 1 and ' '.join([str(i) for i in items[1:]]) or '')
        start       = lambda self, items: ((), {'fields': dict(items)})
    
    def __init__(self, fields: Dict[str, str]):
        super().__init__(fields)
        self.fields = dict([
            (Field(field), Evaluator(expr))
            for field, expr 
            in fields.items()
        ])
    
    async def target(self, event, pipeline):
        for field, expr in self.fields.items():
            await field.write(event, expr(event.data))
        yield event
