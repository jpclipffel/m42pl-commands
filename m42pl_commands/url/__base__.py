from m42pl.commands import GeneratingCommand
from m42pl.fields import Field, FieldsMap


class BaseURL(GeneratingCommand):
    """Base class for URL commands.

    This base class handle the following children commands properties:

    * The `_syntax_` attribute
    * the `_schema_` attribute
    * Fields (parameters)
    """

    _syntax_ = (
        '[urls=](url, ...) [[method=]{HTTP method}] [[headers]={headers k/v}]'
        '[[data=]{data k/v}] [[json=]{json k/v}] [[frequency=]{seconds}]'
        '[[count=]{integer}]'
    )

    _schema_ = {
        'properties': {
            'time': { 'type': 'number' },
            'request': {
                'type': 'object',
                'description': 'HTTP request',
                'properties': {
                    'method': { 'type': 'string' },
                    'url': { 'type': 'string' },
                    'headers': { 'type': 'object' },
                    'data': { 'type': 'object' }
                }
            },
            'response': {
                'type': 'object',
                'description': 'HTTP response',
                'properties': {
                    'status': { 'type': 'number' },
                    'reason': { 'type': 'string' },
                    'mime': { 'type': 'object' },
                    'headers': { 'type': 'object' },
                    'content': {}
                }
            }
        }
    }

    def __init__(self, urls: str, method: str = 'GET',
                    headers: dict = {}, data: dict = None, json: dict = None,
                    frequency: int = -1, count: int = 1):
        """
        :param urls: URLs to fetch
        :param method: HTTP method (``GET``, ``POST``, ...)
        :param headers: HTTP headers field
            (defaults to an empty ``dict``)
        :param data: Form field (defaults to ``None``)
            Should be either ``None`` or a ``dict`` field
        :param json: JSON payload (defaults to ``None``)
            Should be either ``None`` or a ``dict`` field
        :param frequency: Sleep time between each call
            (defaults to -1, i.e. no sleep time)
        :param count: Number of requests to performs
            (defaults to 1, i.e. a single request)
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
