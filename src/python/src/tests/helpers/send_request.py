import requests


def send_httpbin_request(comrade_user, comrade_password):
    proxy = {
        "https": f"http://{comrade_user}:{comrade_password}@127.0.0.1:8081",
        "http": f"http://{comrade_user}:{comrade_password}@127.0.0.1:8081",
    }

    response = requests.get("http://httpbin.org/ip", proxies=proxy)
    return response


def send_httpsbin_request(comrade_user, comrade_password):
    proxy = {
        "https": f"http://{comrade_user}:{comrade_password}@127.0.0.1:8081",
        "http": f"http://{comrade_user}:{comrade_password}@127.0.0.1:8081",
    }

    response = requests.get("https://httpbin.org/ip", proxies=proxy)
    return response
