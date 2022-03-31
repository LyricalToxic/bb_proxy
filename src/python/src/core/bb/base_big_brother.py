import asyncio
import os
import signal
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from threading import Thread, Event
from core.bb.bb_storage import BBStorage
from exceptions import InvalidProxyError
from settings import LISTEN_PORT
from utils.project.default_proxy import load_proxy_stub
from utils.types_.constans import LISTEN_HOST
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
from core.addons.dynamic_upstream_addon import DynamicUpstreamAddon


class BaseBigBrother(object):

    def __init__(self):
        super().__init__()
        self.logger = getLogger(BaseBigBrother.__name__)
        self._local_storage = BBStorage()
        self._master = None
        self._mimtproxy_event_loop = asyncio.get_event_loop()

    def run(self, options):
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
        self.setup_mitmproxy(options)

    def shutdown(self, signal, frame):
        asyncio.run_coroutine_threadsafe(self.before_shutdown(), self._mimtproxy_event_loop)
        # self.logger.info("%s, %s", signal, frame)

    async def before_shutdown(self):
        await asyncio.sleep(0)

    def setup_mitmproxy(self, options):
        asyncio.set_event_loop(self._mimtproxy_event_loop)
        proxy_spec = load_proxy_stub()

        if not proxy_spec:
            raise InvalidProxyError(
                "Cannot find default proxy."
                "To produce proxy use cmd options, env variables or database."
            )
        else:
            dump_master_opts = Options(
                listen_host=LISTEN_HOST,
                listen_port=LISTEN_PORT,
                mode=proxy_spec.upstream_mode,
                ssl_insecure=True,
                upstream_cert=False,
            )
            self._master = DumpMaster(dump_master_opts)
            self._master.addons.add(DynamicUpstreamAddon(self))
            self._master.options.update(connection_strategy="lazy")
            self._master.run()

    def get_comrade_proxy_spec(self, identifier):
        pass

    async def authenticate_comrade(self, username, password):
        pass
