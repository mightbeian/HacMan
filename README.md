# 🎯 HacMan - ML-Powered CTF Platform

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)

An intelligent Capture-The-Flag platform that uses Machine Learning to dynamically adjust challenge difficulty and provide contextual hints to players.

## 🚀 Features

### Core Functionality
- **Multiple Challenge Categories**: Web Exploits, Cryptography, Steganography, Forensics, Binary Exploitation
- **Dynamic Difficulty Adjustment**: ML model predicts optimal next challenge based on player performance
- **AI-Generated Hints**: NLP-powered hint system that summarizes relevant concepts
- **Real-time Leaderboard**: Competitive scoring with ranks and badges
- **Player Analytics Dashboard**: Track progress, completion times, and skill development

### Technical Features
- JWT-based authentication & authorization
- RESTful API with comprehensive documentation
- Real-time chat and collaboration features
- Challenge flag validation with anti-cheat measures
- Performance metrics tracking (completion time, attempts, hint usage)
- Automated difficulty prediction using Random Forest classifier

## 🏗️ Architecture

### Backend (Django REST Framework)
- **Authentication**: JWT tokens with refresh mechanism
- **Challenge Management**: CRUD operations for CTF challenges
- **ML Integration**: Scikit-learn models for difficulty prediction
- **NLP Hints**: Transformers-based hint generation
- **Database**: PostgreSQL with optimized queries

### Frontend (React)
- **Modern UI**: Material-UI components with responsive design
- **State Management**: React Context + Hooks
- **Real-time Updates**: WebSocket integration for live features
- **Code Editor**: Monaco editor for challenge solving

## 📦 Tech Stack

### Backend
- Python 3.9+
- Django 4.2+
- Django REST Framework
- PostgreSQL 14+
- Scikit-learn
- Transformers (Hugging Face)
- Celery (async tasks)
- Redis (caching & queuing)

### Frontend
- React 18+
- Material-UI (MUI)
- Axios
- React Router
- Monaco Editor
- Chart.js

### ML/AI
- Random Forest Classifier (difficulty prediction)
- BERT-based models (hint generation)
- Performance metrics analysis

## 🛠️ Installation

### Prerequisites
```bash
# Python 3.9+
python --version

# Node.js 18+
node --version

# PostgreSQL 14+
psql --version

# Redis (optional, for caching)
redis-server --version
```

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/mightbeian/HacMan.git
cd HacMan
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configure database**
```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE hacman_db;
CREATE USER hacman_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hacman_db TO hacman_user;
\q
```

5. **Set environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. **Run migrations**
```bash
python manage.py migrate
python manage.py createsuperuser
```

7. **Load sample challenges**
```bash
python manage.py loaddata challenges.json
```

8. **Train ML models**
```bash
python manage.py train_models
```

9. **Start backend server**
```bash
python manage.py runserver
```

### Frontend Setup

1. **Install dependencies**
```bash
cd ../frontend
npm install
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with backend API URL
```

3. **Start development server**
```bash
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## 📚 API Documentation

### Authentication
```bash
# Register
POST /api/auth/register/
{
  "username": "player1",
  "email": "player1@example.com",
  "password": "securepass123"
}

# Login
POST /api/auth/login/
{
  "username": "player1",
  "password": "securepass123"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Challenges
```bash
# List challenges
GET /api/challenges/

# Get challenge details
GET /api/challenges/{id}/

# Submit flag
POST /api/challenges/{id}/submit/
{
  "flag": "FLAG{example_flag_here}"
}

# Get hint
GET /api/challenges/{id}/hint/
```

### Player Stats
```bash
# Get player dashboard
GET /api/player/dashboard/

# Get leaderboard
GET /api/leaderboard/

# Get recommended challenges
GET /api/player/recommendations/
```

## 🤖 ML Model Details

### Difficulty Predictor
The platform uses a Random Forest classifier trained on:
- Player's completion rate
- Average solve time per category
- Hint usage patterns
- Error rate trends
- Skill progression curve

### Hint Generator
Utilizes a fine-tuned BERT model to:
- Analyze challenge description and category
- Extract key concepts and techniques
- Generate progressive hints (vague → specific)
- Avoid spoiling the solution

## 🎮 Usage Guide

### For Players
1. **Register/Login** to create your account
2. **Browse Challenges** in different categories
3. **Solve Challenges** and submit flags
4. **Request Hints** if stuck (costs points)
5. **Track Progress** on your dashboard
6. **Compete** on the leaderboard

### For Administrators
1. Access admin panel at `/admin`
2. Create new challenges with flags
3. Set difficulty tiers and point values
4. Monitor player activity and statistics
5. Manage user accounts and permissions

## 🧪 Challenge Categories

### Web Exploitation
- SQL Injection
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Authentication Bypass
- Server-Side Template Injection

### Cryptography
- Classical Ciphers
- RSA Challenges
- Hash Functions
- Encoding/Decoding
- Stream/Block Ciphers

### Steganography
- Image Steganography
- Audio Steganography
- LSB Analysis
- Metadata Extraction

### Forensics
- Memory Analysis
- Network Packet Analysis
- File Recovery
- Log Analysis

### Binary Exploitation
- Buffer Overflow
- Format String Vulnerabilities
- Return-Oriented Programming
- Reverse Engineering

## 🔒 Security Considerations

- Challenges run in isolated Docker containers
- Input validation on all user submissions
- Rate limiting on API endpoints
- Secure flag storage with encryption
- Anti-cheat mechanisms (time tracking, submission patterns)
- Regular security audits

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Adding New Challenges

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on creating challenges.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Christian Paul Cabrera** - *Initial work* - [mightbeian](https://github.com/mightbeian)

## 🙏 Acknowledgments

- Inspired by platforms like HackTheBox, TryHackMe, and picoCTF
- ML models powered by Scikit-learn and Hugging Face
- Community contributors and challenge creators

## 📞 Support

For support, email cabrera.cpaul@gmail.com or open an issue on GitHub.

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Team-based competitions
- [ ] Live CTF events
- [ ] Advanced analytics dashboard
- [ ] Integration with external CTF platforms
- [ ] Docker-based challenge deployment
- [ ] Blockchain-based achievement system
- [ ] AI-powered challenge generation

---

**Happy Hacking! 🎯**