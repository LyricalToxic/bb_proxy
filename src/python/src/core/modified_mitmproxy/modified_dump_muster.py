import asyncio
import sys
import traceback

from mitmproxy import hooks
from mitmproxy.tools.dump import DumpMaster


class ModifiedDumpMuster(DumpMaster):

    def run_loop(self, loop):
        self.start()
        asyncio.ensure_future(self.running())

        exc = None
        if not loop.is_running():
            try:
                loop.run_forever()
            except Exception as e:  # pragma: no cover
                exc = traceback.format_exc()
            finally:
                if not self.should_exit.is_set():  # pragma: no cover
                    self.shutdown()
                loop = asyncio.get_event_loop()
                tasks = asyncio.all_tasks(loop)
                for p in tasks:
                    p.cancel()
                loop.close()

            if exc:  # pragma: no cover
                print(exc, file=sys.stderr)
                print("mitmproxy has crashed!", file=sys.stderr)
                print("Please lodge a bug report at:", file=sys.stderr)
                print("\thttps://github.com/mitmproxy/mitmproxy/issues", file=sys.stderr)

    async def _shutdown(self):
        self.addons.trigger(hooks.DoneHook())
        self.should_exit.set()
        loop = asyncio.get_event_loop()
        loop.stop()

    def run(self):
        loop = asyncio.get_event_loop()
        self.run_loop(loop)
