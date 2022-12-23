from abc import ABCMeta, abstractmethod

from database.data_access.stmt_collections import BaseStmtCollection
from database.models.base import Base


class BaseDBCA(metaclass=ABCMeta):
    @property
    @abstractmethod
    def dbms(self) -> str:
        pass
    @property
    @abstractmethod
    def comrades(self) -> type(Base):
        pass

    @property
    @abstractmethod
    def proxy_comrades(self) -> type(Base):
        pass

    @property
    @abstractmethod
    def proxy_credentials(self) -> type(Base):
        pass

    @property
    @abstractmethod
    def statistics(self) -> type(Base):
        pass

    @property
    @abstractmethod
    def stmt_collection(self) -> BaseStmtCollection:
        pass
