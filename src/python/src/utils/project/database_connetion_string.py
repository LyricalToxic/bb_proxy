from settings import DB_DATABASE, DB_HOST, DB_PORT, DB_DRIVER, DB_PASSWORD, DB_USERNAME


def get_database_connection_string():
    if DB_DRIVER == "mysql":
        return "mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8mb4".format(
            DB_USERNAME,
            DB_PASSWORD,
            DB_HOST,
            DB_PORT,
            DB_DATABASE,
        )
    elif DB_DRIVER == "sqlite":
        return "sqlite+aiosqlite:///database_persistence/{}.db".format(
            DB_DATABASE,
        )
