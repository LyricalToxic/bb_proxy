import asyncio
import signal
from logging import getLogger, Logger
from types import FrameType
from typing import Union, Any

from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from core.bb_innards.storage.bb_storage_keeper import BBStorageKeeper
from core.mod_core_lib.proxy_server_mod_addon import ProxyServerModAddon
from exceptions import InvalidProxyError
from settings import LISTEN_PORT
from utils.constans import LISTEN_HOST
from utils.project.func.default_proxy import load_proxy_stub
from utils.project.func.paths import get_root_path


class BaseBigBrother(object):
    _master: DumpMaster
    _logger: Logger
    _storage_keeper: BBStorageKeeper
    _mimtproxy_event_loop: asyncio.AbstractEventLoop

    def __init__(self, storage_keeper: BBStorageKeeper) -> None:
        super().__init__()
        self._logger = getLogger(BaseBigBrother.__name__)
        self._storage_keeper = storage_keeper
        self._mimtproxy_event_loop = asyncio.get_event_loop()

    async def run(self) -> None:
        self._connect_signals()
        await self._before_setup()
        await self._setup_mitmproxy()
        await self._after_setup()

    def _connect_signals(self) -> None:
        try:
            signal.signal(signal.SIGINT, self._graceful_shutdown)
            signal.signal(signal.SIGTERM, self._graceful_shutdown)
            signal.signal(signal.SIGKILL, self._graceful_shutdown)
        except (AttributeError, OSError) as e:
            self._logger.debug(e)

    async def _before_setup(self) -> None:
        self._logger.info("BEFORE SETUP MITMPROXY")

    async def _after_setup(self) -> None:
        self._logger.info("AFTER SETUP MITMPROXY")

    def _graceful_shutdown(self, signal: Union[int, signal.Signals], frame: FrameType) -> None:
        asyncio.run_coroutine_threadsafe(self._before_shutdown(), self._mimtproxy_event_loop).add_done_callback(
            self._shutdown
        )

    async def _before_shutdown(self) -> None:
        self._logger.info("BEFORE SHUTDOWN MITMPROXY")

    def _shutdown(self, _: Any) -> None:
        self._master.shutdown()
        self._mimtproxy_event_loop.stop()

    async def _setup_mitmproxy(self) -> None:
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
                mode=[proxy_spec.upstream_mode],
                ignore_hosts=[".+"],
                confdir=str(get_root_path().joinpath("data", "certs")),
            )
            self._master = self._setup_dump_master(dump_master_opts)
            await self._master.run()

    def _setup_dump_master(self, dump_master_opts: Options) -> DumpMaster:
        master = DumpMaster(dump_master_opts)
        self._add_addons(master)
        master.options.update(connection_strategy="lazy")
        master.options.update(block_global=False)
        return master

    def _add_addons(self, master: DumpMaster) -> None:
        proxy_server = master.addons.get("proxyserver")
        proxy_server_chain_index = master.addons.chain.index(proxy_server)
        master.addons.remove(proxy_server)

        proxy_server_mod = ProxyServerModAddon(self)
        master.addons.register(proxy_server_mod)
        master.addons.chain.insert(proxy_server_chain_index, proxy_server_mod)
