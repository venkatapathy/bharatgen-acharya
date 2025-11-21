# 🎓 BharatGen Yojaka - AI Learning Platform

An intelligent learning platform powered by Django, RAG (Retrieval-Augmented Generation), and Llama 3.1. Features interactive learning paths, AI-powered chat assistance, and personalized recommendations.

## ✨ Features

### 🚀 Core Features
- **Interactive Learning Paths**: Structured AI courses with modules and content
- **AI Chat Assistant**: RAG-powered conversational AI to help with learning
- **Personalized Recommendations**: Smart recommendations based on learning history
- **Progress Tracking**: Comprehensive analytics and progress monitoring
- **User Profiles**: Full authentication with learning preferences
- **Achievement System**: Gamified learning with streaks and milestones

### 🛠️ Technical Highlights
- **Pluggable RAG System**: Easily swap LLM, embedding, or vector store providers
- **Modern UI**: Clean, Google-inspired interface
- **RESTful APIs**: Well-documented Django REST Framework APIs
- **Ollama Integration**: Local LLM inference with Llama 3.1
- **ChromaDB**: Efficient vector storage for semantic search
- **Sentence Transformers**: High-quality embeddings

## 📋 Prerequisites

- Python 3.9+
- Ollama (for Llama 3.1)
- 8GB+ RAM recommended
- Linux/macOS/Windows with WSL2

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bharatgen-acharya.git
cd bharatgen-acharya
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install and Configure Ollama

```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama 3.1 model
ollama pull llama3.1:8b

# Start Ollama (if not already running)
ollama serve
```

For Docker:
```bash
docker-compose up -d ollama
docker exec -it ollama ollama pull llama3.1:8b
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional, defaults work for local development)
```

### 5. Set Up Database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Load Sample Content

```bash
# Load sample AI learning paths and content
python manage.py load_ai_content

# Build RAG index from content
python manage.py build_rag_index --clear --compute-similarity
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

Visit:
- **Frontend**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/

## 📚 Usage Guide

### For Learners

1. **Register/Login**: Create an account at `/register/`
2. **Browse Learning Paths**: Explore AI courses at `/learning-paths/`
3. **Enroll & Learn**: Start learning and track your progress
4. **Chat with AI**: Get help from the AI assistant at `/chat/`
5. **Track Progress**: View your dashboard at `/`

### For Content Creators

1. **Admin Interface**: Access at `/admin/`
2. **Create Learning Paths**: Add new courses with modules
3. **Add Content**: Create text, code, video, and quiz content
4. **Publish**: Make paths available to learners
5. **Rebuild Index**: Run `python manage.py build_rag_index` after updates

## 🏗️ Architecture

### Backend Stack
- **Django 4.2**: Web framework
- **Django REST Framework**: API layer
- **PostgreSQL/SQLite**: Database
- **JWT**: Authentication

### AI/RAG Stack
- **Ollama + Llama 3.1**: LLM inference
- **Sentence Transformers**: Text embeddings
- **ChromaDB**: Vector database
- **LangChain**: RAG orchestration

### Frontend Stack
- **Vanilla JavaScript**: No framework overhead
- **Modern CSS**: Responsive design
- **Fetch API**: AJAX requests

## 📁 Project Structure

```
bharatgen-acharya/
├── apps/
│   ├── core/           # User auth, profiles, analytics
│   ├── learning/       # Learning paths, modules, content
│   ├── chat/          # AI chat sessions and messages
│   ├── recommendations/ # Recommendation engine
│   └── rag/           # RAG pipeline and providers
├── config/            # Django settings
├── templates/         # HTML templates
├── static/           # CSS, JavaScript, images
├── data/             # Content and ChromaDB storage
├── manage.py
├── requirements.txt
└── README.md
```

## 🔌 API Documentation

### Authentication
```bash
# Register
POST /api/auth/register/
{
  "username": "user",
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}

# Login
POST /api/auth/login/
{
  "username": "user",
  "password": "password123"
}
```

### Learning Paths
```bash
# List paths
GET /api/learning/paths/

# Get path detail
GET /api/learning/paths/{id}/

# Enroll in path
POST /api/learning/paths/{id}/enroll/
```

### Chat
```bash
# Create session
POST /api/chat/sessions/

# Send message
POST /api/chat/sessions/{id}/send_message/
{
  "message": "What is machine learning?",
  "use_rag": true
}
```

### Recommendations
```bash
# Get recommendations
GET /api/recommendations/recommendations/?type=next_content&limit=5
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Random |
| `DEBUG` | Debug mode | `True` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `LLM_MODEL` | Llama model name | `llama3.1:8b` |
| `EMBEDDING_MODEL` | Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage | `./data/chromadb` |

### Pluggable Components

The RAG system is designed to be pluggable. To use different providers:

```python
from apps.rag.pipeline import RAGPipeline
from apps.rag.providers.custom_llm import CustomLLM

# Use custom LLM provider
rag = RAGPipeline(llm=CustomLLM())
```

## 🧪 Management Commands

```bash
# Load sample AI content
python manage.py load_ai_content

# Build RAG index
python manage.py build_rag_index --clear --compute-similarity

# Generate recommendations
python manage.py generate_recommendations --user username
```

## 🐛 Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### ChromaDB Issues
```bash
# Clear and rebuild index
python manage.py build_rag_index --clear
```

### Memory Issues
- Reduce batch size in RAG pipeline
- Use smaller embedding model
- Increase system swap space

## 🚀 Production Deployment

### Using Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Load content
docker-compose exec web python manage.py load_ai_content
docker-compose exec web python manage.py build_rag_index --clear
```

### Manual Deployment

1. Set `DEBUG=False` in `.env`
2. Configure PostgreSQL database
3. Set up Nginx/Apache reverse proxy
4. Use Gunicorn for WSGI
5. Configure static files serving
6. Set up SSL certificates

## 📊 Performance Tips

- Use PostgreSQL for production
- Enable Django caching (Redis/Memcached)
- Pre-compute similarity scores periodically
- Use CDN for static files
- Monitor Ollama resource usage

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [LangChain](https://langchain.com/) for RAG components
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Sentence Transformers](https://www.sbert.net/) for embeddings
- Inspired by [Google Learn Your Way](https://learnyourway.withgoogle.com/)

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Email: support@example.com
- Discord: [Join our community](#)

## 🗺️ Roadmap

- [ ] Video content support
- [ ] Live coding exercises
- [ ] Peer learning features
- [ ] Mobile app
- [ ] Multiple language support
- [ ] Advanced analytics dashboard
- [ ] Integration with external learning platforms

---

**Built with ❤️ for AI Education**
