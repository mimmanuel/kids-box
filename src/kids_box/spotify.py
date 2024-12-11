import json
import os
from typing import Any

import requests
from dotenv import load_dotenv

_ = load_dotenv()

SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

SPOTIFY_SCOPE = (
    "user-read-currently-playing user-read-playback-state user-modify-playback-state"
)

# Global variables for token storage
access_token: str | None = None
refresh_token: str | None = None

with open("tokens.txt", "r") as file:
    refresh_token = file.readline().strip('\n')

async def exchange_code_for_tokens(code: str) -> dict[str, str]:
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv('SPOTIFY_REDIRECT_URI'),
        "client_id": os.getenv('SPOTIFY_CLIENT_ID'),
        "client_secret": os.getenv('SPOTIFY_CLIENT_SECRET'),
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise Exception(
            f"Failed to exchange code for tokens. Status Code: {response.status_code}"
        )

    try:
        json_response: dict[str, str] = response.json()

        assert "access_token" in json_response
        assert "refresh_token" in json_response

        return json_response
    except ValueError as e:
        raise Exception(f"Failed to parse JSON: {e}")

async def parse_tokens(code: str) -> None:
    # Exchange code for tokens
    token_data = await exchange_code_for_tokens(code)

    # Store tokens securely
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    assert access_token is not None
    assert refresh_token is not None

    # Save tokens to file (for demonstration purposes only)
    save_tokens_to_file(refresh_token)



def save_tokens_to_file(refresh_token: str | None):
    with open("tokens.txt", "w") as file:
        _ = file.write(f"{refresh_token}")


def refresh_access_token():
    global access_token, refresh_token

    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }

    print(json.dumps(data))

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        global access_token
        access_token = response.json()["access_token"]
    else:
        raise Exception(
            f"Failed to refresh access token. Status Code: {response.status_code}: {response.text}"
        )


def get_devices() -> list[dict[str, Any]]:
    """Get available devices"""
    global access_token

    if not access_token:
        refresh_access_token()

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to get devices. Status Code: {response.status_code}: {response.text}")

    json_response = response.json()

    assert "devices" in json_response

    return json_response["devices"]

def start_song(device_id: str):
    # Aqua
    # spotify:track:5ZrDlcxIDZyjOzHdYW1ydr

    global access_token

    if not access_token:
        refresh_access_token()

    json = {"uris": [ "spotify:track:5ZrDlcxIDZyjOzHdYW1ydr"]}

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    response = requests.put(f"https://api.spotify.com/v1/me/player/play?device_id={device_id}", headers=headers, json=json)

    print(response.status_code)

    if not response.status_code == 204:
        raise Exception(f"Could not start track: Status code: {response.status_code}: {response.text}")

def get_authorize_url() -> str:
    authorize_url = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}&scope={SPOTIFY_SCOPE}"

    return authorize_url



def is_authenticated() -> bool:
    global refresh_token

    return refresh_token is not None
