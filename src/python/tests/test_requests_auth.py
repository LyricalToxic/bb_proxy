import time
from threading import Thread

from cmdline.bbc_server import run_server
from src.python.tests.utils.send_request import send_httpbin_request, send_httpsbin_request
from utils.containers import ComradeCredential


class TestRequestsAuth:

    def test_http_correct_cred(self, credentials: ComradeCredential):
        thread = Thread(target=run_server)
        thread.start()
        time.sleep(5)
        response = send_httpbin_request(credentials)
        assert 200 == response.status_code


    def test_https_correct_cred(self, credentials: ComradeCredential):
        run_server()
        response = send_httpsbin_request(credentials)
        assert 200 == response.status_code
