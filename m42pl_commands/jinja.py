import os

from jinja2 import Template, Environment, FunctionLoader

from m42pl.commands import StreamingCommand
from m42pl.field import Field


class Jinja(StreamingCommand):
    __about__   = 'Render a Jinja2 template.'
    __syntax__  = '{ [src_field=] <source field> | [src_file=] <source file> } [ [dest_field=] <destination field> [dest_file=] <destination file> ]'
    __aliases__ = ['jinja', 'template_jinja', ]
    
    def __init__(self, src_field: str = None, dest_field: str = None, src_file: str = None, dest_file: str = None,
                 searchpath: str = '.'):
        '''Initializes the command instance.

        :param src_field:           Source field.
        :param optional dest_field: Destination field.
                                    Defaults to `src_field` if neither `dest_field` not `dest_file` are set.
        :param optional src_file:   Source file.
        :param optional dest_file:  Destination file.
        :param optional searchpath: Templates default search path.
        '''
        super().__init__(src_field, dest_field, src_file, dest_file, searchpath)
        # ---
        self.src_field = src_field and Field(src_field) or None
        self.dest_field = dest_field and Field(dest_field) or None
        self.src_file = src_file and Field(src_file) or None
        self.dest_file = dest_file and Field(dest_file) or None
        self.searchpath = os.path.abspath(searchpath)
        # ---
        if self.dest_field is None and self.dest_file is None:
            self.dest_field = self.src_field
        # ---
        self.renderer = self.src_field and self.renderer_field or self.renderer_file
        self.writer = self.dest_field and self.writer_field or self.writer_file
        # ---
        self.jinja_env = Environment(loader=FunctionLoader(self.load_template))
        self.current_file = None

    def load_template(self, name):
        '''Custom templates loader used by the Jinja environment.
        
        This loader search included templates (e.g. templates referenced in 'include' or 'block' directives)
        in the parrent directory of the current processed file.
        '''
        print(f'load_template --> {name}')
        current_path = self.current_file and os.path.dirname(self.current_file) or self.searchpath
        try:
            with open(os.path.join(current_path, name), 'r') as fd:
                return fd.read()
        except Exception:
            return None

    def renderer_field(self, event):
        # return Template(self.src_field.read(event.data)).render(**event.data)
        return self.jinja_env.from_string(self.src_field.read(event.data)).render(**event.data)
    
    def renderer_file(self, event):
        try:
            self.current_file = self.src_file.read(event.data)
            with open(self.current_file, 'r') as fd:
                # return Template(fd.read()).render(**event.data)
                return self.jinja_env.from_string(fd.read()).render(**event.data)
        except Exception as error:
            self._logger.error(f'failed to render template: {str(error)}')
            return ''
    
    def writer_field(self, event, rendered):
        self.dest_field.write(event.data, rendered)
        return event
    
    def writer_file(self, event, rendered):
        try:
            with open(self.dest_file.read(event.data), 'w') as fd:
                fd.write(rendered)
        except Exception as error:
            print(f'error 2 --> {error}')
            pass
        return event
    
    def target(self, event, pipeline):
        try:
            self.writer(event, self.renderer(event))
        except Exception as error:
            print(f'error 3 --> {error}')
            pass
        return event
