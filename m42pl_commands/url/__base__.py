from m42pl.commands import GeneratingCommand
from m42pl.fields import Field, FieldsMap


class BaseURL(GeneratingCommand):
    """Base class for URL commands.

    This base class handle the following children commands properties:

    * The `_syntax_` attribute
    * Fields (parameters)
    """

    _syntax_ = (
        '[urls=](url, ...) [[method=]{HTTP method}] [[headers]={headers k/v}]'
        '[[data=]{data k/v}] [[json=]{json k/v}] [[frequency=]{seconds}]'
        '[[count=]{integer}]'
    )

    def __init__(self, urls: list = [], method: str = 'GET',
                    headers: dict = {}, data: dict = None, json: dict = None,
                    frequency: int = -1, count: int = 1):
        """
        :param urls:        URLs to fetch
        :param method:      HTTP method ("GET", "POST", ...)
        :param headers:     HTTP headers field; Defaults to an empty map
        :param data:        Form field; Should be either `None` or a
                            dict field reference; Defaults to `None`
        :param json:        JSON field; Should be either `None` or a
                            dict field reference; Defaults to `None`
        :param frequency:   Sleep time between each call; Defaults to 
                            -1 (no sleep time)
        :param count:       Number of requests to performs; Default to
                            1 (a single request)
        """
        super().__init__(urls, method, headers, data, json, frequency, count)
        self.fields = FieldsMap(**{
            'urls': Field(urls, seqn=True, default=[]),
            'method': Field(method, default=method),
            'headers': Field(headers, default=headers),
            'data': Field(data, default=data),
            'json': Field(json, default=json),
            'frequency': Field(frequency, default=frequency),
            'count': Field(count, default=count)
        })
