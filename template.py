import os
import sys

# This script creates a directory structure for a project with the specified files.
list_of_files = [
    "docker-compose.yml",
    "README.md",
    ".env",
    "src/__init__.py",
    "src/config.py",
    "src/database.py",
    "src/models/__init__.py",
    "src/models/user.py",
    "src/models/voice.py",
    "src/models/text.py",
    "src/models/image.py",
    "src/models/chatbot.py",
    "src/models/music.py",
    "src/models/emotion.py",
    "src/routes/__init__.py",
    "src/routes/user.py",
    "src/routes/voice.py",
    "src/routes/text.py",
    "src/routes/image.py",
    "src/routes/chatbot.py",
    "src/routes/music.py",
    "src/routes/emotion.py",
    "src/utils/__init__.py",
    "src/utils/common.py",
    "src/exceptions/__init__.py",
    "src/exceptions/custom_exceptions.py",
    "src/logging/__init__.py",
    "src/logging/logger.py",
    "src/middleware/__init__.py",
    "src/middleware/auth.py",
    "src/middleware/error_handler.py",
    "src/middleware/response_handler.py",
    "src/middleware/validation.py",
    "src/middleware/rate_limiter.py",
    "src/middleware/cors.py",
    "src/middleware/security.py",
    "src/middleware/monitoring.py",
    "src/middleware/metrics.py",
    "src/middleware/health_check.py",
    "src/middleware/maintenance.py",
    "src/middleware/feature_flag.py",
    "src/middleware/ab_testing.py",
    "src/middleware/feature_toggle.py",
    "src/middleware/feature_branching.py",
    "emotion-text/app/main.py",
    "emotion-text/Dockerfile",
    "emotion-text/requirements.txt",
    "emotion-voice/app/main.py",
    "emotion-voice/Dockerfile",
    "emotion-voice/requirements.txt",
    "emotion-image/app/main.py",
    "emotion-image/Dockerfile",
    "emotion-image/requirements.txt",
    "chatbot/app/main.py",
    "chatbot/Dockerfile",
    "chatbot/requirements.txt",
    "music-recommender/app/main.py",
    "music-recommender/Dockerfile",
    "music-recommender/requirements.txt",
    "frontend/app/Home.py",
    "frontend/app/utils.py",
    "frontend/Dockerfile",
    "frontend/requirements.txt",
]

# Create project directory
def create_files():
    for file in list_of_files:
        directory = os.path.dirname(file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write('')
            print(f'Created {file}')
        else:
            print(f'{file} already exists')
        
create_files()