from m42pl.commands import GeneratingCommand
from m42pl.fields import Field


class BaseURL(GeneratingCommand):
    _syntax_ = '''{{{name}}} {{ <url> | url='<url>' }} [ method=<method> ] [ frequency=<seconds> ] [ count=<integer> ]'''

    def __init__(self, url: str, method: str = 'GET',
                 frequency: int = -1, count: int = 1):
        '''
        :param url:         URL to fetch.
        :param method:      HTTP method ("GET", "POST", ...)
                            Case insensitive.
        :param frequency:   Sleep time between each call.
                            Defaults to -1 (not sleep time).
        :param count:       Number of requests to performs.
                            Default to 1 (a single request).
        '''
        self.url        = Field(url)
        self.method     = Field(method, default=method)
        self.frequency  = Field(frequency, default=frequency)
        self.count      = Field(count, default=count)

    async def setup(self, event, pipeline):
        self.url        = await self.url.read(event, pipeline)
        self.method     = await self.method.read(event, pipeline)
        self.frequency  = await self.frequency.read(event, pipeline)
        self.count      = await self.count.read(event, pipeline)
