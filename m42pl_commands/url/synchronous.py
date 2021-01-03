import time
import asyncio
import requests

from m42pl.event import Event

from .__base__ import BaseURL


class URL(BaseURL):
    _about_     = 'Performs synchronous HTTP calls to a given URL'
    _aliases_   = ['url_sync', 'curl_sync', 'wget_sync']
    _syntax_    = BaseURL._syntax_.format(name='|'.join(_aliases_))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def target(self, event, pipeline):
        while True:
            # ---
            # Build HTTP request
            request = {
                'method': self.method,
                'url': self.url,
            }
            for field in ('headers', 'data', 'json'):
                if isinstance(getattr(self, field), dict):
                    request[field] = getattr(self, field)
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
            event.data.update({
                'time': time.time_ns(),
                'source': self.url,
                'request': {
                    'method': self.method,
                    'url': self.url,
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
            if self.frequency > 0:
                await asyncio.sleep(self.frequency)
            # ---
            # Decrease requests count
            self.count -= 1
            if self.count <= 0:
                break
