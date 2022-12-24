from datetime import datetime

from sqlalchemy import insert
from sqlalchemy.sql import Executable

from database.data_access.stmt_collections import BaseStmtCollection
from utils.containers import ComradeStats, ProxySpec
from utils.project.enums.state_logging_triggers import LogTrigger


class SqliteStmtCollection(BaseStmtCollection):
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
        }).prefix_with("OR IGNORE")
        return insert_stmt

