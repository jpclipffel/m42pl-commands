from .base import StatsFunction


class DistinctCount(StatsFunction):
    '''Computes the count of distinct value for the given field.
    '''

    async def target(self, pipeline, event, dataset):
        event_value = str(event.get_data(self.source_field))
        # print(f'EVENT VALUE => {event_value}')
        if not isinstance(dataset, list):
            return list(set({event_value, })), 1
        dataset.append(event_value)
        return (dataset, len(dataset))
