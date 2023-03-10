from utils.containers import ProxyCredential, ProxySpec


def load_default_proxy(options):
    def _load_from_env():
        from settings import DEFAULT_PROXY_CREDENTIALS, DEFAULT_PROXY_PORT, DEFAULT_PROXY_HOST
        if not (DEFAULT_PROXY_HOST and DEFAULT_PROXY_PORT):
            return None
        else:
            return ProxySpec(
                host=DEFAULT_PROXY_HOST,
                port=DEFAULT_PROXY_PORT,
                credential=ProxyCredential(DEFAULT_PROXY_CREDENTIALS),
            )

    def _load_from_options(options):
        if not (getattr(options, "proxy_host", None) and getattr(options, "proxy_host", None)):
            return None
        else:
            return ProxySpec(
                host=getattr(options, "proxy_host", None),
                port=getattr(options, "proxy_port", None),
                protocol=getattr(options, "protocol", "https"),
                credential=ProxyCredential(getattr(options, "proxy_credential", None)),
            )

    def _load_from_db():
        pass

    proxy_spec = _load_from_options(options) or _load_from_env() or _load_from_db()
    return proxy_spec


def load_proxy_stub():
    return ProxySpec(
        host="localhost",
        port=1234,
        protocol="https",
        credential=ProxyCredential(None),
    )
