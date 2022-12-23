from database.dbca import BaseDBCA

mysql_drivers = ["mysql"]
sqlite_drivers = ["sqlite"]
supported_divers = [*mysql_drivers, *sqlite_drivers]


def get_dbca(driver: str) -> type(BaseDBCA):
    if driver in mysql_drivers:
        from database.dbca.mysql import MySQLDBCA
        return MySQLDBCA()
    elif driver in sqlite_drivers:
        from database.dbca.sqlite import SqliteDBCA
        return SqliteDBCA()
    else:
        raise Exception(f"Driver `{driver} not supported. Available drivers {supported_divers}`")
