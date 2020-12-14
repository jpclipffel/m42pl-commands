from .base import StatsFunction


class Count(StatsFunction):
    async def target(self, event, dataset, pipeline):
        event_value = event.signature
        if not isinstance(dataset, dict):
            return ({event_value: 1}, 1)
        if not event_value in dataset:
            dataset[event_value] = 1
        else:
            dataset[event_value] += 1
        return (dataset, dataset[event_value])
