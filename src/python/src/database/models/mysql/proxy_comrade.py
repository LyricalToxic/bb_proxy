from sqlalchemy import Column, text, Index
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT

from database.models.base import Base
from database.models.mixins import MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlTimestampsMixin


class ProxyComrade(Base, MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlTimestampsMixin):
    __tablename__ = "proxy_comrades"

    proxy_credential_id = Column("proxy_credential_id", BIGINT(unsigned=True), index=True, nullable=False)
    comrade_id = Column("comrade_id", BIGINT(unsigned=True), index=True, nullable=False)

    bandwidth_limit_b = Column("bandwidth_limit_b", BIGINT, index=False, nullable=False,
                               server_default=text("1024"))
    concurrency_threads_limit = Column("concurrency_threads_limit", BIGINT, index=False, nullable=False,
                                       server_default=text("1"))

    used_bandwidth_b = Column("used_bandwidth_b", BIGINT(unsigned=True), index=False, nullable=False,
                              server_default=text("0"))
    rotate_strategy = Column("rotate_strategy", SMALLINT(unsigned=True), index=False, nullable=False,
                             server_default=text("0"))

    __table_args__ = (
        Index(None, proxy_credential_id, comrade_id),
        Index(None, bandwidth_limit_b, concurrency_threads_limit),
    )
