FROM python:3.10-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY music-recommender/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a symlink to fix Python module imports
RUN ln -s /app/music-recommender /app/music_recommender

# Add an enhanced debug script to check environment and Spotify credentials before starting
RUN echo '#!/bin/bash\n\
echo "==== ENVIRONMENT DIAGNOSTICS ===="\n\
echo "Current directory: $(pwd)"\n\
echo "Directory listing:"\n\
ls -la\n\
echo "Python path:"\n\
python -c "import sys; print(sys.path)"\n\
echo "Checking Spotify environment variables:"\n\
python -c "import os; print(f\"SPOTIPY_CLIENT_ID available: {bool(os.environ.get(\"SPOTIPY_CLIENT_ID\"))}\")" \n\
python -c "import os; print(f\"SPOTIPY_CLIENT_SECRET available: {bool(os.environ.get(\"SPOTIPY_CLIENT_SECRET\"))}\")" \n\
echo "Testing Spotify auth:"\n\
python -c "import sys; sys.path.append(\"/app\"); from music_recommender.app.spotify_auth import get_token; token = get_token(); print(f\"Token obtained: {bool(token)}\")" || echo "Failed to test token" \n\
echo "==== STARTING SERVICE ===="\n\
exec "$@"' > /start.sh && chmod +x /start.sh

# Use the debug script as an entrypoint
ENTRYPOINT ["/start.sh"]
CMD ["uvicorn", "music_recommender.app.main:app", "--host", "0.0.0.0", "--port", "5001", "--log-level", "debug"]