from .__base__ import StatsFunction


class Min(StatsFunction):
    """Returns the minimum value for the given field.
    """

    async def target(self, event, dataset, pipeline):
        event_value = await self.source_field.read(event, pipeline)
        if not isinstance(dataset, (int, float)):
            dataset = None
        if isinstance(event_value, (int, float)) and (dataset is None or event_value < dataset):
            return (event_value, event_value)
        return (dataset, dataset)


class Max(StatsFunction):
    """Returns the maximum value for the given field.
    """

    async def target(self, event, dataset, pipeline):
        event_value = await self.source_field.read(event, pipeline)
        if not isinstance(dataset, (int, float)):
            dataset = None
        if isinstance(event_value, (int, float)) and (dataset is None or event_value > dataset):
            return (event_value, event_value)
        return (dataset, dataset)
