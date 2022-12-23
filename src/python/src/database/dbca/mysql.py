from database.data_access.stmt_collections import BaseStmtCollection, MySQLStmtCollection
from database.dbca import BaseDBCA
from database.models.base import Base
from database.models.mysql import Comrade, ProxyComrade, ProxyCredential, Statistic


class MySQLDBCA(BaseDBCA):

    @property
    def dbms(self) -> str:
        return "mysql"

    @property
    def comrades(self) -> type(Base):
        return Comrade

    @property
    def proxy_comrades(self) -> type(Base):
        return ProxyComrade

    @property
    def proxy_credentials(self) -> type(Base):
        return ProxyCredential

    @property
    def statistics(self) -> type(Base):
        return Statistic

    @property
    def stmt_collection(self) -> BaseStmtCollection:
        return MySQLStmtCollection(self)
