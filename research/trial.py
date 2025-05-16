import spotipy
import spotipy.util as util
import os
import sys
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def get_spotify_token():
    # Set up your Spotify API credentials
    client_id = os.getenv('SPOTIPY_CLIENT_ID')
    client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
    redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
    print(f"Using redirect URI: {redirect_uri}")  # Debug: Print the redirect URI

    # Check if the credentials are set
    if not all([client_id, client_secret, redirect_uri]):
        print("Please set the SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI environment variables.")
        sys.exit(1)

    # Request user authorization
    scope = 'user-library-read'
    token = util.prompt_for_user_token(
        username=os.getenv('SPOTIFY_USERNAME'),
        scope=scope,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
    )

    if not token:
        print("Could not get token for user.")
        sys.exit(1)

    return token

def get_user_playlists(token):
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_playlists(limit=50)
    playlists = results['items']
    
    while results['next']:
        results = sp.next(results)
        playlists.extend(results['items'])

    return playlists

def save_tracks_to_json(tracks, filename='saved_tracks.json'):
    with open(filename, 'w') as f:
        json.dump(tracks, f, indent=4)
    print(f"Saved {len(tracks)} tracks to {filename}")
    
def main():
    token = get_spotify_token()
    playlists = get_user_playlists(token)
    for playlist in playlists:
        print(f"Name: {playlist['name']}")
    #save_tracks_to_json(playlists)
if __name__ == '__main__':
    main()