import asyncio
from asyncio import CancelledError, FIRST_COMPLETED, Future

from mitmproxy.addons.upstream_auth import parse_upstream_auth
from mitmproxy.connection import Server, ConnectionState
from mitmproxy.http import HTTPFlow
from mitmproxy.net.server_spec import ServerSpec
from mitmproxy.script import concurrent

from utils.types_.containers import ProxySpec


class DynamicUpstreamAddon:

    def __init__(self, owner: "BigBrother") -> None:
        self.owner: "BigBrother" = owner

    def http_connect_upstream(self, flow: HTTPFlow) -> None:
        # WARNING! proxy (ip, port) + auth must be unique
        # No way forward information about the request
        proxy_auth = self.owner.get_proxy_auth(flow.server_conn.address)
        if proxy_auth:
            flow.request.headers["Proxy-Authorization"] = parse_upstream_auth(proxy_auth)

    @concurrent
    def request(self, flow: HTTPFlow) -> None:
        asyncio.run(self.set_actual_upstream(flow))

    async def set_actual_upstream(self, flow: HTTPFlow) -> None:
        try:
            proxy_spec = await self._get_proxy_spec(flow)
        except CancelledError:
            # TODO add reply to client and notify about timeout waiting proxy exceed
            flow.kill()
        else:
            is_proxy_change = proxy_spec.address != flow.server_conn.via.address
            server_connection_already_open = flow.server_conn.timestamp_start is not None
            if is_proxy_change and server_connection_already_open:
                flow.server_conn = Server(flow.server_conn.address)
            flow.server_conn.via = ServerSpec(proxy_spec.protocol, proxy_spec.address)

    async def _get_proxy_spec(self, flow: HTTPFlow) -> ProxySpec:
        return self.owner.get_proxy_spec()
