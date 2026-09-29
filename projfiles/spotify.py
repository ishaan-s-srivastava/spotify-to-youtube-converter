import base64
import hashlib
import os
import secrets
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

if not CLIENT_ID:
    raise RuntimeError("SPOTIFY_CLIENT_ID is missing from .env")

if not REDIRECT_URI:
    raise RuntimeError("SPOTIFY_REDIRECT_URI is missing from .env")

SCOPES = "playlist-read-private playlist-read-collaborative"

def generate_code_verifier():
    return secrets.token_urlsafe(64)


def generate_code_challenge(code_verifier):
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()

    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")

class CallbackHandler(BaseHTTPRequestHandler):

    authorization_code = None
    state = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)

        CallbackHandler.authorization_code = query.get("code", [None])[0]
        CallbackHandler.state = query.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        self.wfile.write(
            b"<h1>Spotify authorization complete.</h1>"
            b"<p>You can close this window.</p>"
        )

    def log_message(self, format, *args):
        pass


class Spotify:

    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.expires_at = 0

    def login(self):

        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)

        state = secrets.token_urlsafe(32)

        params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "state": state,
            "code_challenge_method": "S256",
            "code_challenge": code_challenge,
        }

        authorization_url = (
            "https://accounts.spotify.com/authorize?"
            + urllib.parse.urlencode(params)
        )

        print("Opening Spotify authorization...")
        webbrowser.open(authorization_url)

        self._wait_for_callback(state, code_verifier)

    def _wait_for_callback(self, expected_state, code_verifier):

        server = HTTPServer(
            ("127.0.0.1", 8888),
            CallbackHandler
        )

        print("Waiting for Spotify authorization...")

        while CallbackHandler.authorization_code is None:
            server.handle_request()

        server.server_close()

        if CallbackHandler.state != expected_state:
            raise RuntimeError("OAuth state mismatch.")

        code = CallbackHandler.authorization_code

        self._exchange_code(code, code_verifier)

    def _exchange_code(self, code, code_verifier):

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "client_id": CLIENT_ID,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "code_verifier": code_verifier,
            },
        )

        response.raise_for_status()

        data = response.json()

        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token")

        self.expires_at = time.time() + data["expires_in"]

        print("Spotify authorization successful!")

    def get_playlists(self):
        response = requests.get(
            "https://api.spotify.com/v1/me/playlists",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            }
        )

        response.raise_for_status()

        return response.json()

    def access_playlist(self, chosen_plst):
        url = f"https://api.spotify.com/v1/playlists/{chosen_plst['id']}/items"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])

        # Paginate through all pages using the 'next' URL
        while data.get("next"):
            response = requests.get(data["next"], headers=headers)
            response.raise_for_status()
            data = response.json()
            items.extend(data.get("items", []))

        data["items"] = items
        return data