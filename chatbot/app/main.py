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

# Request schemas
class TextInput(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "Chatbot API running"}

@app.post("/predictsentiment")
def predict_sentiment(input: TextInput):
    sentiment = chat_model.classify_sentiment(input.text)
    return {"sentiment": sentiment}

@app.post("/chat")
def chat(input: TextInput):
    reply = chat_model.chat(input.text)
    return {"reply": reply}
