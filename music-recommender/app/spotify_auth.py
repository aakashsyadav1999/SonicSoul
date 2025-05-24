import os
from requests import post,get
import json
import requests
from dotenv import load_dotenv, find_dotenv
import base64
import sys


load_dotenv(find_dotenv())
SPOTIPY_CLIENT_ID = '1ff1ebf6e6cb4efda5737e5e8ccdb601'
SPOTIPY_CLIENT_SECRET = '0cd37ba112244531a323e62604ca3cc5'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/callback'


SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID', '1ff1ebf6e6cb4efda5737e5e8ccdb601')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET', '0cd37ba112244531a323e62604ca3cc5')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI', 'http://127.0.0.1:8000/callback')

def get_token():

    auth_string = f"{SPOTIPY_CLIENT_ID}:{SPOTIPY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode('utf-8')

    # Base 64 encode the client ID and secret
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    result = post(url, headers=headers, data=data)
    print(result)
    json_result = result.json()
    if 'access_token' not in json_result:
        print("Failed to get access token:", json_result)
        return None
    token = json_result['access_token']
    return token

token = get_token()


def get_auth(token):
    return {
        'Authorization': f'Bearer ' + token
        }
    

def search_for_artist(token, artist_name):
    url = f"https://api.spotify.com/v1/search"
    headers = get_auth(token)
    query = f"?q={artist_name}&type=artist&limit1"
    
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    print(json_result)
    
search_for_artist(token, "The Beatles")
