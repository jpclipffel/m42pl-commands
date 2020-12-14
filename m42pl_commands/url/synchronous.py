import time
import asyncio
import requests

# from m42pl.commands import GeneratingCommand
from m42pl.event import Event

from .__base__ import BaseURL


class URL(BaseURL):
    _about_     = 'Performs synchronous HTTP calls to a given URL'
    _aliases_   = ['url_sync', 'curl_sync', 'wget_sync']
    _syntax_    = BaseURL._syntax_.format(name=' | '.join(_aliases_))

    def __init__(self, *args, **kwargs):
        # GeneratingCommand.__init__(self, *args, **kwargs)
        # BaseURL.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)

    async def target(self, event, pipeline):
        while self.count > 0:
            response = requests.request(self.method, self.url)
            # Define event data
            if response.headers.get("content-type").lower() == "application/json":
                try:
                    response_data = response.json()
                except Exception:
                    response_data = response.text
            else:
                response_data = response.text
            # ---
            yield Event(data={
                "time": time.time_ns(),
                "source": self.url,
                "request": {
                    "method": self.method,
                    "url": self.url,
                    "headers": dict(response.request.headers)
                },
                "response": {
                    "status": response.status_code,
                    "reason": response.reason,
                    "mime": {
                        "type": response.headers.get("content-type", None)
                    },
                    "headers": dict(response.headers),
                    "content": response_data
                }
            })
            # Wait
            if self.frequency > 0:
                await asyncio.sleep(self.frequency)
            # Decrease count
            self.count -= 1
