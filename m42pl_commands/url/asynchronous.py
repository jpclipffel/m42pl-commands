import time
import asyncio
import aiohttp

# from m42pl.commands import GeneratingCommand
from m42pl.event import Event

from .__base__ import BaseURL


class URL(BaseURL):
    _about_     = 'Performs asynchronous HTTP calls to a given URL'
    _aliases_   = ['url', 'curl', 'wget']
    _syntax_    = BaseURL._syntax_.format(name=' | '.join(_aliases_))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def target(self, event, pipeline):
        async with aiohttp.ClientSession() as session:
            while self.count > 0:
                async with session.request(self.method, self.url) as response:
                    if response.headers.get("content-type").lower() == "application/json":
                        html = await response.json()
                    else:
                        html = await response.read()
                    yield Event(data={
                        "time": time.time_ns(),
                        "source": self.url,
                        "request": {
                            "method": response.method,
                            "url": str(response.url)
                        },
                        "response": {
                            "status": response.status,
                            "reason": response.reason,
                            "mime": {
                                "type": response.headers.get("content-type", None)
                            },
                            "headers": dict(response.headers),
                            "content": html.decode('UTF-8')
                        }
                    })
                # Wait
                if self.frequency > 0:
                    await asyncio.sleep(self.frequency)
                # Decrease count
                self.count -= 1
