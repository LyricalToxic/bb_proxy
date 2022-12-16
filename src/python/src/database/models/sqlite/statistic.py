from sqlalchemy import Column, Index, INTEGER, text, TIMESTAMP, VARCHAR, UniqueConstraint

from database.models.base import Base


class Statistic(Base):
    __tablename__ = "statistics"

    id = Column("id", INTEGER, index=False, nullable=False, primary_key=True, autoincrement=True)
    proxy_comrade_limit_id = Column("proxy_comrade_limit_id", INTEGER, index=True, nullable=False)

    from_timestamp = Column("from_timestamp", TIMESTAMP, index=True, nullable=False,
                            server_default=text("CURRENT_TIMESTAMP"))
    to_timestamp = Column("to_timestamp", TIMESTAMP, index=True, nullable=False,
                          server_default=text("CURRENT_TIMESTAMP"))
    trigger = Column("trigger", VARCHAR(255), index=False, nullable=False)

    number_of_requests = Column("number_of_requests", INTEGER, index=False, nullable=False, server_default=text("0"))
    upload_traffic_bytes = Column("upload_traffic_bytes", INTEGER, index=False, nullable=False,
                                  server_default=text("0"))
    number_of_responses = Column("number_of_responses", INTEGER, index=False, nullable=False, server_default=text("0"))
    download_traffic_bytes = Column("download_traffic_bytes", INTEGER, index=False, nullable=False,
                                    server_default=text("0"))

    total_traffic_bytes = Column("total_traffic_bytes", INTEGER, index=False, nullable=False, server_default=text("0"))

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
        Index("from_timestamp", "to_timestamp", "trigger"),
        UniqueConstraint("proxy_comrade_limit_id", "from_timestamp", "to_timestamp", "trigger"),
    )
