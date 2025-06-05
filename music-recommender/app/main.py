from fastapi import FastAPI, HTTPException
import os
import sys
from typing import List, Optional
from pydantic import BaseModel
import spotipy
import json
import random

# Import get_token from your spotify_auth.py
try:
    from .spotify_auth import get_token
except ImportError:
    from spotify_auth import get_token

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    """Root endpoint for health checks"""
    return {"status": "ok", "service": "music-recommender"}

def get_spotify():
    """Initialize Spotify client with client credentials"""
    try:
        print("Attempting to get Spotify access token...")
        access_token = get_token()

        if not access_token:
            print("Failed to get access token from spotify_auth.get_token()")
            raise Exception("Failed to get access token using get_token()")

        print(f"Successfully retrieved token (first 10 chars): {access_token[:10]}...")

        # Initialize Spotify client with the token
        sp = spotipy.Spotify(auth=access_token)
        sp._auth = access_token  # Set the token directly on the client
        sp._session.headers.update({"Authorization": f"Bearer {access_token}"})  # Update headers

        # Log headers for debugging
        print(f"Spotify client headers: {sp._session.headers}")

        print("Spotify client created successfully with direct token")
        return sp

    except Exception as e:
        print(f"Error creating Spotify client: {e}")
        return None
    
    
# Map moods to music characteristics
MOOD_TO_MUSIC_PARAMS = {
    "positive": {
        "seed_genres": ["pop", "dance", "happy"], 
        "limit": 10,
        "target_valence": 0.8
    },
    "negative": {
        "seed_genres": ["sad", "acoustic", "rainy-day"],
        "limit": 10,
        "target_valence": 0.3
    },
    "neutral": {
        "seed_genres": ["indie", "ambient", "chill"],
        "limit": 10,
        "target_valence": 0.5
    },
    "energetic": { 
        "seed_genres": ["electronic", "party", "work-out"],
        "limit": 10,
        "target_energy": 0.8 
    },
    "relaxed": { 
        "seed_genres": ["chill", "sleep", "study"],
        "limit": 10,
        "target_energy": 0.3
    }
}

# Add mood to artist genre mapping
MOOD_TO_ARTIST_GENRES = {
    "positive": ["pop", "dance-pop", "happy hardcore", "tropical house", "edm", "funk", "disco"],
    "negative": ["grunge", "emo", "dark ambient", "gothic metal", "blues", "sad core"],
    "neutral": ["indie rock", "alternative", "ambient", "folk", "indie folk", "indie pop"],
    "energetic": ["electronic", "dubstep", "house", "drum-and-bass", "rock", "metal"],
    "relaxed": ["classical", "ambient", "chillout", "jazz", "new age", "acoustic"]
}

def get_recommendations(sp: spotipy.Spotify, mood_params: dict) -> dict:
    """Get recommendations with error handling and fallback"""
    try:
        print(f"\n=== Getting Recommendations for Mood Parameters: {mood_params} ===")
        
        # Verify Spotify client
        if not sp or not hasattr(sp, '_auth'):
            print("Error: Invalid Spotify client or missing auth token")
            return None

        # Fetch available genres
        available_genres = sp.recommendation_genre_seeds()['genres']
        print(f"Available genre seeds: {available_genres[:5]}...")

        # Validate and filter seed genres
        seed_genres = [g for g in mood_params.get("seed_genres", ["pop"]) if g in available_genres]
        if not seed_genres:
            print("No valid genres found, falling back to 'pop'")
            seed_genres = ["pop"]

        # Build recommendation parameters
        params = {
            "seed_genres": seed_genres[:3],
            "limit": mood_params.get("limit", 20),  # Increased limit for better diversity
            "market": "US"  # Specify market to ensure available tracks
        }
        
        # Add mood-specific parameters
        for param in ["target_valence", "target_energy"]:
            if param in mood_params:
                params[param] = mood_params[param]

        print(f"Making recommendations request with params: {params}")
        recommendations = sp.recommendations(**params)
        
        if recommendations and recommendations.get('tracks'):
            print(f"Successfully got {len(recommendations['tracks'])} recommendations")
            return recommendations
        else:
            print("No tracks found in recommendations response")
            return None

    except Exception as e:
        print(f"Error in get_recommendations: {str(e)}")
        return None

class MoodRequest(BaseModel):
    """Request model for mood-based recommendations"""
    mood: str  # Supported moods: positive, negative, neutral, energetic, relaxed
    username: str = "default"  # Optional username, defaults to "default"

class TrackResponse(BaseModel):
    """Response model for track recommendations"""
    id: str
    name: str
    artists: List[str]
    preview_url: Optional[str]
    external_url: str

# Replace the existing recommend_tracks function

@app.post("/recommend", response_model=List[TrackResponse])
async def recommend_tracks(request: MoodRequest):
    """Get diverse track recommendations based on mood"""
    try:
        print(f"\n=== Getting recommendations for mood: {request.mood} ===")
        
        mood = request.mood.lower()
        if mood not in MOOD_TO_ARTIST_GENRES:  # Use existing MOOD_TO_ARTIST_GENRES for validation
            raise HTTPException(status_code=400, detail=f"Unsupported mood: {mood}")
        
        sp = get_spotify()
        if not sp:
            raise HTTPException(
                status_code=503,
                detail="Could not initialize Spotify client"
            )

        # Get recommendations using mood-based approach
        tracks = get_mood_based_recommendations(sp, mood)
        
        if not tracks:
            raise HTTPException(
                status_code=404,
                detail="No recommendations found for the given mood"
            )

        # Process tracks
        processed_tracks = []
        for track in tracks:  # Changed from diverse_tracks to tracks
            if not track: 
                continue
            try:
                track_data = TrackResponse(
                    id=track["id"],
                    name=track["name"],
                    artists=[artist["name"] for artist in track["artists"]],
                    preview_url=track.get("preview_url"),
                    external_url=track["external_urls"]["spotify"]
                )
                processed_tracks.append(track_data)
            except (KeyError, TypeError) as e:
                print(f"Error processing track data: {e}")
                continue

        if not processed_tracks:
            raise HTTPException(
                status_code=404,
                detail="No suitable tracks found after processing"
            )

        return processed_tracks

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred"
        )

@app.get("/available-moods")
async def get_available_moods():
    """Get list of supported moods"""
    return {"moods": list(MOOD_TO_MUSIC_PARAMS.keys())}

@app.post("/spotify/auth") # This endpoint might be vestigial if only using client_credentials
async def spotify_auth_check(request: MoodRequest): # Renamed from spotify_auth to avoid conflict
    """Check if Spotify client (using client credentials) works"""
    sp = get_spotify()
    if not sp:
        # This indicates a problem with server-side Spotify client setup
        return {
            "auth_required": False, # No user auth, but server-side issue
            "message": "Warning: Server could not initialize Spotify client. Check server logs and credentials."
        }
    try:
        # Make a simple API call to verify Spotify client is working
        available_genres = sp.recommendation_genre_seeds()
        return {
            "auth_required": False,
            "message": "Spotify client credentials are working",
            "genres_count": len(available_genres.get('genres', [])) if available_genres else 0
        }
    except Exception as e:
        print(f"Error testing Spotify client: {e}")
        return {
            "auth_required": False,
            "message": f"Spotify client error: {str(e)}"
        }
        
@app.get("/search")
async def search_artist(query: str):
    """Search for an artist on Spotify"""
    try:
        sp = get_spotify()
        if not sp:
            raise HTTPException(
                status_code=503,  # Service Unavailable
                detail="Could not initialize Spotify client. Spotify service might be down or credentials incorrect."
            )

        # Perform the search
        print(f"Searching for artist: {query}")
        results = sp.search(q=query, type="artist", limit=1)
        if not results or not results.get("artists", {}).get("items"):
            raise HTTPException(
                status_code=404,
                detail=f"No artist found for query: {query}"
            )

        # Extract artist details
        artist = results["artists"]["items"][0]
        return {
            "id": artist["id"],
            "name": artist["name"],
            "genres": artist.get("genres", []),
            "popularity": artist.get("popularity"),
            "followers": artist.get("followers", {}).get("total"),
            "external_url": artist["external_urls"]["spotify"]
        }

    except spotipy.SpotifyException as se:
        print(f"Spotify API error during search: {se}")
        raise HTTPException(
            status_code=se.http_status if hasattr(se, 'http_status') else 500,
            detail=f"Spotify API error: {se.msg if hasattr(se, 'msg') else str(se)}"
        )
    except Exception as e:
        print(f"Unexpected error during search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search for artist: {str(e)}"
        )
        
        
@app.get("/artist/{artist_id}/top-tracks")
async def get_top_tracks(artist_id: str):
    """Fetch an artist's top tracks from Spotify"""
    try:
        print(f"Initializing Spotify client...")
        sp = get_spotify()
        if not sp:
            print("Spotify client initialization failed.")
            raise HTTPException(
                status_code=503,
                detail="Could not initialize Spotify client. Spotify service might be down or credentials incorrect."
            )

        print(f"Fetching top tracks for artist ID: {artist_id}")
        results = sp.artist_top_tracks(artist_id)
        if not results or not results.get("tracks"):
            print(f"No top tracks found for artist ID: {artist_id}")
            raise HTTPException(
                status_code=404,
                detail=f"No top tracks found for artist ID: {artist_id}"
            )

        # Simplified response with only track names
        track_names = [track["name"] for track in results["tracks"]]
        return {"songs": track_names}

    except spotipy.SpotifyException as se:
        print(f"Spotify API error during top tracks fetch: {se}")
        raise HTTPException(
            status_code=se.http_status if hasattr(se, 'http_status') else 500,
            detail=f"Spotify API error: {se.msg if hasattr(se, 'msg') else str(se)}"
        )
    except Exception as e:
        print(f"Unexpected error during top tracks fetch: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch top tracks: {str(e)}"
        )
# Add this after MOOD_TO_MUSIC_PARAMS

def get_diverse_recommendations(sp: spotipy.Spotify, mood_params: dict) -> List[dict]:
    """Get diverse recommendations using seed genres"""
    try:
        recommendations = get_recommendations(sp, mood_params)
        if not recommendations or not recommendations.get('tracks'):
            print("No recommendations found")
            return []

        # Randomly select tracks for diversity
        tracks = recommendations['tracks']
        num_tracks = min(15, len(tracks))  # Get up to 15 tracks
        selected_tracks = random.sample(tracks, num_tracks)
        
        print(f"Selected {len(selected_tracks)} diverse tracks")
        return selected_tracks

    except Exception as e:
        print(f"Error in get_diverse_recommendations: {str(e)}")
        return []

def get_mood_based_recommendations(sp: spotipy.Spotify, mood: str) -> List[dict]:
    """Get recommendations based on mood-appropriate artists"""
    try:
        # Get genres for the mood
        genres = MOOD_TO_ARTIST_GENRES.get(mood.lower(), ["pop"])
        print(f"Using genres for {mood}: {genres}")
        
        # Find artists matching these genres
        artists = get_artists_by_genre(sp, genres)
        if not artists:
            print("No artists found, falling back to default recommendation")
            return get_diverse_recommendations(sp, MOOD_TO_MUSIC_PARAMS[mood])
            
        print(f"Found {len(artists)} artists matching mood genres")
        
        # Get a diverse selection of artists
        selected_artists = random.sample(artists, min(len(artists), 3))
        
        # Collect tracks from each artist
        all_tracks = []
        for artist in selected_artists:
            try:
                print(f"Getting top tracks for: {artist['name']}")
                top_tracks = sp.artist_top_tracks(artist['id'], country='US')
                if top_tracks and top_tracks.get('tracks'):
                    # Get a random selection of this artist's top tracks
                    tracks = top_tracks['tracks']
                    num_tracks = min(5, len(tracks))
                    selected_tracks = random.sample(tracks, num_tracks)
                    all_tracks.extend(selected_tracks)
                    print(f"Added {num_tracks} tracks from {artist['name']}")
            except Exception as e:
                print(f"Error getting tracks for {artist['name']}: {str(e)}")
                continue
                
        if not all_tracks:
            print("No tracks found, falling back to default recommendation")
            return get_diverse_recommendations(sp, MOOD_TO_MUSIC_PARAMS[mood])
            
        # Shuffle and limit the number of tracks
        random.shuffle(all_tracks)
        selected_tracks = all_tracks[:15]
        print(f"Returning {len(selected_tracks)} tracks")
        return selected_tracks
        
    except Exception as e:
        print(f"Error in get_mood_based_recommendations: {str(e)}")
        return []

def get_artists_by_genre(sp: spotipy.Spotify, genres: List[str], limit: int = 10) -> List[dict]:
    """Find artists based on genres"""
    try:
        artists = []
        seen_artists = set()
        
        for genre in genres:
            try:
                # Search for artists in this genre
                results = sp.search(q=f"genre:{genre}", type="artist", limit=limit)
                if results and results["artists"]["items"]:
                    for artist in results["artists"]["items"]:
                        # Check if artist matches the genre
                        artist_genres = set(artist.get("genres", []))
                        if genre in artist_genres and artist["id"] not in seen_artists:
                            artists.append(artist)
                            seen_artists.add(artist["id"])
            except Exception as e:
                print(f"Error searching genre {genre}: {str(e)}")
                continue

        return artists
    except Exception as e:
        print(f"Error in get_artists_by_genre: {str(e)}")
        return []

@app.get("/spotify/check")
async def check_spotify():
    """Check if Spotify service is available and working"""
    try:
        sp = get_spotify()
        if not sp:
            raise HTTPException(
                status_code=503,
                detail="Could not initialize Spotify client"
            )

        # Test the client with a simple API call
        try:
            _ = sp.recommendation_genre_seeds()
            return {"status": "ok", "message": "Spotify service is available"}
        except Exception as e:
            print(f"Error testing Spotify client: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Spotify API error: {str(e)}"
            )

    except Exception as e:
        print(f"Error checking Spotify service: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Spotify service error: {str(e)}"
        )