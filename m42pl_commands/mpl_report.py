from m42pl.commands import MetaCommand
from m42pl.fields import Field
from m42pl.pipeline import PipelineRunner
from m42pl.event import Event


class MPLReport(MetaCommand):
    _about_     = 'Report the pipeline execution'
    _aliases_   = ['mpl-report', 'mpl_report', 'report']
    _syntax_    = '<pipeline> [frequency]'
    _schema_    = {
        'properties': {
            'pipeline': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'Pipeline name'
                    },
                    'state': {
                        'type': 'string',
                        'description': 'Pipeline state as running|ending'
                    },
                    'errors': {
                        'type': 'object',
                        'properties': {
                            'count': {
                                'type': 'number',
                                'description': 'Number of disctinct errors'
                            },
                            'list': {
                                'type': 'object',
                                'desription': 'Distinct errors named as offest:line:column:command',
                                'additionalProperties': {
                                    'type': 'object',
                                    'properties': {
                                        'count': {
                                            'type': 'number',
                                            'description': 'Number of error occurence'
                                        },
                                        'message': {
                                            'type': 'string',
                                            'description': 'Error message'
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            'report': {
                'type': 'object',
                'properties': {
                    'frequency': {
                        'type': 'number',
                        'description': 'Reporting frequency'
                    }
                }
            }
        }
    }

    def __init__(self, pipeline: str, frequency: int = -1):
        super().__init__(pipeline, frequency)
        self.report_pipeline = Field(pipeline)
        self.frequency = Field(frequency, default=-1, type=int)
        self.timer = 0

    async def setup(self, event, pipeline, context):
        self.runner = PipelineRunner(context.pipelines[self.report_pipeline.name])
        self.frequency = await self.frequency.read(event, pipeline, context)
        self.pipeline = pipeline
        self.context = context

    async def run_report_pipeline(self, state: str):
        """Run the reporting pipeline.

        :param state: Current pipeline state
        """
        event = Event({
            'pipeline': {
                'name': self.pipeline.name,
                'state': state,
                'errors': {
                    'count': len(self.pipeline.errors),
                    'list': self.pipeline.errors
                }
            },
            'report': {
                'frequency': self.frequency
            },
        })
        async for _ in self.runner(self.context, event):
            pass


    async def target(self, event, pipeline, context, ending, remain):
        if self.frequency > 0:
            if self.timer >= self.frequency:
                self.timer = 0
                await self.run_report_pipeline('running')
            else:
                self.timer += 1

    async def __aenter__(self):
        await self.run_report_pipeline(state='running')
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.run_report_pipeline(state='ending')
