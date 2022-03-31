from core.bb.base_big_brother import BaseBigBrother
from core.comunication.server import BBServer
from settings import SECRET_KEY
from utils.types_.constans import ADDRESS


class CommunicativeBigBrother(BaseBigBrother):

    def __init__(self):
        super().__init__()
        self._bbserver = None

    def run(self, options):
        # bb_server_thread = Thread(target=self.setup_bbserver, name="@BBServer")
        # bb_server_thread.start()
        # bb_server_thread.join()
        super().run(options)


    def setup_bbserver(self):
        self.logger.info("Listen bbserver %s", ADDRESS)
        self._bbserver = BBServer(ADDRESS, SECRET_KEY)
        self._bbserver.start()
        self._bbserver.read_message(self._on_input_received)

    def _on_input_received(self, message):
        self.logger.info(message)
