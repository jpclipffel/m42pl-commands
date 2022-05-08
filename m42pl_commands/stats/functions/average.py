from .__base__ import StatsFunction


class Average(StatsFunction):
    """Returns the list of unique values for a given field.

    Dataset format:
    - [0] (float): the previous average
    - [1] (int): the number of events
    """

    async def target(self, event, dataset, pipeline, context):
        event_value = await self.source_field.read(event, pipeline, context)
        if not isinstance(dataset, tuple):
            dataset = (0.0, 0)
        try:
            dataset = (
                # New average
                ((dataset[0] * dataset[1]) + event_value) / (dataset[1] + 1),
                # Number of events
                dataset[1] + 1
            )
        except Exception:
            pass
        return (dataset, dataset[0])
