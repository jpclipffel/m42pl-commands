import os

import json
from jinja2 import Template, Environment, FunctionLoader

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Jinja(StreamingCommand):
    _about_     = 'Renders a Jinja template'
    _syntax_    = '[src=]{source field} [dest=]{destination field} [[searchpath=]<search path>]'
    _aliases_   = ['jinja', 'template_jinja', 'jinja_template']

    # Custom Jinja2 filters
    filters = {
        'jsonify': json.dumps
    }

    def __init__(self, src: str, dest: str, searchpath: str = '.'):
        """
        :param src_field:   Source field.
        :param dest_field:  Destination field.
        :param searchpath:  Templates default search path.
        """
        super().__init__(src, dest, searchpath)
        self.src_field  = Field(src)
        self.dest_field = Field(dest)
        self.searchpath = Field(searchpath, default=os.path.abspath('.'))

    async def setup(self, event, pipeline, context):
        self.searchpath = await self.searchpath.read(event, pipeline, context)
        self.jinja_env = Environment(loader=FunctionLoader(self.load_template))
        # Inject custom filters
        self.jinja_env.filters.update(self.filters)

    def load_template(self, name):
        """Custom templates loader used by the Jinja environment.
        
        This loader search included templates (templates referenced in
        'include' or 'block' directives) in the parrent directory of
        the currently processed file.
        """
        try:
            with open(os.path.join(self.searchpath, name), 'r') as fd:
                return fd.read()
        except Exception:
            return None
    
    async def target(self, event, pipeline, context):
        try:
            yield await self.dest_field.write(
                event,
                self.jinja_env.from_string(await self.src_field.read(event, pipeline, context)).render(**event['data'])
            )
        except Exception as error:
            self.logger.error(error)
            yield event
