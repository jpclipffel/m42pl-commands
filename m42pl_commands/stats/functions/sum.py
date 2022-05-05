from .__base__ import StatsFunction


class Sum(StatsFunction):
    """Returns the list of unique values for a given field.
    """

    async def target(self, event, dataset, pipeline, context):
        event_value = await self.source_field.read(event, pipeline, context)
        if not isinstance(dataset, float):
            dataset = 0.0
        try:
            dataset += float(event_value)
        except Exception:
            pass
        return (dataset, dataset)
