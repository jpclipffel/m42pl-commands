from m42pl.commands import GeneratingCommand


class Echo(GeneratingCommand):
    _about_     = 'Returns received event or an empty event'
    _aliases_   = ['echo', ]

    def  __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def target(self, event, pipeline):
        yield event
