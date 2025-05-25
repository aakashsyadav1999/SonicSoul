import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import sys
import json
from dotenv import load_dotenv, find_dotenv

# Add the project root directory to the Python path
project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root_path not in sys.path:
    sys.path.append(project_root_path)

from src.database import get_database_connection

load_dotenv(find_dotenv())

def _fetch_new_spotify_token_and_save(username: str, auth_manager: SpotifyOAuth) -> spotipy.Spotify | None:
    try:
        auth_url = auth_manager.get_authorize_url()
        print(f"Authorize here:\n{auth_url}\n")
        redirected_response = input("Paste the full redirect URL here:\n")

        code = auth_manager.parse_response_code(redirected_response)
        if not code:
            print("Could not parse authorization code.")
            return None

        token_info = auth_manager.get_cached_token()
        if not token_info:
            code = auth_manager.get_authorization_code()
            token_info = auth_manager.get_access_token(code)
        
        # Check if we got the token info
        access_token = token_info.get("access_token")

        if access_token:
            print(f"Access token fetched for user {username}")

            # Store only the access_token
            try:
                conn = get_database_connection()
                cursor = conn.cursor()
                cursor.execute(
                                "UPDATE users SET spotify_access_token = %s WHERE username = %s",
                                (access_token, username)
                            )
                conn.commit()
                print(f"Access token saved to DB for {username}")
            except Exception as e:
                print(f"DB Error: {e}")
            finally:
                if cursor: cursor.close()
                if conn: conn.close()

            return spotipy.Spotify(auth=access_token)
        else:
            print("Access token not received.")
            return None

    except Exception as e:
        print(f"Error fetching token: {e}")
        return None

def get_spotify_client(username: str) -> spotipy.Spotify | None:
    """
    Retrieves a Spotify client for the user.
    It tries to load and refresh an existing token from the DB,
    otherwise, it fetches a new one.
    """
    client_id = os.getenv('SPOTIPY_CLIENT_ID')
    client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
    redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

    if not all([client_id, client_secret, redirect_uri]):
        print("Spotify API credentials (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI) are not fully configured.")
        raise ValueError("Spotify API credentials are not fully configured.")

    cache_path = f".spotify_cache_{username}"
    scope = 'user-library-read playlist-read-private'

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=cache_path,
        show_dialog=False, # Initially false, only show dialog if explicitly fetching new
        open_browser=True
    )

    token_info_str = None
    conn_db = None
    cursor_db = None
    try:
        conn_db = get_database_connection()
        cursor_db = conn_db.cursor()
        # Use %s placeholder for pymysql
        query = "SELECT spotify_token_info FROM Users WHERE username = %s"
        cursor_db.execute(query, (username,)) # Changed to pass username as a tuple
        result = cursor_db.fetchone()
        if result and result[0]:
            token_info_str = result[0]
    except Exception as e:
        print(f"Error fetching token from DB for {username}: {e}")
    finally:
        if cursor_db: cursor_db.close()
        if conn_db: conn_db.close()

    if token_info_str:
        print(f"Token found in DB for user {username}.")
        token_info = json.loads(token_info_str)
        print(f"--- Token Info from DB for {username} ---")
        print(json.dumps(token_info, indent=2))
        print("---------------------------------------")
        
        # Load token into auth_manager's cache to allow refresh and validation
        auth_manager.cache_handler.save_token_to_cache(token_info)

        if auth_manager.is_token_expired(token_info):
            print(f"Token for {username} is expired. Attempting refresh.")
            try:
                refreshed_token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
                print(f"Token for {username} refreshed successfully.")
                token_info = refreshed_token_info # Use the new token
                print(f"--- Refreshed Token Info for {username} ---")
                print(json.dumps(token_info, indent=2))
                print("-----------------------------------------")
                
                conn_save, cursor_save = None, None
                try:
                    conn_save = get_database_connection()
                    cursor_save = conn_save.cursor()
                    # Use %s placeholder for pymysql
                    sql_update = "UPDATE Users SET spotify_token_info = %s WHERE username = %s"
                    # Ensure parameters are passed as a tuple
                    cursor_save.execute(sql_update, (json.dumps(token_info), username))
                    conn_save.commit()
                    print(f"Refreshed token for {username} saved to DB.")
                    auth_manager.cache_handler.save_token_to_cache(token_info) # Update cache
                except Exception as e_save:
                    print(f"Error saving refreshed token to DB for {username}: {e_save}")
                finally:
                    if cursor_save: cursor_save.close()
                    if conn_save: conn_save.close()
            except spotipy.SpotifyOauthError as e_refresh:
                print(f"Could not refresh token for {username}: {e_refresh}. Fetching new token.")
                # Force new auth by setting show_dialog true for the fetch function
                auth_manager.show_dialog = True
                return _fetch_new_spotify_token_and_save(username, auth_manager)
            except Exception as e_generic_refresh:
                print(f"Generic error during token refresh for {username}: {e_generic_refresh}. Fetching new token.")
                auth_manager.show_dialog = True
                return _fetch_new_spotify_token_and_save(username, auth_manager)
        
        # If token was not expired, or was successfully refreshed and is now in token_info
        print(f"Using existing/refreshed token for {username}.")
        return spotipy.Spotify(auth_manager=auth_manager) # auth_manager has the token via cache
    else:
        print(f"No token in DB for {username}. Fetching new token.")
        auth_manager.show_dialog = True # Ensure dialog for initial token fetch
        return _fetch_new_spotify_token_and_save(username, auth_manager)

def get_user_playlists(sp):
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