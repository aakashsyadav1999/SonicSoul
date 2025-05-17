from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
import os
from src.models.chatbot import ChatModel

load_dotenv(find_dotenv())

app = FastAPI()

chat_model = ChatModel(api_key=os.getenv("GOOGLE_GEMINI_KEY"))

# Request schemas
class TextInput(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "Chatbot API running"}

@app.post("/predict-sentiment")
def predict_sentiment(input: TextInput):
    sentiment = chat_model.classify_sentiment(input.text)
    return {"sentiment": sentiment}

@app.post("/chat")
def chat(input: TextInput):
    reply = chat_model.chat(input.text)
    return {"reply": reply}
