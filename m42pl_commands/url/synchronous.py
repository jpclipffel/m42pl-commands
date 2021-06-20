import time
import asyncio
import requests

from m42pl.event import Event

from .__base__ import BaseURL


class URL(BaseURL):
    """Synchronous HTTP client.
    """

    _about_     = 'Performs synchronous HTTP calls to a given URL'
    _aliases_   = ['url_sync', 'curl_sync', 'wget_sync']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def target(self, event, pipeline):
        fields = await self.fields.read(event, pipeline)
        # Do not run if we're not in the first chunk, i.e. do not
        # request the same URL in multiple process/tasks/threads/...
        if not self.first_chunk:
            return
        # Run
        while True:
            # ---
            # Build HTTP request
            request = {
                'method': fields.method,
                'url': fields.url,
            }
            for field in ('headers', 'data', 'json'):
                if isinstance(getattr(fields, field), dict):
                    request[field] = getattr(fields, field)
            # ---
            # Executes HTTP request
            response = requests.request(**request)
            # ---
            # Extract response payload a JSON if possible, as raw text otherwise.
            # TODO: Remove hard-coded decode format.
            if 'application/json' in response.headers.get('content-type').lower():
                try:
                    response_data = response.json()
                except Exception:
                    response_data = response.text
            else:
                response_data = response.text
            # ---
            # Generate and yield event
            # yield Event(data={
            event['data'].update({
                'time': time.time_ns(),
                'source': fields.url,
                'request': {
                    'method': fields.method,
                    'url': fields.url,
                    'headers': dict(response.request.headers),
                    'data': request.get('data', {})
                },
                'response': {
                    'status': response.status_code,
                    'reason': response.reason,
                    'mime': {
                        'type': response.headers.get('content-type', None)
                    },
                    'headers': dict(response.headers),
                    'content': response_data
                }
            })
            yield event
            # ---
            # Wait before next request
            if fields.frequency > 0:
                await asyncio.sleep(fields.frequency)
            # ---
            # Decrease requests count
            fields.count -= 1
            if fields.count <= 0:
                break
