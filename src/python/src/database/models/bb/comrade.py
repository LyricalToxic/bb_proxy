from database.models.base import Base
from sqlalchemy import Column, INTEGER, VARCHAR, BINARY, TEXT, TIMESTAMP, text, UniqueConstraint


class Comrade(Base):
    __tablename__ = "comrades"

    id = Column("id", INTEGER, index=False, nullable=False, primary_key=True, autoincrement=True)

    name = Column("name", VARCHAR(255), index=False, nullable=True)
    username = Column("username", VARCHAR(255), index=False, nullable=False)
    password = Column("password", TEXT, index=False, nullable=False)
    description = Column("description", TEXT, index=False, nullable=True)

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
        UniqueConstraint("username", "password"),
    )
