import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os
import requests
from dotenv import load_dotenv, find_dotenv


# Add the project root directory to the Python path
project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root_path)
from src.database import get_database_connection, check_user_cred
from src.middleware.auth import get_spotify_client, get_user_playlists # Changed get_spotify_token to get_spotify_client

# Load environment variables
load_dotenv(find_dotenv())

# Set up Streamlit page
st.set_page_config(page_title="SonicSoul Home", page_icon="🎵", layout="wide")

# --- Session State Defaults ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'selected' not in st.session_state:
    st.session_state.selected = "Home"

# --- LOGIN PAGE LOGIC ---
if not st.session_state.logged_in:
    st.title("Login to SonicSoul")

    # Input fields for username and password
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            # Connect to the MSSQL database
            conn = get_database_connection()
            cursor = conn.cursor()

            # Check if user credentials are correct
            if check_user_cred(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username # Save username in session state
                st.session_state.selected = "Home"  # Set default page after login
                st.success("Login successful! Redirecting...")

                # Attempt to get Spotify client after successful login
                try:
                    print(f"Attempting to get Spotify client for user: {username}")
                    sp = get_spotify_client(username) # Changed to get_spotify_client
                    if sp:
                        st.session_state.spotify_client = sp
                        st.success("Spotify client initialized successfully.")
                        # Optionally, fetch playlists immediately or defer to when needed
                        # user_playlists = get_user_playlists(sp)
                        # st.session_state.user_playlists = user_playlists
                    else:
                        st.warning("Could not initialize Spotify client. Please ensure you have authorized the app and check logs.")
                except ValueError as ve:
                    st.error(f"Spotify Configuration Error: {ve}")
                except Exception as e:
                    st.error(f"An error occurred during Spotify authentication: {e}")

                cursor.close()
                conn.close()
                st.rerun()  # Simulate redirect
            else:
                st.error("Invalid username or password.")
                cursor.close()
                conn.close()
        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.stop()  # Prevent the rest of the page from rendering if not logged in

# --- SIDEBAR MENU ---
with st.sidebar:
    selected = option_menu(
        "Features",
        [
            "Home",
            "AI Text Playlist Recommender",
            "AI Voice Playlist Recommender",
            "AI Image Playlist Recommender",
            "Chat with Assistant",
            "About",
        ],
        icons=[
            "house",
            "robot",
            "music-note-list",
            "cloud-upload",
            "list-ul",
            "search",
            "gear",
            "info-circle",
        ],
        menu_icon="cast",
        default_index=[
            "Home",
            "AI Text Playlist Recommender",
            "AI Voice Playlist Recommender",
            "AI Image Playlist Recommender",
            "Chat with Assistant",
            "About",
        ].index(st.session_state.selected),
    )
    st.session_state.selected = selected

# --- MAIN PAGE CONTENT ---
st.title("🎵 SonicSoul")
st.subheader("Your AI-powered music companion")

if st.session_state.selected == "Home":
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

elif st.session_state.selected == "AI Text Playlist Recommender":
    st.header("AI Playlist Recommender")
    st.write("Detect your mood using text, voice, or image, and get a personalized playlist!")
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
            response = requests.post("http://chatbot:5000/predictsentiment", json={"text": user_text_input})
            if response.status_code == 200:
                sentiment = response.json()['sentiment']
                st.success(f"Predicted Sentiment: {sentiment}")
            else:
                st.error("Failed to get sentiment prediction.")
        except Exception as e:
            st.error(f"API call failed: {e}")
            
elif st.session_state.selected == "AI Voice Playlist Recommender":
    st.header("Chat with SonicSoul Assistant")
    chat_input = st.text_input("You:", key="chat_input")
    if chat_input:
        try:
            response = requests.post("http://chatbot:5000/voice", json={"text": chat_input})
            if response.status_code == 200:
                st.markdown(f"**Assistant:** {response.json()['reply']}")
            else:
                st.error("Failed to get a response from the assistant.")
        except Exception as e:
            st.error(f"API call failed: {e}")

elif st.session_state.selected == "AI Image Playlist Recommender":
    st.header("Chat with SonicSoul Assistant")
    chat_input = st.text_input("You:", key="chat_input")
    if chat_input:
        try:
            response = requests.post("http://chatbot:5000/image", json={"text": chat_input})
            if response.status_code == 200:
                st.markdown(f"**Assistant:** {response.json()['reply']}")
            else:
                st.error("Failed to get a response from the assistant.")
        except Exception as e:
            st.error(f"API call failed: {e}")
            
elif st.session_state.selected == "Chat with Assistant":
    st.header("Chat with SonicSoul Assistant")
    chat_input = st.text_input("You:", key="chat_input")
    if chat_input:
        try:
            response = requests.post("http://chatbot:5000/chat", json={"text": chat_input})
            if response.status_code == 200:
                st.markdown(f"**Assistant:** {response.json()['reply']}")
            else:
                st.error("Failed to get a response from the assistant.")
        except Exception as e:
            st.error(f"API call failed: {e}")
            
elif st.session_state.selected == "About":
    st.write("SonicSoul - Powered by AI. Version 1.0")

st.markdown("---")
st.info("Select a feature from the sidebar to get started!")
