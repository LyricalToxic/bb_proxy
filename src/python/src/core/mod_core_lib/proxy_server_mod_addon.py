import asyncio
import logging
import traceback
from contextlib import contextmanager
from typing import Dict, Tuple

from mitmproxy.addons.proxyserver import Proxyserver
from mitmproxy.connection import Server, Client
from mitmproxy.http import HTTPFlow
from mitmproxy.net.server_spec import ServerSpec
from mitmproxy.proxy import commands, events
from mitmproxy.proxy.mode_servers import ProxyConnectionHandler
from mitmproxy.proxy.server import ConnectionIO
from mitmproxy.utils import asyncio_utils

from core.bb_innards.storage.bb_storage_keeper import BBStorageKeeper
from exceptions import BaseBBException, EmptyComradeAuthHeader
from utils.constans import PROXY_AUTHORIZATION_HEADER, META_COMRADE
from utils.containers import MetaComrade, BufferTrafficUsageBytes
from utils.project.func.proxy_authorization import decode_proxy_auth_header, extract_proxy_auth_header
from utils.types import Identifier


class ProxyConnectionHandlerWrapper:

    def __init__(self, handler: ProxyConnectionHandler, buffer: dict, buffer_lock: asyncio.Lock):
        self._handler: ProxyConnectionHandler = handler
        self._owner_buffer: dict = buffer
        self._buffer_lock: asyncio.Lock = buffer_lock

    def get_mod_handler(self):
        self._handler.server_event = self._server_event
        self._handler._on_data_sent = self._on_data_sent
        self._handler._on_data_received = self._on_data_received
        self._handler._owner_buffer = self._owner_buffer
        self._handler._buffer_lock = self._buffer_lock
        return self._handler

    def _server_event(self, event: events.Event) -> None:
        self._handler.timeout_watchdog.register_activity()
        try:
            layer_commands = self._handler.layer.handle_event(event)
            if isinstance(event, events.DataReceived):
                asyncio_utils.create_task(
                    self._on_data_received(event),
                    name=f"handle_event({event})",
                    client=self._handler.client.peername,
                )
            for command in layer_commands:

                if isinstance(command, commands.OpenConnection):
                    assert command.connection not in self._handler.transports
                    handler = asyncio_utils.create_task(
                        self._handler.open_connection(command),
                        name=f"server connection manager {command.connection.address}",
                        client=self._handler.client.peername,
                    )
                    self._handler.transports[command.connection] = ConnectionIO(handler=handler)
                elif isinstance(command, commands.RequestWakeup):
                    task = asyncio_utils.create_task(
                        self._handler.wakeup(command),
                        name=f"wakeup timer ({command.delay:.1f}s)",
                        client=self._handler.client.peername,
                    )
                    assert task is not None
                    self._handler.wakeup_timer.add(task)
                elif (
                        isinstance(command, commands.ConnectionCommand)
                        and command.connection not in self._handler.transports
                ):
                    pass  # The connection has already been closed.
                elif isinstance(command, commands.SendData):
                    writer = self._handler.transports[command.connection].writer
                    assert writer
                    if not writer.is_closing():
                        writer.write(command.data)
                    asyncio_utils.create_task(
                        self._on_data_sent(command),
                        name=f"handle_event({event})",
                        client=self._handler.client.peername,
                    )
                elif isinstance(command, commands.CloseConnection):
                    self._handler.close_connection(command.connection, command.half_close)
                elif isinstance(command, commands.StartHook):
                    asyncio_utils.create_task(
                        self._handler.hook_task(command),
                        name=f"handle_hook({command.name})",
                        client=self._handler.client.peername,
                    )
                elif isinstance(command, commands.Log):
                    self._handler.log(command.message, command.level)
                else:
                    raise RuntimeError(f"Unexpected command: {command}")
        except Exception:
            self._handler.log(f"mitmproxy has crashed!\n{traceback.format_exc()}", logging.ERROR)

    async def _on_data_sent(self, command: commands.SendData):
        if isinstance(command.connection, Server):
            peer_address = self._handler.client.peername
            payload_size = len(command.data)
            async with self._handler._buffer_lock:
                peer_buffer = self._handler._owner_buffer.get(peer_address)
                peer_buffer.upload = peer_buffer.upload + payload_size
                self._handler._owner_buffer[peer_address] = peer_buffer
                self._handler.log(f"On data received {peer_address}: {peer_buffer}, last upload {payload_size}",
                                  level=logging.INFO)

    async def _on_data_received(self, event: events.DataReceived):
        if isinstance(event.connection, Server):
            peer_address = self._handler.client.peername
            payload_size = len(event.data)
            async with self._handler._buffer_lock:
                peer_buffer = self._handler._owner_buffer.get(peer_address, {})
                peer_buffer.download = peer_buffer.download + payload_size
                self._handler._owner_buffer[peer_address] = peer_buffer
                self._handler.log(f"On data sent {peer_address}: {peer_buffer}, last download {payload_size}",
                                  level=logging.INFO)


class ProxyServerModAddon(Proxyserver):
    """
    This addon runs the actual proxy server.
    """
    connections: Dict[Tuple, ProxyConnectionHandler]
    # Must provide the same name as parent, because in 9 version in master.py#52-56 get addons by their name.
    # WTF? Why isn't instance checking used instead of?
    name: str = "proxyserver"

    def __init__(self, owner):
        super().__init__()
        self._local_buffer: dict = {}
        self._buffer_lock: asyncio.Lock = asyncio.Lock()
        self._owner = owner
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

    @property
    def owner_storage_keeper(self) -> BBStorageKeeper:
        return self._owner.storage_keeper

    @contextmanager
    def register_connection(self, connection_id: tuple, handler: ProxyConnectionHandler) -> None:
        if isinstance(handler, ProxyConnectionHandler):
            pch_wrapper = ProxyConnectionHandlerWrapper(
                handler, self._local_buffer, self._buffer_lock
            )
            handler_mod = pch_wrapper.get_mod_handler()
            self.connections[connection_id] = handler_mod
        else:
            self.connections[connection_id] = handler
        try:
            yield
        finally:
            del self.connections[connection_id]

    def http_connect_upstream(self, flow: HTTPFlow) -> None:
        """
            This handler called for HTTPS connection
        """
        self._inject_proxy_authorization(flow)

    async def http_connect(self, flow: HTTPFlow) -> None:
        """
            Handles HTTP tunnelling that is established during HTTPS connection.
            Use `Proxy-Authorization` header for authorization on CONNECT request.
        """
        await self._process_comrade_upstream(flow)

    async def server_disconnected(self, flow: HTTPFlow) -> None:
        """
            Drain buffered data on HTTP&HTTPS connection when server disconnected.
            For HTTPS connection it's happened immediately, so we can suppose
             1 server disconnection = 1 request-response.
            For HTTP connection server disconnected with delay. Therefore, to be more reliable, we drain buffer
             on response and on server disconnection.
        """
        self.logger.info("on server disconnected")
        await self._drain_buffer(flow)

    async def _drain_buffer(self, flow: HTTPFlow) -> None:
        client = getattr(flow, "client", None) or getattr(flow, "client_conn", None)
        meta_comrade = getattr(client, META_COMRADE, None)

        if meta_comrade:
            comrade_identifier = meta_comrade.comrade_identifier
            client_address = client.peername
            async with self._buffer_lock:
                comrade_buffer = self._local_buffer.get(client_address)
                if comrade_buffer:
                    self.owner_storage_keeper.add_traffic_usage(
                        comrade_identifier, comrade_buffer.upload, comrade_buffer.download
                    )
                    comrade_buffer.reset()

    async def response(self, flow: HTTPFlow) -> None:
        """
            Drain buffered data on HTTP connection when response received
        """
        await self._drain_buffer(flow)

    async def request(self, flow: HTTPFlow) -> None:
        """
            Handles HTTP request.
            Starts process of handling comrade. Injects comrade's proxy credentials to the request header
        """
        await self._process_comrade_upstream(flow)
        self._inject_proxy_authorization(flow)

    async def _process_comrade_upstream(self, flow: HTTPFlow):
        """
            Process comrade in the next steps:
                1. Check PROXY_AUTHORIZATION_HEADER
                2. Assert PROXY_AUTHORIZATION_HEADER value
                3. Parse comrade username and password
                4. Identify comrade by username
                5. Authenticate comrade by username and password
                6. Authorize comrade
                7. Set comrade's proxy server and inject proxy credentials to request header
                8. Reserve thread if success
                9. Return response with status code of failure.
        """
        try:
            await self._set_proxy_upstream(flow)
        except BaseBBException as e:
            self.logger.warning(e)
            flow.response = e.reply_response()
            return
        else:
            self._reserve_thread(flow.client_conn)

    async def client_connected(self, client: Client):
        self.logger.info("on client connected")
        async with self._buffer_lock:
            if client.peername in self._local_buffer:
                self.logger.critical(f"{client.peername} already in buffer")
            else:
                self._local_buffer[client.peername] = BufferTrafficUsageBytes()

    async def client_disconnected(self, client: Client):
        client_address = client.peername

        async with self._buffer_lock:
            del self._local_buffer[client_address]
            self._release_thread(client)

    def _release_thread(self, client_conn):
        meta_comrade = getattr(client_conn, META_COMRADE, None)
        if meta_comrade:
            self.owner_storage_keeper.release_peer_thread(meta_comrade.comrade_identifier, client_conn.peername)

    def _reserve_thread(self, client_conn):
        meta_comrade = getattr(client_conn, META_COMRADE, None)
        if meta_comrade:
            self.owner_storage_keeper.reserve_peer_thread(meta_comrade.comrade_identifier, client_conn.peername)

    # ---------------------------------------------------------
    def _inject_proxy_authorization(self, flow: HTTPFlow):
        meta_comrade = getattr(flow.client_conn, META_COMRADE, None)
        if meta_comrade:
            proxy_spec = self._owner.get_comrade_proxy_spec(meta_comrade.comrade_identifier)
            if proxy_spec.credential:
                flow.request.headers[PROXY_AUTHORIZATION_HEADER] = proxy_spec.credential.basic_token

    async def _set_proxy_upstream(self, flow: HTTPFlow) -> None:
        identifier = await self._authenticate_comrade(flow)
        await self._authorize_comrade(flow, identifier)

        proxy_spec = self._owner.get_comrade_proxy_spec(identifier)
        proxy_spec.rotate()
        self._set_proxy_spec(flow, proxy_spec, identifier)

    def _set_proxy_spec(self, flow, proxy_spec, identifier):
        is_proxy_changed = proxy_spec.address != flow.server_conn.via[1]
        server_connection_already_opened = flow.server_conn.timestamp_start is not None
        if is_proxy_changed and server_connection_already_opened:
            flow.server_conn = Server(flow.server_conn.address)
        self._set_client_identifier(flow.client_conn, identifier)
        flow.server_conn.via = ServerSpec((proxy_spec.protocol, proxy_spec.address))

    async def _authenticate_comrade(self, flow: HTTPFlow) -> Identifier:
        self.logger.debug(f"{flow.request}. Authentication procedure start")
        proxy_auth_header = extract_proxy_auth_header(flow.request)
        if not proxy_auth_header:
            raise EmptyComradeAuthHeader()

        username, password = decode_proxy_auth_header(proxy_auth_header)
        conn_protocol = flow.server_conn.transport_protocol.upper()
        self.logger.info(f"It's me {username}! I am from {conn_protocol} connection!")

        identifier = await self._owner.authenticate_comrade(username, password)

        self.logger.debug(f"{flow.request}. Authentication procedure finished success")
        return identifier

    async def _authorize_comrade(self, flow: HTTPFlow, identifier: Identifier) -> None:
        self.logger.debug(f"{flow.request}. Authorization procedure start")
        await self._owner.authorize_comrade(identifier)
        self.logger.debug(f"{flow.request}. Authorization procedure finished success")

    def _set_client_identifier(self, client: Client, identifier: Identifier):
        meta_comrade = getattr(client, META_COMRADE, MetaComrade())
        meta_comrade.comrade_identifier = identifier
        setattr(client, META_COMRADE, meta_comrade)
