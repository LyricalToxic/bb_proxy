from exceptions.comrade import BaseMitmException


class ProxyBandwidthLimitExceed(BaseMitmException):
    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = f"Proxy usage bandwidth exceed."
        self.message = message
        self.code = 470
        super().__init__(message, *args, **kwargs)


class ProxyThreadLimitExceed(BaseMitmException):
    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = f"Proxy usage thread exceed."
        self.message = message
        self.code = 471
        super().__init__(message, *args, **kwargs)
