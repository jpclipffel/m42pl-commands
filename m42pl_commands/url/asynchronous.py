import time
import asyncio
import aiohttp

from m42pl.event import Event

from .__base__ import BaseURL


class URL(BaseURL):
    _about_     = 'Performs asynchronous HTTP calls to a given URL'
    _aliases_   = ['url', 'curl', 'wget']
    _syntax_    = BaseURL._syntax_.format(name='|'.join(_aliases_))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def target(self, event, pipeline):
        async with aiohttp.ClientSession() as session:
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
                async with session.request(**request) as response:
                    # ---
                    # Extract response payload a JSON if possible, as raw text otherwise.
                    # TODO: Remove hard-coded decode format.
                    if 'application/json' in response.headers.get('content-type').lower():
                        payload = await response.json()
                    else:
                        payload = (await response.read()).decode('UTF-8')
                    # ---
                    # Generate and yield event
                    # TODO: Add requests headers section.
                    # yield Event(data={
                    event.data.update({
                        'time': time.time_ns(),
                        'source': self.url,
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
                                'type': response.headers.get('content-type', None)
                            },
                            'headers': dict(response.headers),
                            'content': payload
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
