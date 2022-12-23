from database.data_access.stmt_collections import SqliteStmtCollection
from database.dbca import BaseDBCA
from database.models.sqlite import (
    Comrade,
    ProxyComrade,
    ProxyCredential,
    Statistic
)


class SqliteDBCA(BaseDBCA):
    @property
    def dbms(self) -> str:
        return "sqlite"

    @property
    def comrades(self):
        return Comrade

    @property
    def proxy_comrades(self):
        return ProxyComrade

    @property
    def proxy_credentials(self):
        return ProxyCredential

    @property
    def statistics(self):
        return Statistic

    @property
    def stmt_collection(self):
        return SqliteStmtCollection(self)
