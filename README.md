# 🎵 SonicSoul - AI-Powered Emotion-Based Music Recommendation Platform

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-green)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-red)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-containerized-blue)](https://docker.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 📖 Overview

**SonicSoul** is an innovative AI-powered music recommendation platform that understands your emotions and curates personalized music experiences. By analyzing emotions through multiple channels - text, voice, and images - SonicSoul creates a unique musical journey tailored to your current mood and preferences.

### 🌟 Key Features

- **🤖 AI-Powered Chatbot**: Interactive conversation with emotion detection using Google Gemini
- **🎯 Multi-Modal Emotion Analysis**: 
  - Text sentiment analysis
  - Voice emotion recognition (planned)
  - Image-based emotion detection (planned)
- **🎵 Smart Music Recommendations**: Spotify integration with mood-based playlist generation
- **👤 User Management**: Secure authentication and personalized profiles
- **📊 Analytics Dashboard**: User mood tracking and listening patterns
- **🔄 Real-time Processing**: Live emotion analysis and instant music recommendations
- **🌐 Modern Web Interface**: Streamlit-based responsive frontend

## 🏗️ Architecture

SonicSoul follows a microservices architecture with the following components:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                    │
│                   Port: 8502                               │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┬─────────────┐
    │             │             │             │             │
┌───▼───┐    ┌───▼───┐    ┌───▼───┐    ┌───▼───┐    ┌───▼───┐
│Chatbot│    │Music  │    │Emotion│    │Emotion│    │Emotion│
│Service│    │Recomm │    │Text   │    │Voice  │    │Image  │
│:5000  │    │:5001  │    │(Soon) │    │(Soon) │    │(Soon) │
└───┬───┘    └───┬───┘    └───────┘    └───────┘    └───────┘
    │            │
    └────────────┼─────────────────────────────────────────────┐
                 │                                             │
            ┌────▼────┐                                   ┌────▼────┐
            │ MySQL   │                                   │ Spotify │
            │Database │                                   │   API   │
            │ :3307   │                                   │         │
            └─────────┘                                   └─────────┘
```

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Spotify Developer Account
- Google Gemini API Key

### Environment Setup

1. **Clone the repository:**
```bash
git clone https://github.com/aakashsyadav1999/SonicSoul.git
cd SonicSoul
```

2. **Set up environment variables:**
Create a `.env` file in the root directory:
```env
# Spotify Configuration
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8502/callback

# Google Gemini AI
GOOGLE_GEMINI_KEY=your_gemini_api_key

# Database Configuration
DB_HOST=mysql
DB_USER=ray
DB_PASSWORD=advicr49
DB_NAME=music_prediction_db
DB_PORT=3306

# Service URLs
CHATBOT_URL=http://chatbot:5000
MUSIC_RECOMMENDER_URL=http://music-recommender:5001
```

3. **Launch with Docker Compose:**
```bash
docker-compose up --build
```

4. **Access the application:**
- Frontend: http://localhost:8502
- Chatbot API: http://localhost:5000
- Music Recommender API: http://localhost:5001
- MySQL Database: localhost:3307

### Manual Setup (Development)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up MySQL database:**
```bash
# Start MySQL and run the initialization script
mysql -u root -p < mysql/init.sql
```

3. **Run services individually:**
```bash
# Terminal 1 - Chatbot Service
cd chatbot
python app/main.py

# Terminal 2 - Music Recommender
cd music-recommender
python app/main.py

# Terminal 3 - Frontend
cd frontend
streamlit run app/Home.py --server.port 8501
```

## 🎯 Current Features

### ✅ Implemented

- **User Authentication System**
  - Secure login/registration
  - Session management
  - Demo mode for testing

- **AI Chatbot**
  - Google Gemini integration
  - Emotion classification from text
  - Mood mapping to music genres
  - Natural conversation flow

- **Music Recommendation Engine**
  - Spotify API integration
  - Mood-based playlist generation
  - Real-time track suggestions
  - User preference learning

- **Database Management**
  - MySQL with user profiles
  - Music preference storage
  - Listening history tracking

- **Web Interface**
  - Responsive Streamlit frontend
  - Real-time chat interface
  - Music player integration
  - User dashboard

### 🔧 Core Components

#### Chatbot Service (`/chatbot`)
- **Technology**: FastAPI + Google Gemini AI
- **Features**: 
  - Text sentiment analysis
  - Mood classification (positive, negative, energetic, relaxed, neutral)
  - Context-aware responses
  - Health monitoring

#### Music Recommender (`/music-recommender`)
- **Technology**: FastAPI + Spotify API
- **Features**:
  - Spotify authentication
  - Mood-based track recommendations
  - Playlist generation
  - Audio feature analysis

#### Frontend (`/frontend`)
- **Technology**: Streamlit
- **Features**:
  - Interactive chat interface
  - Music player
  - User authentication
  - Dashboard analytics

## 🔮 Future Roadmap

### 📅 Phase 1 (Q3 2025) - Enhanced Emotion Analysis
- **Voice Emotion Recognition**
  - Real-time voice analysis
  - Emotion detection from audio input
  - Voice-to-text integration
  - Speaker emotion profiling

- **Image-Based Emotion Detection**
  - Facial expression analysis
  - Computer vision integration
  - Real-time camera processing
  - Photo emotion analysis

### 📅 Phase 2 (Q4 2025) - Advanced Features
- **Machine Learning Enhancement**
  - Collaborative filtering
  - Deep learning recommendation models
  - User behavior prediction
  - Personalized emotion modeling

- **Social Features**
  - Mood sharing
  - Friend recommendations
  - Social playlists
  - Community mood trends

### 📅 Phase 3 (Q1 2026) - Platform Expansion
- **Multi-Platform Support**
  - Mobile app development
  - API marketplace
  - Third-party integrations
  - Cross-platform synchronization

- **Advanced Analytics**
  - Mood analytics dashboard
  - Music discovery insights
  - Personalized reports
  - Trend analysis

### 📅 Phase 4 (Q2 2026) - AI Evolution
- **Advanced AI Features**
  - Multi-modal emotion fusion
  - Predictive mood modeling
  - Context-aware recommendations
  - Emotion-driven content creation

## 🛠️ Technical Stack

### Backend Services
- **FastAPI**: High-performance Python web framework
- **Google Gemini AI**: Advanced language model for emotion analysis
- **Spotify Web API**: Music streaming and recommendation
- **MySQL**: Relational database for user data
- **Docker**: Containerization and deployment

### Frontend
- **Streamlit**: Interactive web application framework
- **Python**: Core programming language
- **HTML/CSS**: Custom styling and layouts

### DevOps & Infrastructure
- **Docker Compose**: Multi-container orchestration
- **MySQL**: Database management
- **Environment Variables**: Configuration management
- **Health Checks**: Service monitoring

## 📊 Monitoring & Analytics

### Health Monitoring
- Service health checks
- Database connectivity monitoring
- API response time tracking
- Error rate monitoring

### User Analytics
- Mood pattern analysis
- Music preference tracking
- Usage statistics
- Recommendation accuracy metrics

## 🤝 Contributing

We welcome contributions to SonicSoul! Here's how you can help:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Ensure Docker compatibility

## 📄 API Documentation

### Chatbot API
- `GET /`: Health check
- `POST /analyze_sentiment`: Analyze text emotion
- `POST /chat`: Interactive conversation

### Music Recommender API
- `GET /`: Health check
- `POST /recommend`: Get mood-based recommendations
- `GET /track/{track_id}`: Get track details
- `POST /playlist/create`: Create custom playlist

## 🔒 Security & Privacy

- **Data Encryption**: All sensitive data encrypted
- **Secure Authentication**: Token-based authentication
- **Privacy First**: User data protection compliance
- **API Security**: Rate limiting and validation

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/aakashsyadav1999/SonicSoul/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aakashsyadav1999/SonicSoul/discussions)
- **Email**: [your-email@example.com](mailto:your-email@example.com)
- **LinkedIn**: [Your LinkedIn Profile](https://linkedin.com/in/your-profile)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for advanced language processing
- **Spotify** for comprehensive music data API
- **Streamlit** for rapid frontend development
- **FastAPI** for high-performance backend services
- **Docker** for seamless deployment
- **Open Source Community** for continuous inspiration

---

### 🌟 Star this repository if you find SonicSoul helpful!

**Made with ❤️ by [Aakash Yadav]**

*SonicSoul - Where AI meets music, and emotions find their perfect soundtrack.*