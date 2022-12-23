from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects.mysql import MEDIUMINT, VARCHAR, TEXT

from database.models.base import Base
from database.models.mixins import MysqlPrimaryKeyMixin, MysqlTimestampsMixin


class ProxyCredential(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "proxy_credentials"

    type = Column("type", VARCHAR(255), index=True, nullable=False)
    protocol = Column("protocol", VARCHAR(255), index=False, nullable=False)
    host = Column("host", VARCHAR(255), index=False, nullable=False)
    port = Column("port", MEDIUMINT(unsigned=True), index=False, nullable=False)
    username = Column("username", VARCHAR(255), index=False, nullable=True)
    password = Column("password", TEXT, index=False, nullable=True)
    description = Column("description", TEXT, index=False, nullable=True)
    options = Column("options", TEXT, index=False, nullable=True)

    __table_args__ = (
        UniqueConstraint(host, port, username),
    )
