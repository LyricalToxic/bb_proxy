import asyncio


from core.bb.big_brother import BigBrother


async def main(options):
    bbc = BigBrother()
    await bbc.run(options)


def _run(options):
    asyncio.get_event_loop().run_until_complete(main(options))
