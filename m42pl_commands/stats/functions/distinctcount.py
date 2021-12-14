from .__base__ import StatsFunction


class DistinctCount(StatsFunction):
    """Counts the number of distinct value for a given field.
    """

    async def target(self, event, dataset, pipeline, context):
        event_value = await self.source_field.read(event, pipeline, context)
        if not isinstance(dataset, set):
            return set({event_value, }), 1
        dataset.add(event_value)
        return (dataset, len(dataset))
