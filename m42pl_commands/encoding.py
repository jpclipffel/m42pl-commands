from collections import OrderedDict
from textwrap import dedent

import m42pl
from m42pl.commands import StreamingCommand
from m42pl.fields import Field
from m42pl.event import derive


class Base(StreamingCommand):
    _syntax_ = (
        '''{src field} [as {dest field}] with <codec> | '''
        '''{src field} with <codec> [as {dest field}] | '''
        '''[[codec=]<codec>] [[src=]{src field}] [[dest=]{dest field}]'''
    )

    _grammar_ = OrderedDict(StreamingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        encoding_src    : field?
        encoding_dest   : (("as"|"to") field)?
        encoding_codec  : "with" field
        encoding_expr   : (encoding_src encoding_dest encoding_codec)
                        | (encoding_src encoding_codec encoding_dest)
        encoding_args   : arguments
        start           : encoding_expr | encoding_args
    ''')

    class Transformer(StreamingCommand.Transformer):
        def encoding_src(self, items):
            return {'src': items and items[0] or None}

        def encoding_dest(self, items):
            return {'dest': items and items[0] or None}
        
        def encoding_codec(self, items):
            return {'codec': items[0]}

        def encoding_expr(self, items):
            return (), {**items[0], **items[1], **items[2]}
        
        def encoding_args(self, items):
            return items[0]

        def start(self, items):
            return items[0][0], items[0][1]

    def __init__(self, codec: str, src=None, dest=None):
        super().__init__(codec, src, dest)
        self.codec = Field(codec, default=codec)
        self.src = src and Field(src, default=src) or None
        self.dest = dest and Field(dest, default=dest) or None

    async def setup(self, event, pipeline, context):
        self.encoder = m42pl.encoder(
            await self.codec.read(event, pipeline, context)
        )()


class Encode(Base):
    _about_     = 'Encodes event or event field'
    _aliases_   = ['encode',]
    _schema_    = {
        'properties': {
            '{dest_field}': { 'description': 'Encoded field' }
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.dest:
            self.dest = Field('encoded')

    async def target(self, event, pipeline, context):
        if self.src:
            yield await self.dest.write(
                event,
                self.encoder.encode({
                    self.src.name: await self.src.read(event, pipeline, context)
                })
            )
        else:
            yield await self.dest.write(
                event,
                self.encoder.encode(event['data'])
            )


class Decode(Base):
    _about_     = 'Decodes event or event field'
    _aliases_   = ['decode',]
    _schema_    = {
        'properties': {
            '{dest_field}': { 'description': 'Decoded field' }
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.src:
            self.src = Field('encoded')

    async def target(self, event, pipeline, context):
        if self.dest:
            yield await self.dest.write(
                event,
                self.encoder.decode(await self.src.read(event, pipeline, context))
            )
        else:
            yield derive(
                event,
                data=self.encoder.decode(
                    await self.src.read(event, pipeline, context)
                )
            )


class Codecs(StreamingCommand):
    _about_     = 'Returns available codecs'
    _aliases_   = ['codecs',]
    _schema_    = {
        'properties': {
            'code': {
                'type': 'object',
                'properties': {
                    'alias': {'type': 'string', 'description': 'Codec name'},
                    'about': {'type': 'string', 'description': 'Codec info'},
                }
            }
        }
    }

    def __init__(self):
        super().__init__()
        self.field = Field('codec')

    async def target(self, event, pipeline, context):
        for name, encoder in m42pl.encoders.ALIASES.items():
            yield await self.field.write(event, {
                'alias': name,
                'about': encoder._about_
            })
