import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os
import requests
from dotenv import load_dotenv, find_dotenv
from typing import Dict, List

# Initialize session for making requests
session = requests.Session()

# Configure retry strategy
retries = requests.adapters.Retry(
    total=5,
    backoff_factor=0.1,
    status_forcelist=[500, 502, 503, 504]
)
session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))

# Load environment variables
load_dotenv(find_dotenv())

# Service URLs
CHATBOT_URL = os.getenv('CHATBOT_URL', 'http://localhost:5000')
MUSIC_RECOMMENDER_URL = os.getenv('MUSIC_RECOMMENDER_URL', 'http://localhost:8000')

# Initialize database connection status
DB_AVAILABLE = True

# Try to import database functions
try:
    # Add the project root directory to the Python path
    project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.append(project_root_path)
    from src.database import get_database_connection, check_user_cred
except Exception as e:
    print(f"Database connection failed: {e}")
    DB_AVAILABLE = False

# Set up Streamlit page
st.set_page_config(page_title="SonicSoul Home", page_icon="🎵", layout="wide")

# --- Session State Defaults ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'selected' not in st.session_state:
    st.session_state.selected = "Home"
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = not DB_AVAILABLE

# --- LOGIN PAGE LOGIC ---
if not st.session_state.logged_in:
    st.title("Login to SonicSoul")

    if not DB_AVAILABLE:
        st.warning("⚠️ Database connection unavailable. Running in demo mode.")
        if st.button("Continue in Demo Mode"):
            st.session_state.logged_in = True
            st.session_state.username = "demo_user"
            st.session_state.selected = "Home"
            st.session_state.demo_mode = True
            st.rerun()
    else:
        # Input fields for username and password
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            try:
                # Connect to the database
                conn = get_database_connection()
                cursor = conn.cursor()

                # Check if user credentials are correct
                if check_user_cred(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.selected = "Home"
                    st.success("Login successful! Initializing Spotify...")

                    # Initialize Spotify connection
                    if check_spotify_connection():
                        st.success("Connected to Spotify!")
                    else:
                        st.warning("Using limited Spotify functionality")
                    
                    cursor.close()
                    conn.close()
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
                    cursor.close()
                    conn.close()
            except Exception as e:
                st.error("Database connection error. Try demo mode instead.")
                st.session_state.demo_mode = True
                if st.button("Switch to Demo Mode"):
                    st.session_state.logged_in = True
                    st.session_state.username = "demo_user"
                    st.session_state.selected = "Home"
                    st.rerun()

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
    st.write("Share how you're feeling, and I'll recommend the perfect music for your mood!")
    st.markdown(
        """
        - **How it works:**  
          1. Enter how you're feeling in the text box below
          2. AI will analyze your mood
          3. Get personalized music recommendations based on your mood!
        """
    )

    # Get available moods for reference
    try:
        moods_response = session.get(f"{MUSIC_RECOMMENDER_URL}/available-moods")
        if moods_response.status_code == 200:
            available_moods = moods_response.json()["moods"]
            st.info(f"Supported moods: {', '.join(available_moods)}")
    except Exception as e:
        st.warning(f"Could not fetch available moods: {str(e)}")

    user_text_input = st.text_input("Tell me how you're feeling:")
    if user_text_input:
        try:
            # First, predict sentiment using chatbot service
            sentiment_response = session.post(
                f"{CHATBOT_URL}/predictsentiment", 
                json={"text": user_text_input}
            )
            
            if sentiment_response.status_code == 200:
                sentiment = sentiment_response.json()['sentiment']
                st.success(f"I sense that you're feeling: {sentiment}")
                
                # Then, get music recommendations using the detected mood
                try:
                    print(f"Requesting recommendations for mood: {sentiment}")
                    recommendations_response = session.post(
                        f"{MUSIC_RECOMMENDER_URL}/recommend",
                        json={"mood": sentiment.lower(), "username": st.session_state.username}
                    )
                    
                    if recommendations_response.status_code == 200:
                        tracks = recommendations_response.json()
                        st.subheader("🎵 Your Personalized Playlist")
                        for track in tracks:
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"**{track['name']}** by {', '.join(track['artists'])}")
                                if track['preview_url']:
                                    st.audio(track['preview_url'])
                            with col2:
                                st.markdown(f"[Open in Spotify]({track['external_url']})")
                            st.divider()
                    elif recommendations_response.status_code == 401:
                        st.error("Spotify service unavailable. Please try again later.")
                    else:
                        error_msg = recommendations_response.json().get('detail', 'Unknown error occurred')
                        st.error(f"Could not get music recommendations: {error_msg}")
                        print(f"Error response from music recommender: {recommendations_response.text}")
                        # Show supported moods if available
                        try:
                            moods_response = session.get(f"{MUSIC_RECOMMENDER_URL}/available-moods")
                            if moods_response.status_code == 200:
                                available_moods = moods_response.json()["moods"]
                                st.info(f"Hint: Try expressing how you feel using one of these moods: {', '.join(available_moods)}")
                        except Exception:
                            pass
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Network error occurred: {str(e)}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")
                    print(f"Unexpected error in recommendation flow: {str(e)}")
            else:
                st.error("Failed to analyze your mood. Please try again.")
        except Exception as e:
            st.error(f"API call failed: {e}")
            
        st.markdown("---")
        st.info("💡 Not seeing what you like? Try expressing your mood differently or check out the Voice and Image recommenders!")
            
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

def init_spotify():
    """Initialize Spotify service connection"""
    return check_spotify_connection()

def check_spotify_connection():
    """Check if Spotify service is available and working"""
    try:
        response = session.get(f"{MUSIC_RECOMMENDER_URL}/spotify/check")
        if response.status_code == 200:
            return True
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            print(f"Spotify connection check failed: {error_msg}")  # Debug log
            return False
    except Exception as e:
        print(f"Error checking Spotify connection: {str(e)}")  # Debug log
        st.error(f"Spotify service error: {str(e)}")
        return False

def process_spotify_error(response):
    """Handle Spotify service errors"""
    try:
        error_data = response.json().get("detail", "Unknown error")
        st.error(f"Spotify service error: {error_data}")
    except Exception as e:
        st.error(f"Error processing response: {str(e)}")

def get_recommendations(username: str, mood: str):
    """Get music recommendations with simplified error handling"""
    try:
        response = session.post(
            f"{MUSIC_RECOMMENDER_URL}/recommend",
            json={"username": username, "mood": mood},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = response.json().get('detail', 'Unknown error occurred')
            st.error(f"Could not get music recommendations: {error_msg}")
            return None
            
    except Exception as e:
        st.error(f"Connection error: Please make sure all services are running")
        print(f"Error details: {str(e)}")
        return None

def show_home_page():
    st.title("SonicSoul - Music for Every Mood 🎵")
    
    # Check if user is logged in
    if "username" not in st.session_state:
        st.warning("Please log in to access music recommendations")
        return
    
    # Check Spotify connection
    if not check_spotify_connection():
        st.error("Unable to connect to Spotify service. Please try again later.")
        return
    
    # Display main content
    show_mood_selection()
    
def show_mood_selection():
    """Display mood selection and handle recommendations"""
    st.subheader("How are you feeling today?")
    
    # Text input for mood description
    user_text_input = st.text_input("Tell me how you're feeling:", key="mood_input")
    
    # Show available moods as reference
    try:
        moods_response = session.get(f"{MUSIC_RECOMMENDER_URL}/available-moods")
        if moods_response.status_code == 200:
            available_moods = moods_response.json()["moods"]
            st.info(f"I can understand these moods: {', '.join(available_moods)}")
    except Exception:
        pass

    if user_text_input:
        try:
            # First, predict sentiment using chatbot service
            sentiment_response = session.post(
                f"{CHATBOT_URL}/predictsentiment",
                json={"text": user_text_input}
            )

            if sentiment_response.status_code == 200:
                sentiment = sentiment_response.json()['sentiment']
                st.success(f"I sense that you're feeling: {sentiment}")

                # Get recommendations based on detected mood
                response = session.post(
                    f"{MUSIC_RECOMMENDER_URL}/recommend",
                    json={"mood": sentiment.lower(), "username": st.session_state.username}
                )

                if response.status_code == 200:
                    recommendations = response.json()
                    display_recommendations(recommendations)
                else:
                    st.error("Failed to get recommendations. Please try again.")
                    if response.status_code == 404:
                        st.info("Hint: Try expressing your mood differently - I understand positive, negative, neutral, energetic, and relaxed feelings best.")
            else:
                st.error("Failed to analyze your mood. Please try again.")

        except Exception as e:
            st.error(f"Error getting recommendations: {str(e)}")
            print(f"Recommendation error details: {str(e)}")  # Debug log

def display_recommendations(recommendations):
    """Display the recommended tracks in a nice format"""
    if not recommendations:
        st.warning("No recommendations available at the moment.")
        return
        
    st.subheader("Your Personalized Recommendations")
    
    for track in recommendations:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if track.get("album_image"):
                st.image(track["album_image"], width=100)
        
        with col2:
            st.write(f"**{track['name']}**")
            st.write(f"Artist: {track['artists'] if isinstance(track.get('artists'), list) else track.get('artist', 'Unknown')}")
            st.write(f"Album: {track.get('album', 'Unknown')}")
            if track.get("preview_url"):
                st.audio(track["preview_url"])
            if track.get("external_url"):
                st.markdown(f"[Open in Spotify]({track['external_url']})")
            
        st.markdown("---")
