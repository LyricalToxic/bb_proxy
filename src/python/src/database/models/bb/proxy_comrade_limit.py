from database.models.base import Base
from sqlalchemy import Column, INTEGER, text, Index, TIMESTAMP


class ProxyComradeLimit(Base):
    __tablename__ = "proxy_comrade_limits"

    id = Column("id", INTEGER, index=False, nullable=False, primary_key=True, autoincrement=True)
    proxy_credential_id = Column("proxy_credential_id", INTEGER, index=True, nullable=False)
    comrade_id = Column("comrade_id", INTEGER, index=True, nullable=False)

    bandwidth_limit_mb = Column("bandwidth_limit", INTEGER, index=False, nullable=False, server_default=text("1024"))
    concurrency_threads_limit = Column("concurrency_threads_limit", INTEGER, index=False, nullable=False,
                                       server_default=text("1"))

    status = Column("status", INTEGER, index=True, nullable=False, server_default=text("0"))
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at = Column(
        "updated_at",
        TIMESTAMP,
        nullable=False,
        index=True,
        unique=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        Index("proxy_credential_id", "comrade_id"),
        Index("bandwidth_limit_mb", "concurrency_threads_limit"),
    )
