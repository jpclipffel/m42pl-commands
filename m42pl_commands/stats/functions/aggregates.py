from m42pl.event import signature

from .__base__ import StatsFunction


class Aggregates(StatsFunction):
    """Returns the internal aggregation structures.
    """

    async def __call__(self, event, pipeline):
        return self.aggregates
