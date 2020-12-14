import regex

from m42pl.commands import StreamingCommand
from m42pl.field import Field


class Regex(StreamingCommand):
    __about__   = 'Parse a source field using a regular expression with named groups'
    __syntax__  = '[ expression= ] "regex with named groups" [ field= ] source_field [ [ dest= ] dest_field ] [ [ update= ] {{ true | false }} ]'
    __aliases__ = ['regex', 'rex', 'rx', 'extract', ]
    
    def __init__(self, expression: str, field: str, dest: str = '.', update: bool = False):
        '''Initializes the command instance.
        
        :param expression:  Regular expression with named groups
        :param field:       Source field name
        :param dest:        Destination field name
        :param update:      Update the source field instead
        '''
        super().__init__(expression, field, dest, update)
        self.expression = regex.compile(expression)
        self.source_field = Field(field)
        self.dest_field = dest
        self.update = update
    
    def target(self, pipeline, event):
        # results = self.expression.match(event.get_data(self.field)).groupdict()
        try:
            results = self.expression.match(self.source_field.read(event.data)).groupdict()
        except AttributeError:
            results = { 'failed': self.source_field.read(event.data) }
            # print(f'regex --> failed: {results}')
        # print(f'fields --> {fields}')
        if self.update:
            # event.set_data(self.field, fields)
            self.source_field.write(event.data, results)
        else:
            for field, value in results.items():
                # event.set_data(f'{self.dest}.{field}', value)
                Field(f'{self.dest_field}{field}').write(event.data, value)
        return event
