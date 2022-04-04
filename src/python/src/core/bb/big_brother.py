import asyncio
import datetime

from sqlalchemy.ext.asyncio import create_async_engine

from core.bb.communicative_big_brother import CommunicativeBigBrother
from database.models.bb import ProxyComrade, Comrade, ProxyCredential, Statistic
from sqlalchemy import select, and_, update, text

from exceptions.comrade import ComradeIdentificationError, ComradeAuthenticationError
from exceptions.database import InvalidDatabaseCredentialError
from exceptions.proxy import ProxyBandwidthLimitExceed, ProxyThreadLimitExceed
from settings import DB_PREPARING_ENABLED
from utils.project.database_connection import load_database_connection_url, load_default_database_connection_url
from utils.project.enums.proxy_states import ProxyStates
from utils.project.enums.state_logging_triggers import StateLoggingTriggersBySignal, StateLoggingTriggers
from sqlalchemy import insert
from alembic.config import Config
from alembic import command

from utils.project.paths import get_root_path


class BigBrother(CommunicativeBigBrother):
    # TODO: add polling db for update actual state of the comrade proxy.
    #  This needs if user change credentials or something else in table records.

    def __init__(self):
        super().__init__()
        self.async_engine = None

    async def before_setup_mitmproxy(self):
        self.async_engine = await self.setup_engine()

    async def setup_engine(self):
        connection_string = await self._get_database_connection_string()
        async_engine = create_async_engine(connection_string)
        # FIXME: alembic command raised exception from already running event loop
        #  See database/env.py:59-65
        # try:
        #     alembic_cfg = Config(get_root_path().joinpath("alembic.ini"))
        #     alembic_cfg.set_main_option("sqlalchemy.url", connection_string)
        #     command.upgrade(alembic_cfg, "head")
        # except Exception as e:
        #     print(e)
        return async_engine

    async def _get_database_connection_string(self):
        db_connection_url_from_config = load_database_connection_url()
        async_engine = create_async_engine(db_connection_url_from_config)
        try:
            async with async_engine.begin() as connection:
                await connection.execute(text("SELECT 1;"))
            return db_connection_url_from_config
        except Exception as e:
            self.logger.warning("Connection to database failed. %s", e)
            if DB_PREPARING_ENABLED:
                self.logger.warning("Default local sqlite database will use.")
                return load_default_database_connection_url()
            else:
                raise InvalidDatabaseCredentialError()

    # -------------------------------

    # Comrade identification procedure
    # If comrade not found in local storage, then try ro retrieve record from database and append it to local storage
    async def authenticate_comrade(self, username, password):
        identifier = await self.identify_comrade(username)
        comrade = self._local_storage.get_comrade(identifier)
        if comrade and comrade[1] == password:
            return identifier
        else:
            raise ComradeAuthenticationError(username=username)

    async def identify_comrade(self, username):
        identifier = self._get_comrade_identifier_from_local(username)
        if not identifier:
            identifier = await self._get_comrade_identifier_from_database(username)
            if identifier:
                self.schedule_logging_statistic(identifier)
        if not identifier:
            raise ComradeIdentificationError(username=username)
        else:
            return identifier

    def schedule_logging_statistic(self, identifier):
        task = asyncio.run_coroutine_threadsafe(self.log_statistic(identifier), self._mimtproxy_event_loop)
        self._local_storage.inject_logging_task(task, identifier)
        return task

    async def _get_comrade_identifier_from_database(self, username):
        comrade = await self._retrieve_comrade(username)
        if not comrade:
            return None
        else:
            identifier = self._local_storage.append_comrade(comrade)
            await self._update_proxy_comrade(comrade.id, {
                ProxyComrade.status: ProxyStates.RESERVED,
            })
            return identifier

    async def _update_proxy_comrade(self, comrade_id, values):
        async with self.async_engine.begin() as connection:
            update_stmt = self._build_update_proxy_comrade(comrade_id, values)
            await connection.execute(update_stmt)

    async def _retrieve_comrade(self, username):
        async with self.async_engine.begin() as connection:
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
            ProxyComrade.rotate_strategy,
            Comrade.username,
            Comrade.password,
            ProxyCredential.type,
            ProxyCredential.protocol,
            ProxyCredential.host,
            ProxyCredential.port,
            ProxyCredential.username.label("proxy_username"),
            ProxyCredential.password.label("proxy_password"),
            ProxyCredential.options,
        ]).where(
            and_(
                Comrade.username == username,
                ProxyComrade.status == ProxyStates.AVAILABLE,
            )
        ).select_from(joined_stmt)
        return select_stmt

    def _build_update_proxy_comrade(self, id_, values):
        update_stmt = update(ProxyComrade).values(values).where(ProxyComrade.id == id_)
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
    async def authorize_comrade(self, identifier):
        comrade_usage = self._local_storage.get_comrade_usage(identifier)
        proxy_comrade = self._local_storage.get_comrade_proxy_spec(identifier)
        if comrade_usage.total_traffic >= proxy_comrade.limits.bandwidth:
            await self._update_proxy_comrade(proxy_comrade.record_id, {
                ProxyComrade.status: ProxyStates.BANDWIDTH_LIMIT_UTILISED,
                ProxyComrade.used_bandwidth_b: comrade_usage.total_traffic
            })
            await self.log_statistic(identifier, StateLoggingTriggers.BANDWIDTH_LIMIT_USAGE_EXCEED)
            comrade_usage._logging_task.cancel()
            self._local_storage.remove_comrade_completely(identifier)
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
    async def log_statistic(self, identifier, force_trigger=None):
        stats = self._local_storage.get_comrade_usage(identifier)
        proxy_spec = self._local_storage.get_comrade_proxy_spec(identifier)
        if force_trigger and force_trigger.name in StateLoggingTriggersBySignal.keys:
            await asyncio.sleep(force_trigger.delay.seconds)
            async with self.async_engine.begin() as connection:
                insert_stmt = self._build_statistic_insert_statement(stats, proxy_spec, force_trigger)
                await connection.execute(insert_stmt)
            self._local_storage._comrade_usage[identifier].reset_traffic()
        else:
            trigger = stats._logging_trigger
            while True:
                await asyncio.sleep(trigger.delay.seconds)
                async with self.async_engine.begin() as connection:
                    insert_stmt = self._build_statistic_insert_statement(stats, proxy_spec, trigger)
                    await connection.execute(insert_stmt)
                self._local_storage._comrade_usage[identifier].reset_traffic()

    def _build_statistic_insert_statement(self, stats, proxy_spec, trigger):
        insert_stmt = insert(Statistic).values({
            Statistic.proxy_comrade_limit_id: proxy_spec.record_id,
            Statistic.from_timestamp: stats._from_timestamp,
            Statistic.to_timestamp: datetime.datetime.now(),
            Statistic.trigger: trigger.name,
            Statistic.number_of_requests: stats.total_requests,
            Statistic.upload_traffic_bytes: stats.upload_traffic,
            Statistic.download_traffic_bytes: stats.download_traffic,
            Statistic.total_traffic_bytes: stats.upload_traffic + stats.download_traffic,
        }).prefix_with("OR IGNORE")
        return insert_stmt

    async def before_shutdown(self):
        self.logger.info("BEFORE SHUTDOWN")
        for identifier in self._local_storage._comrade_identifiers.values():
            await self.log_statistic(identifier, StateLoggingTriggers.BEFORE_SHUTDOWN)
            await self._release_proxy_comrade(identifier)
        self._master.shutdown()

    async def _release_proxy_comrade(self, identifier):
        stats = self._local_storage.get_comrade_usage(identifier)
        proxy_spec = self._local_storage.get_comrade_proxy_spec(identifier)
        status = ProxyStates.AVAILABLE if stats.total_traffic < proxy_spec.limits.bandwidth \
            else ProxyStates.BANDWIDTH_LIMIT_UTILISED
        await self._update_proxy_comrade(proxy_spec.record_id, {
            ProxyComrade.status: status,
            ProxyComrade.used_bandwidth_b: stats.total_traffic
        })
