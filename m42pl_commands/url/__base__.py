from m42pl.commands import GeneratingCommand
from m42pl.fields import Field


class BaseURL(GeneratingCommand):
    """Base class for URL commands classes.

    This base class handle the following children commands properties:

    * Dynamic `_syntax_` attribute
    * Fields (parameters)
    """

    _syntax_ = '({name}) [url=]<url> [method=<method>] [frequency=<seconds>] [count=<integer>]'

    def __init__(self, url: str, method: str = 'GET',
                    headers: dict = {}, data: dict = None, json: dict = None,
                    frequency: int = -1, count: int = 1):
        '''
        :param url:         URL to fetch.

        :param method:      HTTP method ("GET", "POS.T", ...).
                            Case insensitive.

        :param headers:     HTTP headers field.
                            Defaults to an empty map.

        :param data:        Form field.
                            Should be either `None` or a dict field reference.
                            Defaults to `None`.
        
        :param json:        JSON field.
                            Should be either `None` or a dict field reference.
                            Defaults to `None`.

        :param frequency:   Sleep time between each call.
                            Defaults to -1 (not sleep time).

        :param count:       Number of requests to performs.
                            Default to 1 (a single request).
        '''
        super().__init__(url, method, frequency, count)
        self.url        = Field(url)
        self.method     = Field(method, default=method)
        self.headers    = Field(headers, default=headers)
        self.data       = Field(data, default=data)
        self.json       = Field(json, default=json)
        self.frequency  = Field(frequency, default=frequency)
        self.count      = Field(count, default=count)

    async def setup(self, event, pipeline):
        self.url        = await self.url.read(event, pipeline)
        self.method     = await self.method.read(event, pipeline)
        self.headers    = await self.headers.read(event, pipeline)
        self.data       = await self.data.read(event, pipeline)
        self.json       = await self.json.read(event, pipeline)
        self.frequency  = await self.frequency.read(event, pipeline)
        self.count      = await self.count.read(event, pipeline)
