from __future__ import annotations

from collections import OrderedDict
from textwrap import dedent

from typing import Any

from m42pl.commands import MetaCommand, GeneratingCommand
from m42pl.fields import Field, LiteralField
from m42pl.event import derive


class KVWrite(MetaCommand):
    """Write key/value pairs to the pipeline's context's KVStore.

    TODO: Maybe make <key name> optional and use the <field> name by
    default ?
    """

    _about_     = 'Set a KVStore key'
    _aliases_   = ['kvwrite', 'kv_write']
    _syntax_    = '<key name> [=] <field>'
    _schema_    = {'properties': {}} # type: ignore

    _grammar_   = OrderedDict(GeneratingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        key     : field
        value   : field
        start   : key "="? value
    ''')

    class Transformer(GeneratingCommand.Transformer):
        def key(self, items):
            return {'key': items[0]}
        
        def value(self, items):
            return {'value': items[0]}

        def start(self, items):
            return (), {**items[0], **items[1]}

    def __init__(self, key: str, value: Any):
        """
        :param key:         Key name
        :param value:       Key value
        """
        super().__init__(key, value)
        self.key = Field(key, default=key)
        self.value = Field(value, default=value)
    
    async def target(self, event, pipeline, context):
        if event:
            await context.kvstore.write(
                await self.key.read(event, pipeline, context),
                await self.value.read(event, pipeline, context)
            )


class KVRead(GeneratingCommand):
    """Reads key/value pairs from the pipeline's context's KVStore.

    TODO: Maybe make the <field> optional and use the <key name> as
    default ?
    """

    _about_     = 'Read a KVStore key'
    _aliases_   = ['kvread', 'kv_read']
    _syntax_    = '<key name> | <key name> as <field> | <field> = <key name>'
    _schema_    = {
        'properties': {
            '{dest}': {'description': 'Key value read from KVStore'}
        }
    }

    _grammar_   = OrderedDict(GeneratingCommand._grammar_)
    _grammar_['start'] = dedent('''\
        key     : field
        dest    : field
        kvname  : field
        start   : (key "as" dest) | (dest "=" key) | kvname
    ''')

    class Transformer(GeneratingCommand.Transformer):
        def key(self, items):
            return {'key': items[0]}
        
        def dest(self, items):
            return {'dest': items[0]}

        def kvname(self, items):
            return {'key': items[0], 'dest': items[0]}

        def start(self, items):
            # If only a kvname is given
            if len(items) < 2:
                return (), items[0]
            # If both a key and dest are given
            else:
                return (), {**items[0], **items[1]}

    def __init__(self, key: str, dest):
        """
        :param key:         Key name
        :param dest:        Destination field
        """
        super().__init__(key, dest)
        self.key = Field(key, default=key)
        self.dest = Field(dest, default=dest)

    async def target(self, event, pipeline, context):
        if event:
            yield await self.dest.write(
                event,
                await context.kvstore.read(
                    await self.key.read(event, pipeline, context)
                )
            )


class KVItems(GeneratingCommand):
    """Reads the full KVStore.
    """

    _about_     = 'Read a KVStore'
    _aliases_   = ['kvitems', 'kv_items']
    _syntax_    = '[[key=]{key}]'
    _schema_    = {
        'properties': {
            '{key}': {'description': 'Key value read from KVStore'}
        }
    }

    def __init__(self, key: str|None = None):
        self.key = Field(key)

    async def setup(self, event, pipeline, context):
        self.key = await self.key.read(event, pipeline, context)

    async def target(self, event, pipeline, context):
        async for k, i in context.kvstore.items(self.key):
            yield await LiteralField(k).write(derive(event), i)


class KVDelete(MetaCommand):
    """Deletes a KVStore key.
    """

    _about_     = 'Delete a KVStore entry'
    _aliases_   = ['kvdelete', 'kv_delete']
    _syntax_    = '[key=]{key}'
    _schema_    = {'properties': {}} # type: ignore

    def __init__(self, key: str):
        self.key = Field(key)

    async def target(self, event, pipeline, context):
        await context.kvstore.delete(
            await self.key.read(event, pipeline, context)
        )
