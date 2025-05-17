import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv

# Set up path to access src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models.chatbot import ChatModel

# Load environment variables
load_dotenv(find_dotenv())

# Initialize FastAPI
app = FastAPI()

# Load your model once during startup
chat_model = ChatModel(api_key=os.getenv("GOOGLE_GEMINI_KEY"))

# Define request body schema
class InputText(BaseModel):
    text: str

@app.post("/predict")
def predict_sentiment(payload: InputText):
    sentiment = chat_model.classify_sentiment(payload.text)
    return {"sentiment": sentiment}