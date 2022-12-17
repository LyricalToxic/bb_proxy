from typing import Optional

from mitmproxy.options import Options

from core.bb_innards.base_big_brother import BaseBigBrother
from core.bb_innards.storage.bb_storage_keeper import BBStorageKeeper
from core.communication.server import BBServer
from settings import SECRET_KEY
from utils.constans import ADDRESS


class CommunicativeBigBrother(BaseBigBrother):

    def __init__(self, storage_keeper: BBStorageKeeper) -> None:
        super().__init__(storage_keeper)
        self._bbserver: Optional[BBServer] = None

    async def run(self, options: Options) -> None:
        await super().run(options)

    def setup_bbserver(self) -> None:
        self.logger.info("Listen bbserver %s", ADDRESS)
        self._bbserver = BBServer(ADDRESS, SECRET_KEY)
        self._bbserver.start()
        self._bbserver.read_message(self._on_input_received)

    def _on_input_received(self, message: str) -> None:
        self.logger.info(message)
