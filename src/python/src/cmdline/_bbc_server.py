import asyncio
import os
import sys
from argparse import ArgumentParser

from cmdline.start_bb import _run


def _parse_args(args):
    parser = ArgumentParser()
    subparser = parser.add_subparsers()
    start_parser = subparser.add_parser("start", help="Start big brother proxy gateway")
    start_parser.add_argument("--proxy_host", dest="proxy_host")
    start_parser.add_argument("--proxy_port", dest="proxy_port")
    start_parser.add_argument("--proxy_credential", dest="proxy_credential")
    start_parser.add_argument("--bandwidth", dest="bandwidth")
    start_parser.add_argument("--threads", dest="threads")
    start_parser.add_argument("--protocol", dest="protocol")
    start_parser.add_argument("--type", dest="proxy_type")
    start_parser.set_defaults(target=_run)
    return parser.parse_args(args)


def main():
    args = sys.argv[1:]
    parsed_args = _parse_args(args)

    if os.name == "nt":
        async def wakeup():
            while True:
                await asyncio.sleep(0.2)

        asyncio.ensure_future(wakeup())
    asyncio.ensure_future(_run(parsed_args))
    asyncio.get_event_loop().run_forever()
