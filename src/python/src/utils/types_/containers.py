import logging
import random
from dataclasses import dataclass, field
from threading import RLock
from typing import Optional, Literal, Union

from utils.project.proxy_authorization import encode_proxy_auth_header
from utils.project.rotate_strategy import RotateStrategy
from utils.types_.constans import MiB, BYTE


@dataclass()
class ProxyLimits(object):
    bandwidth: MiB
    threads: int


@dataclass()
class ProxyUsage(object):
    previous_traffic: BYTE = field(default=0)
    upload_traffic: BYTE = field(default=0)
    download_traffic: BYTE = field(default=0)
    threads: int = field(default=0)
    __lock: RLock = RLock()

    def reserve_thread(self):
        with self.__lock:
            self.threads += 1

    def release_thread(self):
        with self.__lock:
            self.threads = max(0, self.threads - 1)

    def inc_upload_traffic(self, value):
        with self.__lock:
            self.upload_traffic += value

    def inc_download_traffic(self, value):
        with self.__lock:
            self.download_traffic += value

    @property
    def total_traffic(self):
        with self.__lock:
            return self.previous_traffic + self.upload_traffic + self.download_traffic


@dataclass(init=False)
class ProxyCredential(object):
    username: str
    password: str
    __lock: RLock = RLock()

    def __init__(self, credential: Optional[Union[str, list, tuple]] = None):
        with self.__lock:
            if isinstance(credential, str) and len(credential.split(":")) == 2:
                self.username, self.password = credential.split(":")
            elif isinstance(credential, (list, tuple)) and len(credential) == 2:
                self.username, self.password = credential
            elif credential is not None:
                logging.warning("Expected credential format: <USERNAME>:<PASSWORD>, but got %s", credential)

    @property
    def basic_token(self):
        with self.__lock:
            return encode_proxy_auth_header(self.username, self.password)


@dataclass()
class ProxySpec(object):
    host: str
    port: int
    protocol: Literal["http", "https"] = field(default="https")
    credential: ProxyCredential = field(default_factory=ProxyCredential)
    limits: ProxyLimits = field(default_factory=ProxyLimits)
    record_id: Optional[int] = field(default=None)
    rotate_strategy: int = field(default=RotateStrategy.DEFAULT)
    __lock: RLock = RLock()

    @property
    def shortened_url(self):
        with self.__lock:
            return f"{self.protocol}://{self.host}:{self.port}"

    @property
    def full_url(self):
        with self.__lock:
            return f"{self.shortened_url}@{self.credential.username}:{self.credential.password}"

    @property
    def upstream_mode(self):
        with self.__lock:
            return f"upstream:{self.shortened_url}"

    @property
    def address(self):
        with self.__lock:
            return (self.host, self.port)

    def rotate(self):
        with self.__lock:
            pass


@dataclass()
class GeoSerf(ProxySpec):
    standard_rotate_interval: int = field(default=1)
    __lock: RLock = RLock()

    def rotate(self):
        with self.__lock:
            if self.rotate_strategy == RotateStrategy.FORCE_ROTATE:
                username = self.credential.username.split("-")
                self.credential.username = f"{username[0]}-{random.randint(1, 10 ** 9)}"
            if self.rotate_strategy == RotateStrategy.NO_ROTATE:
                pass


__all__ = [
    "ProxySpec",
    "ProxyCredential",
    "ProxyLimits",
    "ProxyUsage",
    "GeoSerf"
]
