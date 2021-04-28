from .__base__ import StatsFunction


class Count(StatsFunction):
    """Count the number of events.
    """
    
    async def target(self, event, dataset, pipeline):
        if not isinstance(dataset, dict):
            return ({event.signature: 1}, 1)
        if event.signature not in dataset:
            dataset[event.signature] = 1
        else:
            dataset[event.signature] += 1
        return (dataset, dataset[event.signature])
