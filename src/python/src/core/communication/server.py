from logging import getLogger
from multiprocessing.connection import Listener


class BBServer(object):

    def __init__(self, address, secret_key):
        self.address = address
        self.__secret_key = secret_key
        self.listener = None
        self.is_running = False
        self.logger = getLogger(BBServer.__name__)
        self.logger.setLevel("INFO")
        self.is_worker = True

    def start(self):
        self._connect()

    def read_message(self, callback):
        self._read_messages(callback)

    def _read_messages(self, callback):
        with self.listener.accept() as connection:
            self.logger.debug("Accept new connection")
            while not connection.closed:
                try:
                    callback(connection.recv())
                except EOFError:
                    self.logger.debug("%s closed", connection)
                    break
        if self.is_worker:
            self._read_messages(callback)

    def _connect(self):
        if not self.is_running:
            self.listener = Listener(self.address, authkey=self.__secret_key)
            self.is_running = True
        else:
            self.logger.warning("Listener already running")
