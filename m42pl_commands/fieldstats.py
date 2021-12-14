from m42pl.commands import BufferingCommand
from m42pl.event import Event


class FieldStats(BufferingCommand):
    _aliases_   = ['fieldstats', 'fieldsstats', 'fstats']
    _about_     = 'Compute fields statistics'

    def __init__(self):
        super().__init__()
        self.stats = {}

    async def setup(self, event, pipeline, context):
        await super().setup(event, pipeline, maxsize=100)

    def stats_key(self, key, value):
        if not isinstance(value, dict):
            if not key in self.stats:
                self.stats[key] = {
                    'type': set()
                }
            self.stats[key]['type'].add(str(type(value).__name__))
        else:
            for k, v in value.items():
                self.stats_key(f'{key}.{k}', v)

    async def target(self, pipeline):
        async for event in super().target(pipeline):
            self.stats_key('', event['data'])
        yield Event(data=self.stats)
