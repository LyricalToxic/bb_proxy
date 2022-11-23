from sqlalchemy.ext.asyncio import create_async_engine

from utils.project.func.database_connection import load_database_connection_url

async_engine = create_async_engine(load_database_connection_url())
