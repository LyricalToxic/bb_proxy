from utils.containers import Comrade
from utils.types import Identifier


class _ComradeIdentifiers(dict):
    """
        Container for comrade credentials. Represents following format {(comrade_username, comrade_password):comrade_id}
        Used for type hinting.
    """


class _ProxySpecs(dict):
    """
        Container for {ProxySpec}. Represents following format {comrade_id:ProxySpec}
        Used for type hinting.
    """


class _ComradeUsage(dict):
    """
        Container for comrade proxy usage. Represents following format {comrade_id:ProxyUsage}
        Used for type hinting.
    """


class _Storage(dict):
    """
        Container for storage.
        Used for type hinting.
    """


class BBStorage(object):

    def __init__(self, **kwargs):
        self._storage: _Storage = _Storage()
        self._comrade_identifiers: _ComradeIdentifiers = _ComradeIdentifiers()

        self._stat_buffer = {}

    def indentify_comrade(self, username: str) -> Identifier:
        return next(
            (cid for c, cid in self._comrade_identifiers.items() if c[0] == username),
            None
        )

    def add(self, comrade: Comrade) -> Identifier:
        comrade_hash = self.add_comrade_identifier(comrade.credential.username, comrade.credential.password)
        self._storage[comrade_hash] = comrade
        return comrade_hash

    def get(self, identifier: Identifier) -> Comrade:
        return self._storage.get(identifier)

    def remove_comrade(self, identifier: Identifier) -> None:
        try:
            del self._storage[identifier]
        except Exception as e:
            pass

        try:
            cid_key = next((key for key, value in self._comrade_identifiers.items() if value == identifier), None)
            del self._comrade_identifiers[cid_key]
        except Exception as e:
            pass

    def add_comrade_identifier(self, comrade_username: str, comrade_password: str) -> Identifier:
        comrade_hash = f"{comrade_username}_{comrade_password}"
        self._comrade_identifiers.update({(comrade_username, comrade_password): comrade_hash})
        return Identifier(comrade_hash)

    @property
    def comrade_identifiers(self) -> _ComradeIdentifiers:
        return self._comrade_identifiers
