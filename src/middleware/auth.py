import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import os
import sys
import json
from dotenv import load_dotenv, find_dotenv
from src.exceptions.spotify_exceptions import SpotifyAuthError

# Add the project root directory to the Python path
project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_path not in sys.path:
    sys.path.append(project_root_path)

from src.database import get_database_connection

load_dotenv(find_dotenv())

def get_client_credentials_spotify():
    """
    Get a Spotify client using client credentials flow.
    This doesn't require user authentication but has limited access.
    """
    try:
        client_id = os.getenv('SPOTIPY_CLIENT_ID')
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

        if not all([client_id, client_secret]):
            print("Missing Spotify credentials in environment")
            return None

        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        
        return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
    except Exception as e:
        print(f"Error creating client credentials client: {e}")
        return None

def _fetch_new_spotify_token_and_save(username: str, auth_manager: SpotifyOAuth) -> spotipy.Spotify | None:
    """
    Initiates a new Spotify authorization flow.
    Returns None and raises SpotifyAuthError with auth URL for frontend to handle.
    """
    try:
        # First try client credentials as fallback
        sp = get_client_credentials_spotify()
        if sp:
            print("Using client credentials flow as fallback")
            return sp
            
        # If that fails, proceed with full auth flow
        auth_url = auth_manager.get_authorize_url()
        print(f"Spotify Authorization URL: {auth_url}")
        
        raise SpotifyAuthError(
            message="Please authorize with Spotify",
            auth_url=auth_url
        )

    except SpotifyAuthError:
        raise
    except Exception as e:
        print(f"Error in auth flow: {e}")
        return None

def _refresh_token(username: str, auth_manager: SpotifyOAuth, token_info: dict) -> tuple[bool, spotipy.Spotify | None]:
    """
    Attempts to refresh an expired token.
    Returns (success, spotify_client)
    """
    try:
        if not auth_manager.is_token_expired(token_info):
            return True, spotipy.Spotify(auth=token_info['access_token'])
            
        # Token expired, try to refresh
        new_token = auth_manager.refresh_access_token(token_info['refresh_token'])
        print("Successfully refreshed token")
        
        # Save new token
        conn = get_database_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE users SET spotify_access_token = %s WHERE username = %s",
                (json.dumps(new_token), username)
            )
            conn.commit()
            print("Saved refreshed token to database")
        finally:
            cursor.close()
            conn.close()
            
        return True, spotipy.Spotify(auth=new_token['access_token'])
        
    except Exception as e:
        print(f"Token refresh failed: {e}")
        return False, None

def get_spotify_client(username: str) -> spotipy.Spotify | None:
    """
    Retrieves a Spotify client for the user.
    First tries the database token, then attempts refresh, 
    then client credentials, finally initiates new auth.
    """
    try:
        client_id = os.getenv('SPOTIPY_CLIENT_ID')
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI', 'http://localhost:8502/callback')

        if not all([client_id, client_secret]):
            print("Missing Spotify credentials in environment")
            raise ValueError("Spotify API credentials not configured")
            
        print(f"Initializing Spotify auth for user: {username}")

        # First try client credentials as quick fallback
        sp = get_client_credentials_spotify()
        if sp:
            print("Using client credentials flow")
            return sp

        # If we need user auth, proceed with full flow
        print(f"Using redirect URI: {redirect_uri}")
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope='user-library-read playlist-read-private',
            cache_path=f".spotify_cache_{username}",
            show_dialog=True
        )

        # Try to get token from database
        token_info = None
        try:
            conn = get_database_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT spotify_access_token FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result and result[0]:
                print(f"Found token in database for: {username}")
                token_info = json.loads(result[0])
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            token_info = None
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        # If we have a token, try to use it or refresh it
        if token_info:
            success, sp = _refresh_token(username, auth_manager, token_info)
            if success:
                try:
                    sp.current_user()
                    print("Successfully verified token")
                    return sp
                except Exception as e:
                    print(f"Token verification failed: {e}")
            
        # If we get here, we need new authorization
        print(f"Initiating new auth flow for: {username}")
        return _fetch_new_spotify_token_and_save(username, auth_manager)

    except SpotifyAuthError:
        # Re-raise for frontend to handle
        raise
    except Exception as e:
        print(f"Unexpected error in get_spotify_client: {str(e)}")
        # Try client credentials one last time
        return get_client_credentials_spotify()

def spotify_login(username: str) -> spotipy.Spotify | None:
    """
    Entry point for Spotify login flow.
    Handles getting/refreshing tokens and new auth if needed.
    """
    try:
        print(f"Starting Spotify login for: {username}")
        return get_spotify_client(username)
            
    except SpotifyAuthError as auth_error:
        # Re-raise for frontend to handle redirect
        raise
    except Exception as e:
        print(f"Error in spotify_login: {str(e)}")
        return None

def get_user_playlists(sp):
    """Get user's Spotify playlists"""
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
    # Example usage, assuming a username is available.
    test_username = "testuser" 
    print(f"Attempting to get Spotify client for {test_username}...")
    # Use the new primary function
    sp = get_spotify_client(test_username)
    
    if sp:
        print(f"Spotify client initialized for {test_username}.")
        # Verify token by making a simple call
        try:
            user_profile = sp.current_user()
            print(f"Successfully fetched profile for: {user_profile['display_name']}")
            
            playlists = get_user_playlists(sp)
            if playlists:
                print(f"Found {len(playlists)} playlists for {test_username}:")
                for playlist in playlists[:5]: # Print first 5
                    print(f"  - {playlist['name']}")
            else:
                print(f"No playlists found for {test_username}.")
        except Exception as e:
            print(f"Error using Spotify client for {test_username}: {e}")
    else:
        print(f"Failed to initialize Spotify client for {test_username}.")

if __name__ == '__main__':
    main()