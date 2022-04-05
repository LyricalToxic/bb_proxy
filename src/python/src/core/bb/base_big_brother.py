import asyncio
import signal
from logging import getLogger
from core.bb.storage.bb_storage import BBStorage
from core.modified_mitmproxy.modified_dump_muster import ModifiedDumpMuster
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

    async def run(self, options):
        self.connect_signals()
        await self.before_setup_mitmproxy()
        await self.setup_mitmproxy(options)

    def connect_signals(self):
        try:
            signal.signal(signal.SIGTERM, self.shutdown)
            signal.signal(signal.SIGINT, self.shutdown)
            signal.signal(signal.SIGKILL, self.shutdown)
        except Exception as e:
            pass

    async def before_setup_mitmproxy(self):
        self.logger.info("BEFORE SETUP MITMPROXY")

    def shutdown(self, signal, frame):
        asyncio.run_coroutine_threadsafe(self.before_shutdown(), self._mimtproxy_event_loop)
        # self.logger.info("%s, %s", signal, frame)

    async def before_shutdown(self):
        await asyncio.sleep(0)

    async def setup_mitmproxy(self, options):
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
            self._master = ModifiedDumpMuster(dump_master_opts)
            self._master.addons.add(DynamicUpstreamAddon(self))
            self._master.options.update(connection_strategy="lazy")
            self._master.run()

    def get_comrade_proxy_spec(self, identifier):
        pass

    async def authenticate_comrade(self, username, password):
        pass
