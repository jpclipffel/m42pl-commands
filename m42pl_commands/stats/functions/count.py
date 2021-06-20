from m42pl.event import signature

from .__base__ import StatsFunction


class Count(StatsFunction):
    """Count the number of events.
    """
    
    async def target(self, event, dataset, pipeline):
        if not isinstance(dataset, dict):
            return ({signature(event): 1}, 1)
        if signature(event) not in dataset:
            dataset[signature(event)] = 1
        else:
            dataset[signature(event)] += 1
        return (dataset, dataset[signature(event)])
