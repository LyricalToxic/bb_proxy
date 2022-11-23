class DriverNotSupported(Exception):

    def __init__(self, message=None, driver=None, *args, **kwargs):
        if not message:
            message = f"Big brother not supported sql driver: {driver}"
        super().__init__(message, *args, **kwargs)


class InvalidDatabaseCredentialError(Exception):

    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = f"Cannot connect to database with given credentials. " \
                      f"To create local sqlite database set DB_PREPARING_ENABLED=True"
        super().__init__(message, *args, **kwargs)
