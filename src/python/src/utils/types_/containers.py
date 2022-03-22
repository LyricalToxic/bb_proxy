import base64
import logging
from dataclasses import dataclass, field
from typing import Optional, Literal

from utils.types_.constans import MiB


@dataclass()
class ProxyLimits(object):
    bandwidth: MiB
    threads: int


@dataclass(init=False)
class ProxyCredential(object):
    username: str
    password: str

    def __init__(self, credential: Optional[str] = None):
        if credential is not None and len(credential.split(":")) == 2:
            self.username, self.password = credential.split(":")
        else:
            logging.warning("Expected credential format: <USERNAME>:<PASSWORD>, but got %s", credential)

    @property
    def basic_token(self):
        cred = base64.b64encode(f"{self.username}:{self.password}".encode("utf-8"))
        return f"Basic {cred}"


@dataclass()
class ProxySpec(object):
    host: str
    port: int
    protocol: Literal["http", "https"] = field(default="https")
    credential: ProxyCredential = field(default_factory=ProxyCredential)
    limits: ProxyLimits = field(default_factory=ProxyLimits)

    @property
    def shortened_url(self):
        return f"{self.protocol}://{self.address}"

    @property
    def full_url(self):
        return f"{self.shortened_url}@{self.credential.username}:{self.credential.password}"

    @property
    def upstream_mode(self):
        return f"upstream:{self.shortened_url}"

    @property
    def address(self):
        return f"{self.host}:{self.port}"


__all__ = [
    "ProxySpec",
    "ProxyCredential",
    "ProxyLimits",
]
