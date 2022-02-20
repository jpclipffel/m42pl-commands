from .__base__ import StatsFunction


class List(StatsFunction):
    """Returns the list of all values for a given field.
    """

    async def target(self, event, dataset, pipeline, context):
        event_value = await self.source_field.read(event, pipeline, context)
        if not isinstance(dataset, list):
            dataset = list()
        if isinstance(event_value, list):
            for i in event_value:
                dataset.append(i)
        else:
            dataset.append(event_value)
        return (dataset, dataset)
