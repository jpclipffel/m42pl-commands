from copy import deepcopy

from m42pl.commands import DictBufferingCommand


class Buffer(DictBufferingCommand):
    __about__   = 'Delays events processing'
    __syntax__  = '[[size=]<buffer size>]'
    __aliases__ = ['buffer', ]

    def __init__(self, size: int = 128):
        super().__init__(maxlen=size)
