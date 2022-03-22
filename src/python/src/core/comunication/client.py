from logging import getLogger
from multiprocessing.connection import Client


class BBClient(object):

    def __init__(self, address, secret_key):
        self.address = address
        self.__secret_key = secret_key
        self.logger = getLogger(BBClient.__name__)

    def communicate(self, args):
        with Client(self.address, authkey=self.__secret_key) as conn:
            conn.send(args)

    def ping(self):
        try:
            _ = Client(self.address, authkey=self.__secret_key)
        except ConnectionRefusedError:
            return False
        else:
            return True
