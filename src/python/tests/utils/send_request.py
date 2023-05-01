import requests
from requests import Response

from utils.containers import ComradeCredential


def send_httpbin_request(credentials: ComradeCredential) -> Response:
    proxy = {
        "http": f"http://{credentials.username}:{credentials.password}@127.0.0.1:8081",
    }
    response = requests.get("http://httpbin.org/ip", proxies=proxy)
    return response


def send_httpsbin_request(credentials: ComradeCredential) -> Response:
    proxy = {
        "https": f"http://{credentials.username}:{credentials.password}@127.0.0.1:8081",
    }
    response = requests.get("https://httpbin.org/ip", proxies=proxy)
    return response
