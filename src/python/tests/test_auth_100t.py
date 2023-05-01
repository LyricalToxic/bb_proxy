from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase

from src.python.tests.utils.send_request import send_httpbin_request, send_httpsbin_request


class TestAuth100T(TestCase):

    def test_http_correct_cred(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            for _ in range(100):
                executor.submit(self._test_http_correct_cred)

    def _test_http_correct_cred(self):
        comrade_user = "mario"
        comrade_password = "mario"
        response = send_httpbin_request(comrade_user, comrade_password)
        print(response.status_code)
        self.assertEqual(200, response.status_code)

    def test_https_correct_cred(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            for _ in range(100):
                executor.submit(self._test_http_correct_cred)

    def _test_https_correct_cred(self):
        comrade_user = "mario"
        comrade_password = "mario"
        response = send_httpsbin_request(comrade_user, comrade_password)
        self.assertEqual(200, response.status_code)
