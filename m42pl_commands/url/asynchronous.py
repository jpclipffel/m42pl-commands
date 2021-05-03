import time
import asyncio
import aiohttp
import regex
import cgi

from m42pl.event import Event

from .__base__ import BaseURL


class URL(BaseURL):
    """Asynchronous HTTP client.
    """

    _about_     = 'Performs asynchronous HTTP calls to a given URL'
    _aliases_   = ['url', 'curl', 'wget']

    # JSON and plain text mime type regexes
    regex_mime_json = regex.compile(r'(application|text)/json')
    regex_mime_text = regex.compile(r'text/(.*)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def read_response(self, response: aiohttp.ClientResponse,
                            mime_type: str, charset: str, **kwargs):
        """Read and decodes the given :param:`response`.

        :param response:    Partial response sent by server
        :param mime_type:   Response's mime type, if any
        :param charset:     Response's charset, if any
        :param kwargs:      Other content type headers (ignored)
        """
        # JSON
        if self.regex_mime_json.match(mime_type or ''):
            return await response.json()
        # Plain text
        elif self.regex_mime_text.match(mime_type or ''):
            return await response.text()
        # Binary data
        else:
            return await response.read()

    async def request_one(self, session: aiohttp.ClientSession, request: dict):
        """Performs the given :param:`request`.

        :param session: Current aiohttp session
        :param request: aiohttp request parameters (method, url, ...)
        """
        async with session.request(**request) as response:
            # Parse content type header
            mime_type, mime_props = cgi.parse_header(
                response.headers.get('content-type', '').lower()
            )
            # Generate and return response data
            return {
                'time': time.time_ns(),
                'request': {
                    'method': response.method,
                    'url': str(response.url),
                    'headers': request.get('headers', {}),
                    'data': request.get('data', {})
                },
                'response': {
                    'status': response.status,
                    'reason': response.reason,
                    'mime': {
                        **{'type': mime_type},
                        **mime_props
                    },
                    'headers': dict(response.headers),
                    'content': await self.read_response(
                        response,
                        mime_type,
                        mime_props
                    )
                }
            }

    async def target(self, event, pipeline):
        fields = await self.fields.read(event, pipeline)
        # Do not run if we're not in the first chunk, i.e. do not
        # request the same URL in multiple process/tasks/threads/...
        if not self.first_chunk:
            return
        # Setup base request (== request template)
        base_request = {}
        for field in ('headers', 'data', 'json'):
            if isinstance(getattr(fields, field), dict):
                base_request[field] = getattr(fields, field)
        # Run
        async with aiohttp.ClientSession() as session:
            while True:
                # Build requests batch
                requests = []
                for url in fields.urls:
                    requests.append(
                        self.request_one(
                            session,
                            {
                                **base_request,
                                **{
                                    'method': fields.method,
                                    'url': url
                                }
                            }))
                # Execute requests and yield them as soon as possible
                for request in asyncio.as_completed(requests):
                    yield event.derive(data=await request)
                # Wait before next requests batch
                if fields.frequency > 0:
                    await asyncio.sleep(fields.frequency)
                # Decrease request count
                fields.count -= 1
                if fields.count <= 0:
                    break
