from mitmproxy.http import Response
from mitmproxy.net.http import status_codes


class BaseBBException(Exception):
    code: int = 449
    message: str = "Something went wrong on mitmproxy side."
    headers: dict = {}

    def reply_response(self):
        body = self.message
        return Response.make(
            status_code=self.code,
            content=body,
            headers={"Content-Type": "text/html", **self.headers}
        )


class EmptyComradeAuthHeader(BaseBBException):

    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = "`Proxy-Authorization` header is empty, please enter username and password."
        self.code = status_codes.PROXY_AUTH_REQUIRED
        self.message = (
            f"<html>"
            f"<head><title>{self.code} {message}</title></head>"
            f"<body><h1>{self.code} {message}</h1></body>"
            f"</html>"
        )
        self.headers = {"Proxy-Authenticate": 'Basic realm="bb-proxy"'}
        super().__init__(message, *args, **kwargs)


class IncorrectComradeAuthHeader(BaseBBException):
    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = "`Proxy-Authorization` header has incorrect format." \
                      "Please enter username and password with following format:" \
                      "`Basic base64encode(%username%, %password%)`"
        self.code = 461
        self.message = message
        super().__init__(message, *args, **kwargs)


class ComradeIdentificationError(BaseBBException):
    def __init__(self, message=None, username=None, *args, **kwargs):
        if not message:
            message = f"Cannot identify comrade. Not found comrade with username {username}"
        self.code = 462
        self.message = message
        super().__init__(message, *args, **kwargs)


class TimeoutIdentificationError(BaseBBException):
    def __init__(self, message=None, username=None, *args, **kwargs):
        if not message:
            message = f"Identification comrade {username} failed. Timeout exceed."
        self.code = 463
        self.message = message
        super().__init__(message, *args, **kwargs)


class ComradeAuthenticationError(BaseBBException):
    def __init__(self, message=None, username=None, *args, **kwargs):
        if not message:
            message = f"Authentication comrade {username} failed."
        self.code = 464
        self.message = message
        super().__init__(message, *args, **kwargs)
