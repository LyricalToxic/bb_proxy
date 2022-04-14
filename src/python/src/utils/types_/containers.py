import datetime
import logging
import random
from asyncio import Task
from dataclasses import dataclass, field
from threading import RLock
from typing import Optional, Literal, Union

from settings import STATISTIC_LOGGING_TIME_TRIGGER
from utils.project.enums.rotate_strategies import RotateStrategies
from utils.project.proxy_authorization import encode_proxy_auth_header
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
    total_requests: int = field(default=0)
    _from_timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    _logging_trigger: int = STATISTIC_LOGGING_TIME_TRIGGER
    _logging_task: Optional[Task] = field(default=None)
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

    def inc_total_requests(self):
        with self.__lock:
            self.total_requests += 1

    @property
    def total_traffic(self):
        with self.__lock:
            return self.previous_traffic + self.upload_traffic + self.download_traffic

    def reset_traffic(self):
        with self.__lock:
            self.previous_traffic = self.total_traffic
            self.upload_traffic = 0
            self.download_traffic = 0
            self.total_requests = 0
            self._from_timestamp = datetime.datetime.now()


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
    rotate_strategy: int = field(default=RotateStrategies.DEFAULT)
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
            return self.host, self.port

    def rotate(self):
        with self.__lock:
            pass


@dataclass()
class GeoSerf(ProxySpec):
    standard_rotate_interval: int = field(default=1)
    __lock: RLock = RLock()

    def rotate(self):
        with self.__lock:
            if self.rotate_strategy == RotateStrategies.FORCE_ROTATE:
                username = self.credential.username.split("-")
                self.credential.username = f"{username[0]}-{random.randint(1, 10 ** 9)}"
            if self.rotate_strategy == RotateStrategies.NO_ROTATE:
                pass


@dataclass()
class BrightDataDatacenter(ProxySpec):
    __lock: RLock = RLock()

    def rotate(self):
        with self.__lock:
            if self.rotate_strategy == RotateStrategies.FORCE_ROTATE:
                pass
            if self.rotate_strategy == RotateStrategies.NO_ROTATE:
                pass


__all__ = [
    "ProxySpec",
    "ProxyCredential",
    "ProxyLimits",
    "ProxyUsage",
    "GeoSerf",
    "BrightDataDatacenter"
]
