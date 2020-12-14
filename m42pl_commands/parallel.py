from textwrap import dedent

from m42pl.commands import GeneratingCommand


class Parallel(GeneratingCommand):
    __about__   = 'Run multiples pipelines in parallel'
    __syntax__  = 'parallel [ | command ... | ... ], [ | command ... | ... ], ...'
    __aliases__ = ['parallel', ]
    
    def __init__(self, references: str):
        self.references = references
    
    def target(self, context, event):
        context.pipelines.dispatch()