from .base import StatsFunction


class Values(StatsFunction):
    async def target(self, event, dataset, pipeline):
        event_value = await self.source_field.read(event)
        if not isinstance(dataset, list):
            dataset = list()
        if event_value:
            if isinstance(event_value, list):
                for i in event_value:
                    if i not in dataset:
                        dataset.append(i)
            elif event_value not in dataset:
                dataset.append(event_value)
        return (dataset, dataset)
