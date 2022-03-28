from sqlalchemy.ext.asyncio import create_async_engine

from utils.project.database_connetion_string import get_database_connection_string

async_engine = create_async_engine(get_database_connection_string())
