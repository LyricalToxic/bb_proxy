import logging
import random
from asyncio import Task
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Literal, Union

from utils.project.enums.rotate_strategies import RotateStrategies
from utils.project.func.proxy_authorization import encode_proxy_auth_header


@dataclass()
class BufferTrafficUsageBytes(object):
    upload: int = 0
    download: int = 0

    def reset(self):
        self.upload = 0
        self.download = 0


@dataclass()
class TrafficUsageBytes(object):
    last_interval_upload: int = 0
    last_interval_download: int = 0
    session_upload: int = 0
    session_download: int = 0

    @property
    def total(self):
        return self.session_upload + self.session_download

    @property
    def interval_total(self):
        return self.last_interval_upload + self.last_interval_download


@dataclass()
class ComradeStats(object):
    traffic_usage: TrafficUsageBytes = field(default_factory=TrafficUsageBytes)
    thread_peers_reserved: set = field(default_factory=set)
    last_reset_timestamp: datetime = field(default_factory=datetime.now)

    def reset_last_interval(self):
        self.traffic_usage.last_interval_upload = 0
        self.traffic_usage.last_interval_download = 0
        self.thread_peers_reserved = set()
        self.last_reset_timestamp = datetime.now()


@dataclass()
class ComradeLimits(object):
    is_traffic_limit_set: bool = False
    is_threads_limit_set: bool = False
    traffic_bandwidth_b: int = 0
    threads_threshold: int = 0


@dataclass()
class ComradeCredential(object):
    username: str
    password: str


@dataclass(init=False)
class ProxyCredential(object):
    username: str
    password: str

    def __init__(self, credential: Optional[Union[str, list, tuple]] = None):
        if isinstance(credential, str) and len(credential.split(":")) == 2:
            self.username, self.password = credential.split(":")
        elif isinstance(credential, (list, tuple)) and len(credential) == 2:
            self.username, self.password = credential
        elif credential is not None:
            logging.warning("Expected credential format: <USERNAME>:<PASSWORD>, but got %s", credential)

    @property
    def basic_token(self):
        return encode_proxy_auth_header(self.username, self.password)


@dataclass()
class ProxySpec(object):
    host: str
    port: int
    protocol: Literal["http", "https"] = field(default="https")
    credential: ProxyCredential = field(default_factory=ProxyCredential)
    record_id: Optional[int] = field(default=None)
    rotate_strategy: int = field(default=RotateStrategies.DEFAULT)

    @property
    def shortened_url(self):
        return f"{self.protocol}://{self.host}:{self.port}"

    @property
    def full_url(self):
        return f"{self.shortened_url}@{self.credential.username}:{self.credential.password}"

    @property
    def upstream_mode(self):
        return f"upstream:{self.shortened_url}"

    @property
    def address(self):
        return self.host, self.port

    def rotate(self):
        pass


@dataclass()
class GeoSerf(ProxySpec):
    standard_rotate_interval: int = field(default=1)

    def rotate(self):

        if self.rotate_strategy == RotateStrategies.FORCE_ROTATE:
            username = self.credential.username.split("-")
            self.credential.username = f"{username[0]}-{random.randint(1, 10 ** 9)}"
        if self.rotate_strategy == RotateStrategies.NO_ROTATE:
            pass


@dataclass()
class BrightDataDatacenter(ProxySpec):

    def rotate(self):

        if self.rotate_strategy == RotateStrategies.FORCE_ROTATE:
            pass
        if self.rotate_strategy == RotateStrategies.NO_ROTATE:
            pass


@dataclass()
class BrightDataResidential(ProxySpec):

    def rotate(self):

        if self.rotate_strategy == RotateStrategies.FORCE_ROTATE:
            pass
        if self.rotate_strategy == RotateStrategies.NO_ROTATE:
            pass


@dataclass()
class MetaComrade(object):
    comrade_identifier: Optional[int] = field(default=None)


@dataclass()
class Comrade(object):
    limits: ComradeLimits
    proxy_specs: ProxySpec
    credential: ComradeCredential
    log_task: Task = None
    stats: ComradeStats = field(default_factory=ComradeStats)
