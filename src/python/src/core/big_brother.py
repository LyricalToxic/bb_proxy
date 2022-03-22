import asyncio
import signal
from functools import partial
from logging import getLogger
from threading import Thread
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from core.addons.dynamic_upstream_addon import DynamicUpstreamAddon
from core.comunication.server import BBServer
from core.storage.threadsafe_storage import ThreadSafeStorage
from exceptions import InvalidProxyError
from settings import LISTEN_PORT, SECRET_KEY
from utils.project import load_default_proxy
from utils.types_.constans import LISTEN_HOST, ADDRESS


class BigBrother(object):

    def __init__(self):
        self._bbserver = None
        self.logger = getLogger(BigBrother.__name__)
        self.storage = dict()

    async def run(self, options):
        mp_thread = Thread(target=self.setup_mitmproxy, args=(options,))
        mp_thread.start()

        self.setup_bbserver()

    def setup_bbserver(self):
        self.logger.info("Listen bbserver %s", ADDRESS)
        self._bbserver = BBServer(ADDRESS, SECRET_KEY)
        self._bbserver.start()
        self._bbserver.read_message(self._on_input_received)

    def _on_input_received(self, message):
        self.logger.info(message)

    def setup_mitmproxy(self, options):
        asyncio.set_event_loop(asyncio.new_event_loop())
        proxy_spec = load_default_proxy(options)

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
                upstream_cert=False
            )
            master = DumpMaster(dump_master_opts)
            master.addons.add(DynamicUpstreamAddon(self))
            master.run()

    def get_proxy_spec(self):
        return ""

    def get_proxy_auth(self, address):
        return None

    def shoutdown(self,  signal, frame):
        self.logger.warning("SIGNAL %s", signal)
        # master.shutdown()
