from sqlalchemy import Column, text, UniqueConstraint
from sqlalchemy.dialects.sqlite import INTEGER, TIMESTAMP, VARCHAR, TEXT

from database.models.base import Base


class ProxyCredential(Base):
    __tablename__ = "proxy_credentials"

    id = Column("id", INTEGER, index=False, nullable=False, primary_key=True, autoincrement=True)

    type = Column("type", VARCHAR(255), index=True, nullable=False)
    protocol = Column("protocol", VARCHAR(255), index=False, nullable=False)
    host = Column("host", VARCHAR(255), index=False, nullable=False)
    port = Column("port", INTEGER, index=False, nullable=False)
    username = Column("username", VARCHAR(255), index=False, nullable=True)
    password = Column("password", TEXT, index=False, nullable=True)
    description = Column("description", TEXT, index=False, nullable=True)
    options = Column("options", TEXT, index=False, nullable=True)

    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, index=True, server_default=text("CURRENT_TIMESTAMP"),
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
        UniqueConstraint(host, port, username),
    )
