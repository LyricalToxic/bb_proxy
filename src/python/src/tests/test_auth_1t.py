from unittest import TestCase

from tests.helpers.send_request import send_httpbin_request, send_httpsbin_request


class TestAuth1T(TestCase):

    def test_http_correct_cred(self):
        comrade_user = "mario"
        comrade_password = "mario"
        response = send_httpbin_request(comrade_user, comrade_password)
        self.assertEqual(200, response.status_code)

    def test_https_correct_cred(self):
        comrade_user = "mario"
        comrade_password = "mario"
        response = send_httpsbin_request(comrade_user, comrade_password)
        self.assertEqual(200, response.status_code)
