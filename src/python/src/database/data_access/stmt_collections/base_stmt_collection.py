from abc import ABCMeta, abstractmethod

from sqlalchemy.sql import Executable

from utils.containers import ProxySpec, ComradeStats
from utils.project.enums.state_logging_triggers import LogTrigger


class BaseStmtCollection(metaclass=ABCMeta):

    @abstractmethod
    def build_init_query(self):
        pass

    @abstractmethod
    def build_select_comrade_proxy_query(self, username: str) -> Executable:
        pass

    @abstractmethod
    def build_update_proxy_comrade_query(self, id_: int, values: dict) -> Executable:
        pass

    @abstractmethod
    def build_statistic_insert_query(
            self, stats: ComradeStats, proxy_spec: ProxySpec, trigger: LogTrigger
    ) -> Executable:
        pass
