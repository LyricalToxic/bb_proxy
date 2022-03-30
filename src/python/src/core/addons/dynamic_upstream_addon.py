import asyncio
from logging import getLogger

from mitmproxy.connection import Server
from mitmproxy.http import HTTPFlow, Request
from mitmproxy.net.server_spec import ServerSpec
from mitmproxy.script import concurrent

from exceptions.comrade import EmptyComradeAuthHeader, BaseMitmException
from utils.project.http import calculate_http_obj_size
from utils.project.proxy_authorization import decode_proxy_auth_header
from utils.types_.containers import ProxySpec


class DynamicUpstreamAddon:

    def __init__(self, owner: "BigBrother") -> None:
        self.owner: "BigBrother" = owner
        self.logger = getLogger(DynamicUpstreamAddon.__name__)

    # --------------------------
    # Mitm proxy hook handlers
    def http_connect_upstream(self, flow: HTTPFlow) -> None:
        # WARNING! proxy (ip, port) + auth must be unique
        # No way forward information about the request
        comrade_identifier = flow.client_conn._comrade_identifier
        proxy_spec = self.owner.get_comrade_proxy_spec(comrade_identifier)
        if proxy_spec.credential:
            flow.request.headers["Proxy-Authorization"] = proxy_spec.credential.basic_token

    @concurrent
    def request(self, flow: HTTPFlow) -> None:
        self.logger.info("Received request %s", flow.request)
        asyncio.run(self._set_actual_upstream(flow))

    def response(self, flow: HTTPFlow) -> None:
        self.logger.info("Received request %s", flow.response)
        if hasattr(flow.client_conn, "_comrade_identifier"):
            comrade_identifier = flow.client_conn._comrade_identifier
            self.owner.comrade_usage[comrade_identifier].release_thread()
            self.owner.comrade_usage[comrade_identifier].inc_download_traffic(calculate_http_obj_size(flow.response))
            self.owner.comrade_usage[comrade_identifier].inc_upload_traffic(calculate_http_obj_size(flow.request))

    # --------------------------
    async def _set_actual_upstream(self, flow: HTTPFlow) -> None:
        try:
            identifier = await self._authenticate_comrade(flow.request)
            self._authorize_comrade(identifier, flow.request)
        except BaseMitmException as e:
            self.logger.warning(e)
            flow.response = e.reply_response()
            return

        proxy_spec = self._get_comrade_proxy_spec(identifier)
        is_proxy_change = proxy_spec.address != flow.server_conn.via.address
        server_connection_already_open = flow.server_conn.timestamp_start is not None
        if is_proxy_change and server_connection_already_open:
            flow.server_conn = Server(flow.server_conn.address)
        flow.client_conn._comrade_identifier = identifier
        flow.server_conn.via = ServerSpec(proxy_spec.protocol, proxy_spec.address)

    async def _authenticate_comrade(self, request: Request):
        self.logger.debug("%s. Authentication procedure start", request)
        proxy_auth_header = request.headers.get("Proxy-Authorization1")  # FIXME: change header key
        if not proxy_auth_header:
            raise EmptyComradeAuthHeader()
        username, password = decode_proxy_auth_header(proxy_auth_header)
        identifier = await self.owner.authenticate_comrade(username, password)
        self.logger.debug("%s. Authentication procedure finished success", request)
        return identifier

    def _get_comrade_proxy_spec(self, identifier) -> ProxySpec:
        # Comrade proxy spec must be in local storage already
        proxy_spec = self.owner.get_comrade_proxy_spec(identifier)
        self.owner.comrade_usage[identifier].reserve_thread()
        return proxy_spec

    def _authorize_comrade(self, identifier, request):
        self.logger.debug("%s. Authorization procedure start", request)
        self.owner.authorize_comrade(identifier)
        self.logger.debug("%s. Authorization procedure finished success", request)
