import asyncio
from asyncio import Task
from functools import partial
from typing import Optional

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import Row

from core.bb_innards.communicative_big_brother import CommunicativeBigBrother
from core.bb_innards.storage.bb_storage_keeper import BBStorageKeeper
from database.data_access.connection import AsyncConnection
from database.dbca import BaseDBCA
from database.models.sqlite import ProxyComrade
from exceptions.comrade import ComradeIdentificationError, ComradeAuthenticationError
from exceptions.database import InvalidDatabaseCredentialError
from exceptions.proxy import ProxyBandwidthLimitExceed, ProxyThreadLimitExceed
from settings import DB_PREPARING_ENABLED
from utils.containers import ProxySpec
from utils.project.enums.proxy_states import ProxyStates
from utils.project.enums.state_logging_triggers import StateLoggingTriggersBySignal, StateLoggingTriggers, \
    StateLoggingTriggersByTime, LogTrigger
from utils.project.func.database_connection import load_database_connection_url, load_default_database_connection_url
from utils.project.func.paths import get_root_path
from utils.types import Identifier


class BigBrother(CommunicativeBigBrother):

    def __init__(self, storage_keeper: BBStorageKeeper, dbca: BaseDBCA) -> None:
        super().__init__(storage_keeper)
        self.comrade_retrieve_tasks: dict = {}
        self.dbca: BaseDBCA = dbca
        self.async_connection: AsyncConnection

    async def before_setup_mitmproxy(self) -> None:
        await super().before_setup_mitmproxy()
        self.async_connection = await self.setup_async_connection()

    async def setup_async_connection(self) -> AsyncConnection:
        connection_string = await self._get_database_connection_string()
        async_connection = AsyncConnection(connection_string)
        partial_apply_migrations = partial(self._apply_migrations, connection_string)
        await async_connection.execute_in_thread(partial_apply_migrations)
        return async_connection

    def _apply_migrations(self, connection_string: str) -> None:
        try:
            alembic_cfg = Config(get_root_path().joinpath("alembic.ini"))
            alembic_cfg.set_main_option("sqlalchemy.url", connection_string)
            alembic_cfg.set_main_option("config_logger", "0")
            command.upgrade(alembic_cfg, "head")
        except Exception as e:
            self.logger.error(e)

    async def _get_database_connection_string(self) -> Optional[str]:
        db_connection_url_from_config = load_database_connection_url()
        async_connection = AsyncConnection(db_connection_url_from_config)
        try:
            await async_connection.execute(self.dbca.stmt_collection.build_init_query())
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
    async def authenticate_comrade(self, username: str, password: str) -> Optional[Identifier]:
        identifier = await self.identify_comrade(username)
        if not self._storage_keeper.is_comrade_authenticated(identifier, password):
            raise ComradeAuthenticationError(username=username)
        else:
            return identifier

    async def identify_comrade(self, username: str) -> Optional[Identifier]:
        identifier = self._get_comrade_identifier_from_local(username)
        if not identifier:
            comrade_retrieving_task = self.comrade_retrieve_tasks.get(username, None)
            if not comrade_retrieving_task:
                comrade_retrieving_task = asyncio.ensure_future(self._get_comrade_identifier_from_database(username))
                comrade_retrieving_task.set_name(username)
                self.comrade_retrieve_tasks[username] = comrade_retrieving_task
                comrade_retrieving_task.add_done_callback(self.on_comrade_retrieved)
            identifier = await comrade_retrieving_task
        if not identifier:
            raise ComradeIdentificationError(username=username)
        else:
            return identifier

    def on_comrade_retrieved(self, done_task: Task) -> None:
        results = done_task.result()
        if results:
            self.schedule_logging_statistic(results)
        del self.comrade_retrieve_tasks[done_task.get_name()]

    def schedule_logging_statistic(self, identifier: Identifier) -> Task:
        self.logger.info("LOG STATISTIC SETUP FOR %s", identifier)
        task = asyncio.run_coroutine_threadsafe(
            self.log_statistic(identifier, StateLoggingTriggersByTime.EVERY_MINUTE),
            self._mimtproxy_event_loop
        )
        self._storage_keeper.set_logging_task(task, identifier)
        return task

    async def _get_comrade_identifier_from_database(self, username: str) -> Optional[Identifier]:
        comrade = await self._retrieve_comrade(username)
        if not comrade:
            return None
        else:
            identifier = self._storage_keeper.add_comrade(comrade)
            await self._update_proxy_comrade(
                comrade.id,
                {ProxyComrade.status: ProxyStates.RESERVED}
            )
        return identifier

    async def _update_proxy_comrade(self, comrade_id: int, values: dict) -> None:
        update_stmt = self.dbca.stmt_collection.build_update_proxy_comrade_query(comrade_id, values)
        await self.async_connection.execute(update_stmt)

    async def _retrieve_comrade(self, username: str) -> Row:
        select_stmt = self.dbca.stmt_collection.build_select_comrade_proxy_query(username)
        cursor_result = await self.async_connection.execute(select_stmt)
        return cursor_result.fetchone()

    def _get_comrade_identifier_from_local(self, username: str) -> Identifier:
        return self._storage_keeper.indentify_comrade(username)

    # -------------------------------

    # -------------------------------
    # Authorize comrade
    async def authorize_comrade(self, identifier: Identifier) -> None:
        if self._storage_keeper.is_bandwidth_exceed(identifier):
            comrade_stats = self._storage_keeper.get_comrade_stats(identifier)
            comrade_id = self._storage_keeper.get_comrade_proxy_spec(identifier).record_id
            await self._update_proxy_comrade(comrade_id, {
                ProxyComrade.status: ProxyStates.BANDWIDTH_LIMIT_UTILISED,
                ProxyComrade.used_bandwidth_b: text(
                    f"{ProxyComrade.used_bandwidth_b.name} + {comrade_stats.traffic_usage.total}"
                )
            })
            await self.log_statistic(identifier, StateLoggingTriggers.BANDWIDTH_LIMIT_USAGE_EXCEED)
            self._storage_keeper.purge_logging_task(identifier)
            self._storage_keeper.remove_comrade(identifier)
            raise ProxyBandwidthLimitExceed()
        if self._storage_keeper.is_thread_limit_exceed(identifier):
            raise ProxyThreadLimitExceed()

    # -------------------------------
    async def log_statistic(self, identifier: Identifier, trigger: Optional[LogTrigger] = None) -> None:
        if trigger and trigger.name in StateLoggingTriggers.keys:
            while True:
                await asyncio.sleep(trigger.delay.seconds)
                stats = self._storage_keeper.get_comrade_stats(identifier)
                proxy_spec = self._storage_keeper.get_comrade_proxy_spec(identifier)
                insert_stmt = self.dbca.stmt_collection.build_statistic_insert_query(stats, proxy_spec, trigger)
                await self.async_connection.execute(insert_stmt)
                self._storage_keeper.reset_traffic(identifier)
                if trigger.name in StateLoggingTriggersBySignal.keys:
                    break
        else:
            self.logger.error("Unknown trigger: %s", trigger)

    async def before_shutdown(self) -> None:
        await super().before_shutdown()
        for identifier in self._storage_keeper.get_identifiers():
            await self.log_statistic(identifier, StateLoggingTriggers.BEFORE_SHUTDOWN)
            await self._release_proxy_comrade(identifier)

    async def _release_proxy_comrade(self, identifier: Identifier) -> None:
        stats = self._storage_keeper.get_comrade_stats(identifier)
        proxy_spec = self._storage_keeper.get_comrade_proxy_spec(identifier)
        is_available = self._storage_keeper.is_comrade_proxy_exceed(identifier)
        status = ProxyStates.AVAILABLE if is_available else ProxyStates.BANDWIDTH_LIMIT_UTILISED
        await self._update_proxy_comrade(proxy_spec.record_id, {
            ProxyComrade.status: status,
            ProxyComrade.used_bandwidth_b: text(
                f"{ProxyComrade.used_bandwidth_b.name} + {stats.traffic_usage.total}"
            )
        })

    @property
    def storage_keeper(self) -> BBStorageKeeper:
        return self._storage_keeper

    def get_comrade_proxy_spec(self, identifier: Identifier) -> ProxySpec:
        return self._storage_keeper.get_comrade_proxy_spec(identifier)
