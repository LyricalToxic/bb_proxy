from database.dbca import BaseDBCA, SqliteDBCA

mysql_drivers = ["mysql"]
sqlite_drivers = ["sqlite"]


def get_dbca(driver: str) -> type(BaseDBCA):
    if driver in mysql_drivers:
        return "MySQLDBCA"
    elif driver in sqlite_drivers:
        return SqliteDBCA
