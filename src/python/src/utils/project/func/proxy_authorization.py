import base64
from typing import Tuple, Optional, Union

from mitmproxy.http import Response, Request

from exceptions import IncorrectComradeAuthHeader
from utils.constans import PROXY_AUTHORIZATION_HEADER


def encode_proxy_auth_header(username: str, password: str):
    cred = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
    return f"Basic {cred}"


def decode_proxy_auth_header(auth_header_value: str) -> Tuple[str, str]:
    try:
        _basic, encoded_cred = auth_header_value.split(" ")
        decoded_cred = base64.b64decode(encoded_cred).decode("utf-8")
        username, password = decoded_cred.split(":")
        return username, password
    except Exception:
        raise IncorrectComradeAuthHeader()


def extract_proxy_auth_header(response_or_request: Union[Request, Response]) -> Optional[str]:
    auth_value_standard = response_or_request.headers.get(PROXY_AUTHORIZATION_HEADER)
    # puppeteer send auth header key in lower register
    auth_value_lower = response_or_request.headers.get(PROXY_AUTHORIZATION_HEADER.lower())
    return auth_value_standard or auth_value_lower
