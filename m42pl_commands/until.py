from copy import deepcopy

from m42pl.commands import StreamingCommand, GeneratingCommand
from m42pl.fields import Field


# class Until(StreamingCommand):
class Until(GeneratingCommand):
    """Run a sub-pipeline until a field become true.

    This command is similar to a do-while statement:

    * The sub-pipeline is run once
    * The sub-pipeline is run again until the given `field` become true
    """

    _about_     = 'Run a sub-pipeline once and repeat until a field become true'
    _syntax_    = '<field> <pipeline>'
    _aliases_   = ['until', 'while']

    def __init__(self, field: str, pipeline: str):
        """
        :param field:       Conditional field
        :param pipeline:    Pipeline ID
        """
        super().__init__(field, pipeline)
        self.field = Field(field)
        self.pipeline = Field(pipeline)

    async def setup(self, event, pipeline):
        self.pipeline = pipeline.context.pipelines[self.pipeline.name]

    async def target(self, event, pipeline):
        source_event = event
        latest_event = None
        field_value = False
        # ---
        while not field_value:
            async for _event in self.pipeline(source_event):
                latest_event = _event
                field_value = await self.field.read(latest_event, pipeline)
                yield latest_event
