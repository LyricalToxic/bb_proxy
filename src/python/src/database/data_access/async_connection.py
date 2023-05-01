import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any

from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncResult
from sqlalchemy.sql import Executable


class AsyncConnection(object):
    future: bool = True

    def __init__(self, connection_string: str) -> None:
        self._connection_string: str = connection_string
        self._async_engine: AsyncEngine = None
        self._setup_engine()

    def _setup_engine(self) -> None:
        if self._async_engine:
            self._async_engine.dispose()
        self._async_engine = create_async_engine(self._connection_string, future=self.future)

    def on_engine_setup(self, engine: AsyncEngine) -> None:
        logging.info("On engine setup")

    async def execute(self, stmt: Executable) -> CursorResult:
        async with self._async_engine.begin() as connection:
            return await connection.execute(stmt)

    async def execute_cb(self, callback: Callable, *args, **kwargs) -> Any:
        async with self._async_engine.begin() as connection:
            return await callback(connection, *args, **kwargs)

    async def execute_in_thread(self, callback: Callable) -> None:
        await asyncio.get_running_loop().run_in_executor(
            ThreadPoolExecutor(max_workers=1), callback
        )
