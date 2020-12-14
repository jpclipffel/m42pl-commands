from textwrap import dedent

from m42pl.commands import MetaCommand


class Ignore(MetaCommand):
    _about_     = 'Does nothing'
    _aliases_   = ['ignore', 'pass', 'comment']
    _syntax_    = '...'
    _grammar_   = {
        'start': dedent('''\
            start : /.+/
        ''')
    }
    
    class Transformer(MetaCommand.Transformer):
        def start(self, items):
            return (), {}
    
    def __init__(self, *args, **kwargs):
        super().__init__()
