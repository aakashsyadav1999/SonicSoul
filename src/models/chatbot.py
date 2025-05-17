import google.generativeai as genai


class ChatModel:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.client = genai

    def classify_sentiment(self, message: str) -> str:
        prompt = (
            "To help me pick the right songs, could you tell me if this message feels Positive, Negative, or Neutral? "
            "Just the overall mood would be great, thanks!\n\n"
            f"Message: {message}"
        )
        response = self.client.GenerativeModel("gemini-2.0-flash").generate_content(
            contents=[prompt],
            generation_config={
                "temperature": 0.0,
                "max_output_tokens": 10,
                "top_p": 1.0,
                "top_k": 40
            }
        )
        sentiment = response.text.strip()
        return sentiment

    def chat(self, message: str) -> str:
        prompt = (
            "You are a helpful assistant. "
            "Respond to the user's message in a friendly and informative manner.\n\n"
            f"User: {message}\nAssistant:"
        )
        response = self.client.GenerativeModel("gemini-2.0-flash").generate_content(
            contents=[prompt],
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 150,
                "top_p": 1.0,
                "top_k": 40
            }
        )
        reply = response.text.strip()
        return reply