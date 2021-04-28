from .__base__ import StatsFunction


class First(StatsFunction):
    """Returns the first value of a given field.
    """

    async def target(self, event, dataset, pipeline):
        if dataset is None:
            value = await self.source_field.read(event, pipeline)
            return (value, value)
        return (dataset, dataset)


class Last(StatsFunction):
    """Returns the last value of a given field.
    """

    async def target(self, event, dataset, pipeline):
        value = await self.source_field.read(event, pipeline)
        return (value, value)
