import asyncio
from logging import getLogger

from mitmproxy.connection import Server, Client
from mitmproxy.http import HTTPFlow, Request

from core.bb_innards.base_big_brother import BaseBigBrother
from exceptions.comrade import EmptyComradeAuthHeader, BaseMitmException
from utils.constans import PROXY_AUTHORIZATION_HEADER, META_COMRADE
from utils.containers import ProxySpec, MetaComrade
from utils.project.func.proxy_authorization import decode_proxy_auth_header
from utils.types import Identifier


class DynamicUpstreamAddon:

    def __init__(self, owner: BaseBigBrother) -> None:
        self.owner: BaseBigBrother = owner
        self.logger = getLogger(DynamicUpstreamAddon.__name__)

    # --------------------------
    def http_connect_upstream(self, flow: HTTPFlow) -> None:
        """
            This handler called for HTTPS connection
        :param flow:
        :return:
        """
        self._inject_proxy_authorization(flow)

    async def request(self, flow: HTTPFlow) -> None:
        """
            This handler set proxy auth if client use HTTP connection
        """
        self.logger.info("Received request %s", flow.request)
        if not flow.server_conn.tls:
            await self._set_actual_upstream(flow)
            self._inject_proxy_authorization(flow)
        await self._reserve_thread(flow.client_conn)

    async def client_disconnected(self, client: Client) -> None:
        await self._release_thread(client)

    async def http_connect(self, flow: HTTPFlow) -> None:
        """
            Handles HTTP tunnelling that is established during HTTPS connection.
            Use `Proxy-Authorization` header for authorization on CONNECT request.
        """
        self.logger.info("Received request %s", flow.request)
        await self._set_actual_upstream(flow)

    # --------------------------

    def _inject_proxy_authorization(self, flow: HTTPFlow) -> None:
        """
            Proxy credentials injects to the request header {PROXY_AUTHORIZATION_HEADER} if exists.
        """
        meta_comrade = getattr(flow.client_conn, META_COMRADE, None)
        if meta_comrade:
            proxy_spec = self.owner.get_comrade_proxy_spec(meta_comrade.comrade_identifier)
            if proxy_spec.credential:
                flow.request.headers[PROXY_AUTHORIZATION_HEADER] = proxy_spec.credential.basic_token

    async def _reserve_thread(self, client: Client) -> None:
        """
            Reserve threads per comrade.
        """
        meta_comrade = getattr(client, META_COMRADE, None)
        if meta_comrade:
            self.owner.comrade_usage[meta_comrade.comrade_identifier].reserve_thread(client.id)
            await asyncio.sleep(0)

    async def _release_thread(self, client: Client) -> None:
        """
            Release thread per comrade.
        """
        meta_comrade = getattr(client, META_COMRADE, None)
        if meta_comrade:
            self.owner.comrade_usage[meta_comrade.comrade_identifier].release_thread(client.id)
            await asyncio.sleep(0)

    async def _set_actual_upstream(self, flow: HTTPFlow) -> None:
        """
            Retrieve, authenticate and set corresponding proxy for comrade.
            If exception C{BaseMitmException} being raised, then custom response will be returned.
        """
        try:
            identifier = await self._authenticate_comrade(flow.request)
            await self._authorize_comrade(flow.request, identifier)
        except BaseMitmException as e:
            self.logger.warning(e)
            flow.response = e.reply_response()
            return

        proxy_spec = self._get_comrade_proxy_spec(identifier)
        proxy_spec.rotate()

        is_proxy_change = proxy_spec.address != flow.server_conn.via.address
        server_connection_already_open = flow.server_conn.timestamp_start is not None
        if is_proxy_change and server_connection_already_open:
            flow.server_conn = Server(flow.server_conn.address)
        self.__set_client_identifier(flow.client_conn, identifier)

    async def _authenticate_comrade(self, request: Request) -> Identifier:
        """
            Delegate authentication to owner.
            Raise C{EmptyComradeAuthHeader} if {PROXY_AUTHORIZATION_HEADER} not exists or empty.
        """
        self.logger.debug("%s. Authentication procedure start", request)
        proxy_auth_header = request.headers.get(PROXY_AUTHORIZATION_HEADER)
        if not proxy_auth_header:
            raise EmptyComradeAuthHeader()
        username, password = decode_proxy_auth_header(proxy_auth_header)
        identifier = await self.owner.authenticate_comrade(username, password)
        self.logger.debug("%s. Authentication procedure finished success", request)
        return identifier

    def _get_comrade_proxy_spec(self, identifier: Identifier) -> ProxySpec:
        # Comrade proxy spec must be in local storage already
        """
            Delegate retrieving comrade proxy specification to owner.
        """
        proxy_spec = self.owner.get_comrade_proxy_spec(identifier)
        return proxy_spec

    async def _authorize_comrade(self, request: Request, identifier: Identifier) -> None:
        """
            Delegate comrade authorization to owner.
        """
        self.logger.debug("%s. Authorization procedure start", request)
        await self.owner.authorize_comrade(identifier)
        self.logger.debug("%s. Authorization procedure finished success", request)

    def __set_client_identifier(self, client: Client, identifier: Identifier) -> None:
        """
            Bind identifier to flow.
        """
        meta_comrade = getattr(client, META_COMRADE, MetaComrade())
        meta_comrade.comrade_identifier = identifier
        setattr(client, META_COMRADE, meta_comrade)
