from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
import os
import sys

project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root_path)
from src.models.chatbot import ChatModel

load_dotenv(find_dotenv())

app = FastAPI()

chat_model = ChatModel(api_key=os.getenv("GOOGLE_GEMINI_KEY"))

# Supported moods mapping
MOOD_MAPPING = {
    "happy": "positive",
    "positive": "positive",
    "excited": "positive",
    "joyful": "positive",
    "content": "positive",
    "sad": "negative",
    "angry": "negative",
    "depressed": "negative",
    "anxious": "negative",
    "calm": "relaxed",
    "peaceful": "relaxed",
    "serene": "relaxed",
    "tired": "relaxed",
    "okay": "neutral",
    "fine": "neutral",
    "normal": "neutral",
    "energized": "energetic",
    "pumped": "energetic",
    "active": "energetic"
}

# Request schemas
class TextInput(BaseModel):
    text: str

@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chatbot"}

@app.get("/health")
def health_check():
    """Dedicated health check endpoint"""
    return {"status": "healthy", "service": "chatbot"}

@app.post("/predictsentiment")
def predict_sentiment(input: TextInput):
    """Predict sentiment and map it to supported moods"""
    try:
        # Input validation
        if not input.text or not input.text.strip():
            print("Empty or whitespace-only input received")
            return {"sentiment": "neutral"}

        # Get raw sentiment from model
        print(f"Input text: {input.text}")  # Debug log
        raw_sentiment = chat_model.classify_sentiment(input.text)
        print(f"Raw sentiment from model: {raw_sentiment}")  # Debug log
        
        # Validate model response
        if raw_sentiment is None:
            print("Model returned None sentiment, using neutral")
            return {"sentiment": "neutral"}
        
        # Map to supported mood
        sentiment = raw_sentiment.lower()  # Ensure lowercase for consistent matching
        print(f"Lowercase sentiment: {sentiment}")  # Debug log
        
        # First try direct mapping
        mapped_sentiment = MOOD_MAPPING.get(sentiment)
        if mapped_sentiment:
            print(f"Direct mapping found: {mapped_sentiment}")
        else:
            # Try general sentiment matching only if we have a valid string
            print(f"No direct mapping found, trying general sentiment matching")
            if any(pos in sentiment for pos in ["happy", "joy", "good", "positive"]):
                mapped_sentiment = "positive"
            elif any(neg in sentiment for neg in ["sad", "angry", "bad", "negative"]):
                mapped_sentiment = "negative"
            elif any(rel in sentiment for rel in ["calm", "peaceful", "relax"]):
                mapped_sentiment = "relaxed"
            elif any(eng in sentiment for eng in ["energy", "active", "pump"]):
                mapped_sentiment = "energetic"
            else:
                mapped_sentiment = "neutral"
            print(f"General mapping result: {mapped_sentiment}")
                
        return {"sentiment": mapped_sentiment}
    except Exception as e:
        print(f"Error in sentiment prediction: {str(e)}")
        return {"sentiment": "neutral"}  # Safe default

@app.post("/chat")
def chat(input: TextInput):
    reply = chat_model.chat(input.text)
    return {"reply": reply}
