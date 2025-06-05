# chatbot/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

COPY chatbot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["uvicorn", "chatbot.app.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]