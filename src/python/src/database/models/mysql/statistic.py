from sqlalchemy import Column, Index, text, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT, TIMESTAMP, VARCHAR, INTEGER

from database.models.base import Base
from database.models.mixins import MysqlPrimaryKeyMixin, MysqlTimestampsMixin


class Statistic(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "statistics"

    proxy_comrade_limit_id = Column("proxy_comrade_limit_id", BIGINT(unsigned=True), index=True, nullable=False)

    from_timestamp = Column("from_timestamp", TIMESTAMP, index=True, nullable=False,
                            server_default=text("CURRENT_TIMESTAMP"))
    to_timestamp = Column("to_timestamp", TIMESTAMP, index=True, nullable=False,
                          server_default=text("CURRENT_TIMESTAMP"))
    trigger = Column("trigger", VARCHAR(255), index=False, nullable=False)

    number_of_requests = Column("number_of_requests", INTEGER(unsigned=True), index=False, nullable=False,
                                server_default=text("0"))
    upload_traffic_bytes = Column("upload_traffic_bytes", BIGINT(unsigned=True), index=False, nullable=False,
                                  server_default=text("0"))
    number_of_responses = Column("number_of_responses", INTEGER(unsigned=True), index=False, nullable=False,
                                 server_default=text("0"))
    download_traffic_bytes = Column("download_traffic_bytes", BIGINT(unsigned=True), index=False, nullable=False,
                                    server_default=text("0"))

    total_traffic_bytes = Column("total_traffic_bytes", BIGINT(unsigned=True), index=False, nullable=False,
                                 server_default=text("0"))

    __table_args__ = (
        Index(None, from_timestamp, to_timestamp, trigger),
        UniqueConstraint(proxy_comrade_limit_id, from_timestamp, to_timestamp, trigger),
    )
