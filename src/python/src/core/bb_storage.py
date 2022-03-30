from threading import Lock

from utils.project.password_hashing import decrypt_password
from utils.project.proxy_spec_factory import proxy_spec_factory

from utils.types_.containers import ProxyCredential, ProxyLimits, ProxyUsage


class _ComradeSpecs(dict):
    pass


class BBStorage(object):

    def __init__(self):
        self._local_lock = Lock()
        self._comrade_identifiers = dict()
        self._comrade_specs = _ComradeSpecs()
        self._comrade_usage = dict()

    def indentify_comrade(self, username):
        with self._local_lock:
            for comrade, comrade_id in self._comrade_identifiers.items():
                if comrade[0] == username:
                    return comrade_id

    def append_comrade(self, comrade):
        with self._local_lock:
            comrade_username, comrade_password = comrade.username, decrypt_password(comrade.password)
            hashed_comrade = hash((comrade_username, comrade_password))
            self._comrade_identifiers.update({(comrade_username, comrade_password): hashed_comrade})
            self._comrade_usage.update({
                hashed_comrade: ProxyUsage(previous_traffic=comrade.used_bandwidth_b)
            })

            proxy_username, proxy_password = comrade.proxy_username, decrypt_password(comrade.proxy_password)
            proxy_cred = ProxyCredential(credential=(proxy_username, proxy_password))
            proxy_limit = ProxyLimits(bandwidth=comrade.bandwidth_limit_b, threads=comrade.concurrency_threads_limit)
            proxy_spec = proxy_spec_factory(
                proxy_type=comrade.type,
                host=comrade.host,
                port=comrade.port,
                credential=proxy_cred,
                limits=proxy_limit,
                protocol=comrade.protocol,
                record_id=comrade.id,
                rotate_strategy=comrade.rotate_strategy
            )
            self._comrade_specs.update({hashed_comrade: proxy_spec})
            return hashed_comrade

    def get_comrade_proxy_spec(self, identifier):
        with self._local_lock:
            return self._comrade_specs[identifier]

    def get_comrade_by_identifier(self, identifier):
        with self._local_lock:
            for comrade, comrade_id in self._comrade_identifiers.items():
                if comrade_id == identifier:
                    return comrade

    def get_comrade_usage(self, identifier):
        with self._local_lock:
            return self._comrade_usage[identifier]
