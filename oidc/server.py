import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


ISSUER = "https://radiogenic-rossana-nondefiling.ngrok-free.dev/realms/test"
CLIENT_ID = "oidc-test"
REDIRECT_URI = "http://localhost:3000/callback"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Default request logs would include the authorization code.
        pass

    def reply(self, status, message):
        if status >= 400:
            print(message, file=sys.stderr, flush=True)
        body = message.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/login":
            params = urlencode({
                "client_id": CLIENT_ID,
                "response_type": "code",
                "scope": "openid email profile",
                "redirect_uri": REDIRECT_URI,
            })
            self.send_response(302)
            self.send_header(
                "Location", f"{ISSUER}/protocol/openid-connect/auth?{params}"
            )
            self.end_headers()
            return

        if url.path != "/callback":
            self.reply(404, "Open http://localhost:3000/login to log in.")
            return

        params = parse_qs(url.query)
        if "error" in params:
            self.reply(400, f"Login failed: {params['error'][0]}")
            return
        codes = params.get("code", [])
        if len(codes) != 1:
            self.reply(400, "Callback must contain one authorization code.")
            return

        request = Request(
            f"{ISSUER}/protocol/openid-connect/token",
            data=urlencode({
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "code": codes[0],
                "redirect_uri": REDIRECT_URI,
            }).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                tokens = json.load(response)
        except HTTPError as error:
            self.reply(502, f"Token exchange failed: HTTP {error.code}")
            return
        except (URLError, TimeoutError, ValueError) as error:
            self.reply(502, f"Token exchange failed: {error}")
            return

        if not isinstance(tokens, dict) or not all(
            isinstance(tokens.get(key), str) and tokens[key]
            for key in ("access_token", "id_token")
        ):
            self.reply(502, "Token response is missing an access token or ID token.")
            return

        self.reply(
            200,
            f"Access token:\n{tokens['access_token']}\n\n"
            f"ID token:\n{tokens['id_token']}\n",
        )


if __name__ == "__main__":
    try:
        with HTTPServer(("127.0.0.1", 3000), Handler) as httpd:
            print("Open http://localhost:3000/login in your browser.", flush=True)
            httpd.serve_forever()
    except KeyboardInterrupt:
        pass
