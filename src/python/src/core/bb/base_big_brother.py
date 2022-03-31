import asyncio
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
        self.mimtproxy_event_loop = None

    async def run(self, options):
        stop_event = Event()
        mp_thread = Thread(target=self.setup_mitmproxy, args=(options, stop_event), name="@MitmProxy")
        mp_thread.start()
        mp_thread.join()

    def shutdown(self, signal, frame):
        self.logger.info("%s, %s", signal, frame)

    def setup_mitmproxy(self, options, stop_event):
        loop = asyncio.new_event_loop()
        self.mimtproxy_event_loop = loop
        asyncio.set_event_loop(loop)
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
            master = DumpMaster(dump_master_opts)
            master.addons.add(DynamicUpstreamAddon(self))
            master.options.update(connection_strategy="lazy")
            try:
                master.run()
            except KeyboardInterrupt:
                master.shutdown()

    def get_comrade_proxy_spec(self, identifier):
        pass

    async def authenticate_comrade(self, username, password):
        pass
