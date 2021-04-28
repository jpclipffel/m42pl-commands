from .__base__ import StatsFunction


class DistinctCount(StatsFunction):
    """Counts the number of distinct value for a given field.
    """

    async def target(self, pipeline, event, dataset):
        event_value = str(event.get_data(self.source_field))
        # print(f'EVENT VALUE => {event_value}')
        if not isinstance(dataset, list):
            return list(set({event_value, })), 1
        dataset.append(event_value)
        return (dataset, len(dataset))
