import base64
from typing import Tuple


def encode_proxy_auth_header(username: str, password: str):
    cred = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
    return f"Basic {cred}"


def decode_proxy_auth_header(auth_header_value: str) -> Tuple[str, str]:
    try:
        _basic, encoded_cred = auth_header_value.split(" ")
        decoded_cred = base64.b64decode(encoded_cred).decode("utf-8")
        username, password = decoded_cred.split(":")
        return username, password
    except Exception as e:
        raise
