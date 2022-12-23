from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects.mysql import VARCHAR, TEXT

from database.models.base import Base
from database.models.mixins import MysqlPrimaryKeyMixin, MysqlTimestampsMixin


class Comrade(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = "comrades"

    name = Column("name", VARCHAR(255), index=False, nullable=True)
    username = Column("username", VARCHAR(255), index=False, nullable=False)
    password = Column("password", TEXT, index=False, nullable=False)
    description = Column("description", TEXT, index=False, nullable=True)

    __table_args__ = (
        UniqueConstraint(username),
    )
