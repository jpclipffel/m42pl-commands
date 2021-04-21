import os

from jinja2 import Template, Environment, FunctionLoader

from m42pl.commands import StreamingCommand
from m42pl.fields import Field


class Jinja(StreamingCommand):
    _about_     = 'Renders a Jinja template'
    _syntax_    = '[src_field=]{source field} [dest_field=]{destination field} [[searchpath=]<search path>]'
    _aliases_   = ['jinja', 'template_jinja', 'jinja_template']
    
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

    async def setup(self, event, pipeline):
        self.searchpath = await self.searchpath.read(event, pipeline)
        self.jinja_env = Environment(loader=FunctionLoader(self.load_template))

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
    
    async def target(self, event, pipeline):
        try:
            yield await self.dest_field.write(
                event,
                self.jinja_env.from_string(await self.src_field.read(event, pipeline)).render(**event.data)
            )
        except Exception as error:
            self.logger.error(error)
            yield event
