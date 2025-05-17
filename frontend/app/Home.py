import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os

# Add the project root directory to the Python path
project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) # Corrected path to be 'd:\\vscode\\SonicSoul'
sys.path.append(project_root_path)
# from chatbot.app.main import predict_sentiment
import requests
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())



st.set_page_config(page_title="SonicSoul Home", page_icon="🎵", layout="wide")

# Sidebar with feature icons
with st.sidebar:
    selected = option_menu(
        "Features",
        [
            "Home",
            "AI Playlist Recommender",
            "Chat with Assistant",
            "Upload",
            "Playlists",
            "Search",
            "Settings",
            "About"
        ],  
        icons=[
            "house",
            "robot",
            "music-note-list",
            "cloud-upload",
            "list-ul",
            "search",
            "gear",
            "info-circle"
        ],
        menu_icon="cast",
        default_index=0,
    )

st.title("🎵 SonicSoul")
st.subheader("Your AI-powered music companion")

if selected == "Home":
    st.markdown("## AI Music Playlist Recommender")
    st.write(
        """
        Welcome to **SonicSoul** — an AI-based music playlist recommender system that detects your mood and recommends the perfect playlist!
        """
    )
    st.markdown("### Key Features")
    st.markdown(
        """
        - **Multi-Modal Emotion Detection**  
            - Text Input (BERT, RoBERTa via Hugging Face)
            - Voice Input (Google Speech-to-Text + NLP)
            - Image Input (Facial Expression via DeepFace/FER+/OpenCV)
        - **Chatbot Integration**  
            - Interactive chatbot UI (OpenAI GPT or Dialogflow)
            - Collects text, voice, or image input
        - **Music Recommendation**  
            - Recommends playlists based on detected emotion
            - Integrates with Spotify or YouTube
        - **Clean, Modern UI**  
            - Text input, mic button, image upload/webcam
            - Displays detected emotion and recommended playlist
        """
    )
    st.markdown("---")
    st.info("Select 'AI Playlist Recommender' from the sidebar to try the emotion-based music recommender chatbot!")
elif selected == "AI Playlist Recommender":
    st.header("AI Playlist Recommender")
    st.write(
        """
        Detect your mood using text, voice, or image, and get a personalized playlist!
        """
    )
    st.markdown(
        """
        - **Text Input:** Type how you feel
        - **Voice Input:** Speak your mood (speech-to-text)
        - **Image Input:** Upload a selfie or use your webcam
        """
    )

    user_text_input = st.text_input("Enter text to analyze sentiment:")
    if user_text_input:
        try:
            response = requests.post("http://chatbot:5000/predict", json={"text": user_text_input})
            if response.status_code == 200:
                sentiment = response.json()['sentiment']
                st.success(f"Predicted Sentiment: {sentiment}")
            else:
                st.error("Failed to get sentiment prediction.")
        except Exception as e:
            st.error(f"API call failed: {e}")

elif selected == "Chat with Assistant":
    st.header("Chat with SonicSoul Assistant")
    chat_input = st.text_input("You:", key="chat_input")
    if chat_input:
        response = requests.post("http://chatbot:5000/chat", json={"text": chat_input})
        if response.status_code == 200:
            st.markdown(f"**Assistant:** {response.json()['reply']}")
        else:
            st.error("Failed to get a response from the assistant.")

    st.info("This is a prototype. Emotion detection uses only pretrained models. Music is recommended via Spotify or YouTube.")
elif selected == "Music Library":
    st.write("Browse your music library here.")
elif selected == "Upload":
    st.write("Upload your favorite tracks.")
elif selected == "Playlists":
    st.write("Manage and play your playlists.")
elif selected == "Search":
    st.write("Search for songs, artists, or albums.")
elif selected == "Settings":
    st.write("Adjust your preferences and settings.")
elif selected == "About":
    st.write("SonicSoul - Powered by AI. Version 1.0")

st.markdown("---")
st.info("Select a feature from the sidebar to get started!")

# To run this app, install dependencies:
# pip install streamlit streamlit-option-menu
# Then run: streamlit run /D:/vscode/SonicSoul/frontend/app/Home.py