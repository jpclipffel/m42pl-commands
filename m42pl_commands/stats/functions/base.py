from m42pl.fields import Field


class StatsFunction:
    '''Base stats function.
    '''
    
    def __init__(self, source_field: Field, aggr_fields: list, dest_field: Field, aggregates: dict):
        '''
        :param source_field:    Aggregation function source field (must exist).
                                Ex: "| stats min(<source filed>) by ...
                                
        :param aggr_fields:     Aggregations fields.
                                Ex: "| stats min(...) by <aggr_fields>"
                                
        :param dest_field:      Aggregation function result field (created or overwriten).
                                Ex: "| stats min(...) as <dest_field> by ..."
                                
        :param aggregates:      Aggregations structure.
        '''
        self.source_field = source_field
        self.aggr_fields = aggr_fields
        self.dest_field = dest_field
        self.aggregates = aggregates

    async def __call__(self, event, pipeline):
        aggregates = self.aggregates
        # ---
        # Update aggregation table structure with event's fields values
        # For each aggregation level
        for field in self.aggr_fields:
            # Create aggregation level (e.g. 'user' in '{user: {}}')
            if field.name not in aggregates:
                aggregates[field.name] = {}
            # Dive into aggregation level
            aggregates = aggregates[field.name]
            # Create aggregation key (e.g. 'john' and 'jane' in '{user: {john: {}, jane: {}, ...}}')
            ### field_value = str(event.get_data(field.name))
            field_value = str(await field.read(event))
            # if field_value and not field_value in aggregates:
            if field_value not in aggregates:
                aggregates[field_value] = {}
            # Point to final aggregation level
            aggregates = aggregates[field_value]
        # ---
        # Create the latest aggregation level (which will contains the stats function results)
        if not self.dest_field.name in aggregates:
            aggregates[self.dest_field.name] = None
        # ---
        # Run the stats function and let it update its own aggregation level.
        # The stats function **must** returns:
        # tuple[0]: its aggregation level
        # tuple[1]: the event's new value
        aggregates[self.dest_field.name], value = await self.target(event, aggregates[self.dest_field.name], pipeline)
        return value

    async def target(self, *args, **kwargs):
        raise NotImplementedError()
