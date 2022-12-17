from asyncio import Task
from copy import deepcopy
from logging import getLogger, Logger
from typing import Optional

from mitmproxy.connection import Address
from sqlalchemy.engine import Row

from core.bb_innards.storage.bb_storage import BBStorage
from utils.containers import ProxyCredential, ComradeLimits, ComradeCredential, Comrade, ComradeStats, ProxySpec
from utils.project.func.password_hashing import decrypt_password
from utils.project.func.proxy_spec_factory import proxy_spec_factory
from utils.types import Identifier


class BBStorageKeeper(object):

    def __init__(self, storage: BBStorage, **kwargs: dict):
        self.__storage: BBStorage = storage
        self.logger: Logger = getLogger(BBStorageKeeper.__class__.__name__)

    def is_bandwidth_exceed(self, identifier: Identifier) -> bool:
        comrade = self.__storage.get(identifier)

        if not comrade.limits.is_traffic_limit_set:
            return False
        else:
            is_usage_exceed = comrade.limits.traffic_bandwidth_b <= comrade.stats.traffic_usage.total
            return is_usage_exceed

    def release_peer_thread(self, identifier: Identifier, client_address: Address):
        comrade = self.__storage.get(identifier)
        comrade.stats.thread_peers_reserved.remove(str(client_address))

    def reserve_peer_thread(self, identifier: Identifier, client_address: Address):
        comrade = self.__storage.get(identifier)
        comrade.stats.thread_peers_reserved.add(str(client_address))

    def is_thread_limit_exceed(self, identifier: Identifier) -> bool:
        comrade = self.__storage.get(identifier)
        if not comrade.limits.is_threads_limit_set:
            return False
        else:
            thread_peers_reserved = comrade.stats.thread_peers_reserved
            threads_threshold = comrade.limits.threads_threshold
            is_threads_threshold_exceed = threads_threshold < len(thread_peers_reserved) + 1
            return is_threads_threshold_exceed

    def add_traffic_usage(
            self, identifier: Identifier, upload: Optional[int] = None, download: Optional[int] = None
    ) -> None:
        comrade = self.__storage.get(identifier)
        if isinstance(upload, int):
            comrade.stats.traffic_usage.session_upload += upload
            comrade.stats.traffic_usage.last_interval_upload += upload
        if isinstance(download, int):
            comrade.stats.traffic_usage.session_download += download
            comrade.stats.traffic_usage.last_interval_download += download

    def is_comrade_authenticated(self, identifier: Identifier, password: str) -> bool:
        comrade = self.__storage.get(identifier)
        is_password_matched = comrade.credential.password == password
        return is_password_matched

    def add_comrade(self, comrade_data: Row) -> Identifier:
        comrade = self._build_comrade(comrade_data)
        return self.__storage.add(comrade)

    def _build_comrade(self, comrade_data: Row) -> Comrade:
        comrade_username, comrade_password = comrade_data.username, decrypt_password(comrade_data.password)

        proxy_username, proxy_password = comrade_data.proxy_username, decrypt_password(comrade_data.proxy_password)

        proxy_cred = ProxyCredential(credential=(proxy_username, proxy_password))
        proxy_limit = ComradeLimits(
            is_traffic_limit_set=comrade_data.bandwidth_limit_b >= 0,
            is_threads_limit_set=comrade_data.concurrency_threads_limit >= 0,
            traffic_bandwidth_b=max(comrade_data.bandwidth_limit_b - comrade_data.used_bandwidth_b, 0),
            threads_threshold=comrade_data.concurrency_threads_limit
        )
        proxy_spec = proxy_spec_factory(
            proxy_type=comrade_data.type,
            host=comrade_data.host,
            port=comrade_data.port,
            credential=proxy_cred,
            protocol=comrade_data.protocol,
            record_id=comrade_data.id,
            rotate_strategy=comrade_data.rotate_strategy
        )
        comrade_cred = ComradeCredential(
            username=comrade_username,
            password=comrade_password
        )
        comrade = Comrade(
            limits=proxy_limit,
            proxy_specs=proxy_spec,
            credential=comrade_cred,
        )
        return comrade

    def indentify_comrade(self, username: str) -> Identifier:
        return self.__storage.indentify_comrade(username)

    def get_comrade_stats(self, identifier: Identifier) -> ComradeStats:
        comrade = self.__storage.get(identifier)
        if comrade:
            return deepcopy(comrade.stats)

    def purge_logging_task(self, identifier: Identifier) -> None:
        comrade = self.__storage.get(identifier)
        log_task = comrade.log_task
        if log_task:
            log_task.cancel()
        comrade.log_task = None

    def set_logging_task(self, task: Task, identifier: Identifier) -> None:
        comrade = self.__storage.get(identifier)
        if comrade:
            comrade.log_task = task

    def reset_traffic(self, identifier: Identifier) -> None:
        comrade = self.__storage.get(identifier)
        if comrade:
            comrade.stats.reset_last_interval()

    def get_comrade_proxy_spec(self, identifier: Identifier) -> ProxySpec:
        comrade = self.__storage.get(identifier)
        if comrade:
            return comrade.proxy_specs

    def get_identifiers(self) -> list[Identifier]:
        return list(self.__storage.comrade_identifiers.values())

    def remove_comrade(self, identifier: Identifier) -> None:
        self.__storage.remove_comrade(identifier)

    def is_comrade_proxy_exceed(self, identifier: Identifier) -> bool:
        comrade = self.__storage.get(identifier)
        if comrade:
            is_exceed = not comrade.limits.is_traffic_limit_set or \
                        comrade.stats.traffic_usage.total < comrade.limits.traffic_bandwidth_b
            return is_exceed
        else:
            return True
