from textwrap import dedent
from collections import OrderedDict

from typing import Dict

from m42pl.commands import StreamingCommand
from m42pl.utils.eval import Evaluator
from m42pl.fields import Field


class Eval(StreamingCommand):
    _about_     = 'Evaluate a Python expression and assign result to a field'
    _syntax_    = '<field_name> = <expression> [, ...]'
    _aliases_   = ['eval', 'evaluate']
    _grammar_   = OrderedDict(StreamingCommand._grammar_)
    # Eval does not uses the arguments grammar
    _grammar_.pop('arguments_rules')
    # Custom eval grammar
    _grammar_['start'] = dedent('''\
        expression  : field "=" (field | symbol | collection)+
        start       : (expression ","?)+
    ''')
    
    class Transformer(StreamingCommand.Transformer):
        # collections_rules
        function    = lambda self, items: f'{items[0]}{", ".join([str(i) for i in items[1:-1]])}{items[-1]}'  # print(f'function --> {items}')
        sequence    = lambda self, items: f'{items[0]}{" ".join([str(i) for i in items[1:-1]])}{items[-1]}'
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
            try:
                await field.write(event, expr(event.data))
            except Exception as error:
                self.logger.error(error)
                await field.write(event, None)
        yield event
