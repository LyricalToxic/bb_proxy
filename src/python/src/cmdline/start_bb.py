from core.bb.big_brother import BigBrother


async def _run(options):
    bbc = BigBrother()
    await bbc.run(options)
