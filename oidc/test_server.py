import contextlib
import io
import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import HTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

import server


class CallbackTests(unittest.TestCase):
    def setUp(self):
        self.httpd = HTTPServer(("127.0.0.1", 0), server.Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.start()
        self.addCleanup(self.close_server)

    def close_server(self):
        self.httpd.shutdown()
        self.thread.join()
        self.httpd.server_close()

    def get(self, path):
        connection = HTTPConnection(*self.httpd.server_address, timeout=5)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_login_redirect(self):
        status, headers, _ = self.get("/login")
        self.assertEqual(status, 302)
        location = urlparse(headers["Location"])
        self.assertEqual(
            location.scheme + "://" + location.netloc + location.path,
            server.ISSUER + "/protocol/openid-connect/auth",
        )
        params = parse_qs(location.query)
        self.assertEqual(params["client_id"], ["oidc-test"])
        self.assertEqual(params["redirect_uri"], ["http://localhost:3000/callback"])
        self.assertEqual(params["response_type"], ["code"])
        self.assertEqual(params["scope"], ["openid email profile"])
        self.assertNotIn("code_challenge", params)

    def test_callback_exchanges_code_and_displays_tokens_in_browser(self):
        tokens = {"access_token": "sample-access", "id_token": "sample-id"}
        output = io.StringIO()
        with patch("server.urlopen") as exchange, contextlib.redirect_stdout(output):
            exchange.return_value.__enter__.return_value = io.BytesIO(
                json.dumps(tokens).encode()
            )
            status, headers, body = self.get("/callback?code=sample-code")
        self.assertEqual(status, 200)
        request = exchange.call_args.args[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(
            request.full_url, server.ISSUER + "/protocol/openid-connect/token"
        )
        self.assertEqual(parse_qs(request.data.decode()), {
            "grant_type": ["authorization_code"],
            "client_id": ["oidc-test"],
            "code": ["sample-code"],
            "redirect_uri": ["http://localhost:3000/callback"],
        })
        self.assertIn(b"Access token:\nsample-access", body)
        self.assertIn(b"ID token:\nsample-id", body)
        self.assertEqual(headers["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(output.getvalue(), "")

    def test_missing_code_and_provider_denial(self):
        with patch("server.urlopen") as exchange, patch("sys.stderr", io.StringIO()):
            for path in ("/callback", "/callback?error=access_denied"):
                with self.subTest(path=path):
                    status, _, _ = self.get(path)
                    self.assertEqual(status, 400)
            exchange.assert_not_called()

    def test_failed_or_incomplete_token_response(self):
        error = HTTPError("https://example.test/token", 400, "Bad Request", {}, None)
        with patch("server.urlopen", side_effect=error), \
                patch("sys.stderr", io.StringIO()), \
                patch("sys.stdout", io.StringIO()) as output:
            status, _, body = self.get("/callback?code=bad-code")
            self.assertEqual(status, 502)
            self.assertIn(b"400", body)
            self.assertEqual(output.getvalue(), "")

        with patch("server.urlopen") as exchange, \
                patch("sys.stderr", io.StringIO()), \
                patch("sys.stdout", io.StringIO()) as output:
            exchange.return_value.__enter__.return_value = io.BytesIO(b"{}")
            status, _, _ = self.get("/callback?code=sample-code")
            self.assertEqual(status, 502)
            self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
