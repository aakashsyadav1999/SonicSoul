from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from src.middleware.auth import get_spotify_client, spotify_login

router = APIRouter()

class SpotifyCallback(BaseModel):
    code: str
    state: str | None = None

@router.get("/callback")
async def spotify_callback(request: Request, code: str, state: str | None = None):
    """Handle the Spotify OAuth callback"""
    try:
        # Get the username from session state or query params
        username = request.session.get("username")
        if not username:
            raise HTTPException(status_code=400, detail="No active session found")
            
        # Process the callback and get a new client
        sp = spotify_login(username)
        if not sp:
            raise HTTPException(
                status_code=401, 
                detail="Failed to authenticate with Spotify"
            )
            
        return {"message": "Successfully authenticated with Spotify"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication error: {str(e)}"
        )

@router.post("/spotify/refresh")
async def refresh_spotify_token(request: Request):
    """Refresh the Spotify token for the current user"""
    try:
        username = request.session.get("username")
        if not username:
            raise HTTPException(status_code=400, detail="No active session found")
            
        sp = spotify_login(username)
        if not sp:
            raise HTTPException(
                status_code=401,
                detail="Failed to refresh Spotify token"
            )
            
        return {"message": "Successfully refreshed Spotify token"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Token refresh error: {str(e)}"
        )
