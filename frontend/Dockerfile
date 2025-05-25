FROM python:3.11-slim

WORKDIR /app

COPY src ./src
COPY chatbot/app ./chatbot/app 
COPY frontend/app ./frontend/app
COPY frontend/requirements.txt .

RUN apt-get update && \
    apt-get install -y gnupg2 curl && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt
# Add this to your frontend Dockerfile
RUN pip install cryptography

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
