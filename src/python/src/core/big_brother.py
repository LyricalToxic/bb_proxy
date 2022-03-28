import asyncio
from logging import getLogger
from threading import Thread
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from core.addons.dynamic_upstream_addon import DynamicUpstreamAddon
from core.bb_storage import BBStorage
from core.comunication.server import BBServer
from database.connection import async_engine
from database.models.bb import ProxyComradeLimit, Comrade, ProxyCredential
from exceptions import InvalidProxyError
from settings import LISTEN_PORT, SECRET_KEY
from utils.project import load_default_proxy
from utils.project.password_hashing import hash_password
from utils.types_.constans import LISTEN_HOST, ADDRESS


class BigBrother(object):

    def __init__(self):
        self._bbserver = None
        self.logger = getLogger(BigBrother.__name__)
        self.local_storage = BBStorage()
        self.engine = async_engine

    async def run(self, options):
        mp_thread = Thread(target=self.setup_mitmproxy, args=(options,), name="@MitmProxy")
        mp_thread.start()

        # self.setup_bbserver()

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

    async def get_proxy_spec(self):
        connection = await async_engine.connect()
        await connection.execute()
        await connection.close()

    async def get_proxy_zone(self, username, password):
        identifier = self._get_proxy_zone_from_local(username, password)
        if identifier:
            return identifier
        else:
            identifier = await self._get_proxy_zone_from_database(username, password)

    async def _get_proxy_zone_from_database(self, username, password):
        async with async_engine.connect() as connection:
            await connection.execute()

    def build_select_comrade_proxy_limits_stmt(self, username, password):
        password_hash = hash_password(password)
        joined_stmt = ProxyComradeLimit.__table__ \
            .join(Comrade, Comrade.id == ProxyComradeLimit.comrade_id) \
            .join(ProxyCredential, ProxyCredential.id == ProxyComradeLimit.proxy_credential_id)

    def _get_proxy_zone_from_local(self, username, password):
        return self.local_storage.authenticate_comrade(username, password)

    def get_proxy_auth(self, address):
        return None

    def shoutdown(self, signal, frame):
        self.logger.warning("SIGNAL %s", signal)
        # master.shutdown()
