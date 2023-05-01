import asyncio
import os

from cmdline.start_bb import _run


def run_server():
    if os.name == "nt":
        async def wakeup():
            while True:
                await asyncio.sleep(0.2)

        asyncio.ensure_future(wakeup())
    asyncio.ensure_future(_run())
    asyncio.get_event_loop().run_forever()
