import datetime

from sqlalchemy import text, and_, select, update, insert
from sqlalchemy.sql import Executable

from database.data_access.stmt_collections import BaseStmtCollection
from database.models.sqlite import ProxyComrade, Comrade, ProxyCredential, Statistic
from utils.containers import ComradeStats, ProxySpec
from utils.project.enums import ProxyStates
from utils.project.enums.state_logging_triggers import LogTrigger


class SqliteStmtCollection(BaseStmtCollection):

    def build_init_query(self):
        return text("SELECT 1;")

    def build_select_comrade_proxy_query(self, username: str) -> Executable:
        joined_stmt = ProxyComrade.__table__ \
            .join(Comrade, Comrade.id == ProxyComrade.comrade_id) \
            .join(ProxyCredential, ProxyCredential.id == ProxyComrade.proxy_credential_id)
        select_stmt = select([
            ProxyComrade.id,
            ProxyComrade.comrade_id,
            ProxyComrade.proxy_credential_id,
            ProxyComrade.bandwidth_limit_b,
            ProxyComrade.concurrency_threads_limit,
            ProxyComrade.used_bandwidth_b,
            ProxyComrade.rotate_strategy,
            Comrade.username,
            Comrade.password,
            ProxyCredential.type,
            ProxyCredential.protocol,
            ProxyCredential.host,
            ProxyCredential.port,
            ProxyCredential.username.label("proxy_username"),
            ProxyCredential.password.label("proxy_password"),
            ProxyCredential.options,
        ]).where(
            and_(
                Comrade.username == username,
                ProxyComrade.status == ProxyStates.AVAILABLE,
            )
        ).select_from(joined_stmt)
        return select_stmt

    def build_update_proxy_comrade_query(self, id_: int, values: dict) -> Executable:
        update_stmt = update(ProxyComrade).values(values).where(ProxyComrade.id == id_)
        return update_stmt

    def build_statistic_insert_query(self, stats: ComradeStats, proxy_spec: ProxySpec,
                                     trigger: LogTrigger) -> Executable:
        insert_stmt = insert(Statistic).values({
            Statistic.proxy_comrade_limit_id: proxy_spec.record_id,
            Statistic.from_timestamp: stats.last_reset_timestamp,
            Statistic.to_timestamp: datetime.datetime.now(),
            Statistic.trigger: trigger.name,
            Statistic.upload_traffic_bytes: stats.traffic_usage.last_interval_upload,
            Statistic.download_traffic_bytes: stats.traffic_usage.last_interval_download,
            Statistic.total_traffic_bytes: stats.traffic_usage.interval_total,
        }).prefix_with("OR IGNORE")
        return insert_stmt
