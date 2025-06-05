import os
import requests
import base64
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

def get_token():
    """
    Get a client credentials token from Spotify API.
    """
    client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("Error: SPOTIPY_CLIENT_ID or SPOTIPY_CLIENT_SECRET not set in environment variables.")
        return None

    # Prepare the data
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    try:
        print("Making Spotify token request...")
        response = requests.post(url, headers=headers, data=data)

        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return None

        json_result = response.json()
        token = json_result.get('access_token')
        if not token:
            print("Failed to get access token. Response:", json_result)
            return None

        print(f"Successfully obtained Spotify token. Expires in {json_result.get('expires_in', 'unknown')} seconds.")
        return token
    except Exception as e:
        print(f"Error during token request: {e}")
        return None