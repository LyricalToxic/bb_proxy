from mitmproxy.http import Response


class BaseMitmException(Exception):
    code: int = 449
    message: str = "Something went wrong on mitmproxy side."

    def reply_response(self):
        body = self.message
        return Response.make(
            status_code=self.code,
            content=body,
            headers={"Content-Type": "text/html"}
        )


class EmptyComradeAuthHeader(BaseMitmException):

    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = "`Proxy-Authorization` header is empty, please enter username and password."
        self.code = 460
        self.message = message
        super().__init__(message, *args, **kwargs)


class IncorrectComradeAuthHeader(BaseMitmException):
    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = "`Proxy-Authorization` header has incorrect format." \
                      "Please enter username and password with following format:" \
                      "`Basic base64encode(%username%, %password%)`"
        self.code = 461
        self.message = message
        super().__init__(message, *args, **kwargs)


class ComradeIdentificationError(BaseMitmException):
    def __init__(self, message=None, username=None, *args, **kwargs):
        if not message:
            message = f"Cannot identify comrade. No found comrade with username {username}"
        self.code = 462
        self.message = message
        super().__init__(message, *args, **kwargs)


class TimeoutIdentificationError(BaseMitmException):
    def __init__(self, message=None, username=None, *args, **kwargs):
        if not message:
            self.message = f"Identification comrade {username} failed. Timeout exceed."
        self.code = 463
        self.message = message
        super().__init__(message, *args, **kwargs)


class ComradeAuthenticationError(BaseMitmException):
    def __init__(self, message=None, username=None, *args, **kwargs):
        if not message:
            self.message = f"Authentication comrade {username} failed."
        self.code = 464
        self.message = message
        super().__init__(message, *args, **kwargs)
