from abc import ABCMeta
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import text, select, update, insert, and_
from sqlalchemy.sql import Executable

from utils.containers import ProxySpec, ComradeStats
from utils.project.enums import ProxyStates
from utils.project.enums.state_logging_triggers import LogTrigger

if TYPE_CHECKING:
    from database.dbca import BaseDBCA


class BaseStmtCollection(metaclass=ABCMeta):
    def __init__(self, dbca: "BaseDBCA"):
        self._dbca: "BaseDBCA" = dbca

    def build_init_query(self) -> str:
        return text("SELECT 1;")

    def build_select_comrade_proxy_query(self, username: str) -> Executable:
        joined_stmt = self._dbca.proxy_comrades.__table__ \
            .join(self._dbca.comrades, self._dbca.comrades.id == self._dbca.proxy_comrades.comrade_id) \
            .join(self._dbca.proxy_credentials,
                  self._dbca.proxy_credentials.id == self._dbca.proxy_comrades.proxy_credential_id)
        select_stmt = select([
            self._dbca.proxy_comrades.id,
            self._dbca.proxy_comrades.comrade_id,
            self._dbca.proxy_comrades.proxy_credential_id,
            self._dbca.proxy_comrades.bandwidth_limit_b,
            self._dbca.proxy_comrades.concurrency_threads_limit,
            self._dbca.proxy_comrades.used_bandwidth_b,
            self._dbca.proxy_comrades.rotate_strategy,
            self._dbca.comrades.username,
            self._dbca.comrades.password,
            self._dbca.proxy_credentials.type,
            self._dbca.proxy_credentials.protocol,
            self._dbca.proxy_credentials.host,
            self._dbca.proxy_credentials.port,
            self._dbca.proxy_credentials.username.label("proxy_username"),
            self._dbca.proxy_credentials.password.label("proxy_password"),
            self._dbca.proxy_credentials.options,
        ]).where(
            and_(
                self._dbca.comrades.username == username,
                self._dbca.proxy_comrades.status == ProxyStates.AVAILABLE,
            )
        ).select_from(joined_stmt)
        return select_stmt

    def build_update_proxy_comrade_query(self, id_: int, values: dict) -> Executable:
        update_stmt = update(self._dbca.proxy_comrades).values(values).where(self._dbca.proxy_comrades.id == id_)
        return update_stmt

    def build_statistic_insert_query(
            self, stats: ComradeStats, proxy_spec: ProxySpec, trigger: LogTrigger
    ) -> Executable:
        insert_stmt = insert(self._dbca.statistics).values({
            self._dbca.statistics.proxy_comrade_limit_id: proxy_spec.record_id,
            self._dbca.statistics.from_timestamp: stats.last_reset_timestamp,
            self._dbca.statistics.to_timestamp: datetime.now(),
            self._dbca.statistics.trigger: trigger.name,
            self._dbca.statistics.upload_traffic_bytes: stats.traffic_usage.last_interval_upload,
            self._dbca.statistics.download_traffic_bytes: stats.traffic_usage.last_interval_download,
            self._dbca.statistics.total_traffic_bytes: stats.traffic_usage.interval_total,
        }).prefix_with("IGNORE")
        return insert_stmt
