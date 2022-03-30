from core.bb.communicative_big_brother import CommunicativeBigBrother
from database.connection import async_engine
from database.models.bb import ProxyComrade, Comrade, ProxyCredential
from sqlalchemy import select, and_, update

from exceptions.comrade import ComradeIdentificationError, ComradeAuthenticationError
from exceptions.proxy import ProxyBandwidthLimitExceed, ProxyThreadLimitExceed


class BigBrother(CommunicativeBigBrother):
    # TODO: add polling db for update actual state of the comrade proxy.
    #  This needs if user change credentials or something else in table records.

    def __init__(self):
        super().__init__()
        self.engine = self.setup_engine()

    def setup_engine(self):
        # TODO: add checking connection.
        #  If connection not established, then create sqlite local db and apply migrations. Notify user about it.
        return async_engine

    async def get_proxy_spec(self):
        connection = await async_engine.connect()
        await connection.execute()
        await connection.close()

    # -------------------------------
    # Comrade identification procedure
    # If comrade not found in local storage, then try ro retrieve record from database and append it to local storage
    async def authenticate_comrade(self, username, password):
        identifier = await self.identify_comrade(username)
        comrade = self._local_storage.get_comrade_by_identifier(identifier)
        if comrade and comrade[1] == password:
            return identifier
        else:
            raise ComradeAuthenticationError(username=username)

    async def identify_comrade(self, username):
        identifier = self._get_comrade_identifier_from_local(username)
        if not identifier:
            identifier = await self._get_comrade_identifier_from_database(username)
        if not identifier:
            raise ComradeIdentificationError(username=username)
        else:
            return identifier

    async def _get_comrade_identifier_from_database(self, username):
        comrade = await self._retrieve_comrade(username)
        if not comrade:
            return None
        else:
            identifier = self._local_storage.append_comrade(comrade)
            await self._update_proxy_comrade(comrade)
            return identifier

    async def _update_proxy_comrade(self, comrade):
        async with async_engine.begin() as connection:
            update_stmt = self._build_update_proxy_comrade(comrade)
            await connection.execute(update_stmt)

    async def _retrieve_comrade(self, username):
        async with async_engine.begin() as connection:
            select_stmt = self.build_select_comrade_proxy_stmt(username)
            cursor_result = await connection.execute(select_stmt)
            return cursor_result.fetchone()

    def build_select_comrade_proxy_stmt(self, username):
        joined_stmt = ProxyComrade.__table__ \
            .join(Comrade, Comrade.id == ProxyComrade.comrade_id) \
            .join(ProxyCredential, ProxyCredential.id == ProxyComrade.proxy_credential_id)
        select_stmt = select([
            ProxyComrade.id,
            ProxyComrade.comrade_id,
            ProxyComrade.proxy_credential_id,
            ProxyComrade.bandwidth_limit_b,
            ProxyComrade.concurrency_threads_limit,
            ProxyComrade.used_bandwidth_b,
            Comrade.username,
            Comrade.password,
            ProxyCredential.host,
            ProxyCredential.port,
            ProxyCredential.username.label("proxy_username"),
            ProxyCredential.password.label("proxy_password"),
            ProxyCredential.options,
            ProxyCredential.type,
        ]).where(
            and_(
                Comrade.username == username,
                ProxyComrade.status == 0,  # TODO: make enum class
            )
        ).select_from(joined_stmt)
        return select_stmt

    def _build_update_proxy_comrade(self, result):
        update_stmt = update(ProxyComrade).values({
            # ProxyComrade.status: 1,  # TODO: make enum class
            ProxyComrade.status: 0,  # FIXME: ONLY FOR TESTS
        }).where(
            ProxyComrade.id == result.id
        )
        return update_stmt

    def _get_comrade_identifier_from_local(self, username):
        return self._local_storage.indentify_comrade(username)

    # -------------------------------

    # -------------------------------
    # Get proxy spec by comrade identifier
    def get_comrade_proxy_spec(self, identifier):
        return self._local_storage.get_comrade_proxy_spec(identifier)

    # -------------------------------

    # -------------------------------
    # Authorize comrade
    def authorize_comrade(self, identifier):
        comrade_usage = self._local_storage.get_comrade_usage(identifier)
        proxy_comrade = self._local_storage.get_comrade_proxy_spec(identifier)
        if comrade_usage.total_traffic >= proxy_comrade.limits.bandwidth:
            raise ProxyBandwidthLimitExceed()
        if comrade_usage.threads >= proxy_comrade.limits.threads:
            raise ProxyThreadLimitExceed()

    # -------------------------------

    # -------------------------------
    # Comrade usage
    @property
    def comrade_usage(self):
        return self._local_storage._comrade_usage
    # -------------------------------
