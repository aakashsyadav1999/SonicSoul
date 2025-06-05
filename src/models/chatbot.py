import google.generativeai as genai
from typing import List
import json


class ChatModel:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.client = genai

    def classify_sentiment(self, message: str) -> str:
        """Classify the sentiment/mood of a message into one of our supported categories"""
        
        # Comprehensive mood keywords dictionary
        mood_keywords = {
            'positive': {
                'happy', 'joy', 'excited', 'great', 'wonderful', 'love', 'amazing', 'good', 'fantastic',
                'awesome', 'glad', 'delighted', 'pleased', 'grateful', 'blessed', 'thrilled', 'cheery',
                'beautiful', 'brilliant', 'success', 'win', 'proud', 'perfect', 'smile', 'laugh'
            },
            'negative': {
                'sad', 'angry', 'upset', 'terrible', 'bad', 'hate', 'awful', 'disappointed', 'frustrated',
                'depressed', 'worried', 'anxious', 'stressed', 'hurt', 'pain', 'miserable', 'sick',
                'tired', 'lost', 'fear', 'lonely', 'heartbroken', 'crying', 'mad', 'annoyed'
            },
            'energetic': {
                'pumped', 'energized', 'hyped', 'active', 'dynamic', 'party', 'dance', 'workout', 'run',
                'exercise', 'power', 'strong', 'fire', 'fast', 'rush', 'action', 'move', 'jump',
                'bounce', 'racing', 'alive', 'motivated', 'lets go', 'ready', 'energy'
            },
            'relaxed': {
                'calm', 'peaceful', 'chill', 'relax', 'quiet', 'gentle', 'soothing', 'mellow', 'tranquil',
                'rest', 'zen', 'serene', 'harmony', 'slow', 'smooth', 'easy', 'meditation', 'mindful',
                'cozy', 'comfortable', 'content', 'still', 'settled', 'soft', 'dreamy'
            }
        }

        print(f"\n[Sentiment Analysis] Input message: '{message}'")
        
        # First try keyword matching
        message_lower = message.lower()
        for mood, keywords in mood_keywords.items():
            # Count how many keywords match
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches >= 2:  # If multiple keywords match, we have high confidence
                print(f"[Sentiment Analysis] Strong keyword matches ({matches}) for mood: {mood}")
                return mood

        # If no strong keyword matches, try LLM
        prompt = (
            "Analyze the emotional content of this message and classify it into EXACTLY ONE mood category.\n"
            "Important Guidelines:\n"
            "1. POSITIVE mood: For strong happiness, joy, love, satisfaction, achievement\n"
            "   Examples: 'Just got promoted!', 'This is the best day ever!'\n"
            "2. NEGATIVE mood: For sadness, anger, anxiety, disappointment, frustration\n"
            "   Examples: 'Everything is going wrong today', 'I can't stand this'\n"
            "3. ENERGETIC mood: For high energy, enthusiasm, excitement, dynamic activity\n"
            "   Examples: 'Time to hit the gym!', 'Let's party all night!'\n"
            "4. RELAXED mood: For calmness, peace, contentment, mellowness\n"
            "   Examples: 'Enjoying a quiet evening', 'So peaceful here'\n"
            "5. Use NEUTRAL only if there is truly NO emotional content\n"
            "   Example: 'What's the weather forecast?'\n\n"
            "Only output one word: positive, negative, energetic, relaxed, or neutral\n"
            "Consider context and intensity of emotions carefully.\n\n"
            f"Message to analyze: '{message}'\n\n"
            "Classification:"
        )

        try:
            response = self.client.GenerativeModel("gemini-2.0-flash").generate_content(
                contents=[prompt],
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 10,
                    "top_p": 0.95,
                    "top_k": 40
                }
            )

            # Extract and clean up the response
            raw_response = response.text.strip().lower()
            print(f"[Sentiment Analysis] Raw model response: '{raw_response}'")
                
            # Map common variations to standard moods
            mood_mappings = {
                'happy': 'positive', 'joyful': 'positive', 'excited': 'positive',
                'sad': 'negative', 'angry': 'negative', 'upset': 'negative',
                'calm': 'relaxed', 'peaceful': 'relaxed', 'chill': 'relaxed',
                'energized': 'energetic', 'active': 'energetic', 'hyped': 'energetic'
            }
            
            sentiment = mood_mappings.get(raw_response, raw_response)
            print(f"[Sentiment Analysis] Mapped sentiment: '{sentiment}'")
            
            supported_moods = {"positive", "negative", "neutral", "energetic", "relaxed"}
            if sentiment not in supported_moods:
                print(f"[Sentiment Analysis] WARNING: Unsupported sentiment '{sentiment}'")
                # Try single keyword matching as a fallback
                for mood, keywords in mood_keywords.items():
                    if any(keyword in message_lower for keyword in keywords):
                        sentiment = mood
                        print(f"[Sentiment Analysis] Fallback keyword match: {mood}")
                        break
                else:
                    sentiment = 'neutral'
                    print("[Sentiment Analysis] No keyword matches, defaulting to neutral")
            
            print(f"[Sentiment Analysis] Final sentiment: '{sentiment}'")
            return sentiment

        except Exception as e:
            print(f"[Sentiment Analysis] Error in LLM processing: {str(e)}")
            # Try simple keyword matching as fallback
            for mood, keywords in mood_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    print(f"[Sentiment Analysis] Error fallback keyword match: {mood}")
                    return mood
            
            print("[Sentiment Analysis] No keywords matched, using neutral")
            return "neutral"

    def chat(self, message: str) -> str:
        prompt = (
            "You are a helpful assistant. "
            "Respond to the user's message in a friendly and informative manner.\n\n"
            f"User: {message}\nAssistant:"
        )
        response = self.client.GenerativeModel("gemini-2.0-flash").generate_content(
            contents=[prompt],
            generation_config={
                "temperature": 0.0,
                "max_output_tokens": 150,
                "top_p": 1.0,
                "top_k": 40
            }
        )
        reply = response.text.strip()
        return reply