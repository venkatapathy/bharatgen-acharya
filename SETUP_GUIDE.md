# 📖 Complete Setup Guide

This guide will walk you through setting up the BharatGen Acharya from scratch.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [Loading Content](#loading-content)
5. [Testing the Setup](#testing-the-setup)
6. [Common Issues](#common-issues)

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **Python**: 3.9 or higher
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **Internet**: For downloading models

### Software Dependencies
- Python 3.9+
- pip (Python package manager)
- Ollama (for Llama 3.1)
- Git

## Installation Steps

### Step 1: Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git curl
```

#### macOS
```bash
brew install python git
```

#### Windows (WSL2)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git curl
```

### Step 2: Install Ollama

Ollama provides local LLM inference for the AI chat feature.

#### Linux/macOS
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Download and install from: https://ollama.ai/download

#### Verify Installation
```bash
ollama --version
```

### Step 3: Clone the Repository

```bash
git clone https://github.com/yourusername/bharatgen-acharya.git
cd bharatgen-acharya
```

### Step 4: Run Automated Setup

We provide an automated setup script that handles most of the configuration:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The script will:
1. Create a virtual environment
2. Install Python dependencies
3. Create configuration files
4. Download the Llama 3.1 model
5. Set up the database
6. Load sample content
7. Build the RAG index

### Step 5: Manual Setup (Alternative)

If you prefer manual setup or the script fails:

#### 5a. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 5b. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5c. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

#### 5d. Set Up Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

#### 5e. Load Sample Content
```bash
python manage.py load_ai_content
python manage.py build_rag_index --clear --compute-similarity
```

## Configuration

### Environment Variables

Edit `.env` to customize your setup:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1:8b

# RAG Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=./data/chromadb
MAX_CONTEXT_LENGTH=4096
TEMPERATURE=0.7
TOP_K=5
```

### Ollama Configuration

1. **Start Ollama Server**:
```bash
ollama serve
```

2. **Pull Llama 3.1 Model**:
```bash
ollama pull llama3.1:8b
```

3. **Verify Model**:
```bash
ollama list
```

You should see `llama3.1:8b` in the list.

## Loading Content

### Load Sample AI Content

The platform comes with sample AI learning paths:

```bash
python manage.py load_ai_content
```

This creates:
- Introduction to Machine Learning (Beginner)
- Natural Language Processing Fundamentals (Intermediate)
- Computer Vision Basics (Intermediate)

### Build RAG Index

After loading content, build the RAG index for the AI chat:

```bash
python manage.py build_rag_index --clear --compute-similarity
```

Options:
- `--clear`: Clear existing index before building
- `--compute-similarity`: Calculate similarity scores for recommendations

### Add Custom Content

1. **Via Admin Interface**:
   - Visit http://localhost:8000/admin/
   - Navigate to Learning → Learning Paths
   - Create new paths, modules, and content

2. **After Adding Content**:
   ```bash
   python manage.py build_rag_index
   ```

## Testing the Setup

### 1. Start the Server

```bash
# Make sure Ollama is running
ollama serve

# In another terminal, start Django
source venv/bin/activate
python manage.py runserver
```

### 2. Access the Platform

Open your browser and visit:
- **Frontend**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/

### 3. Create a Test Account

1. Go to http://localhost:8000/register/
2. Create a new account
3. Log in

### 4. Test Features

#### Test Learning Paths
1. Go to "Learning Paths"
2. Enroll in "Introduction to Machine Learning"
3. Start the first module
4. Mark content as complete

#### Test AI Chat
1. Go to "AI Chat"
2. Ask a question: "What is machine learning?"
3. Verify the AI responds with context from the learning materials

#### Test Recommendations
1. Complete some content
2. Go to the dashboard
3. Check if recommendations appear

### 5. Verify RAG System

```bash
# Check RAG stats
python manage.py shell
>>> from apps.rag.pipeline import get_rag_pipeline
>>> rag = get_rag_pipeline()
>>> stats = rag.get_stats()
>>> print(stats)
```

## Common Issues

### Issue: Ollama Connection Failed

**Symptoms**: Chat doesn't work, errors about connecting to Ollama

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# In another terminal, verify the model
ollama list
```

### Issue: ChromaDB Errors

**Symptoms**: Errors when building RAG index

**Solution**:
```bash
# Remove existing ChromaDB data
rm -rf data/chromadb

# Rebuild index
python manage.py build_rag_index --clear
```

### Issue: No Recommendations

**Symptoms**: Empty recommendations on dashboard

**Solution**:
```bash
# Compute similarity scores
python manage.py build_rag_index --compute-similarity

# Generate recommendations
python manage.py generate_recommendations
```

### Issue: Static Files Not Loading

**Symptoms**: No CSS/JavaScript on pages

**Solution**:
```bash
python manage.py collectstatic --noinput
```

### Issue: Memory Issues

**Symptoms**: System freezes or crashes

**Solution**:
- Use a smaller model: `ollama pull llama3.1:8b` (instead of 70b)
- Reduce batch size in RAG pipeline
- Close other applications
- Increase system swap space

### Issue: Port Already in Use

**Symptoms**: "Error: That port is already in use"

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
python manage.py runserver 8080
```

## Development Tips

### Running Tests

```bash
python manage.py test
```

### Accessing Django Shell

```bash
python manage.py shell
```

### Viewing Logs

```bash
# Django logs
tail -f logs/django.log

# Ollama logs
journalctl -u ollama -f
```

### Database Management

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database
python manage.py flush
```

## Next Steps

After successful setup:

1. **Explore the Admin Interface**: Add custom content
2. **Customize the Frontend**: Modify templates and styles
3. **Configure RAG**: Adjust prompts and retrieval settings
4. **Add More Content**: Create comprehensive learning paths
5. **Deploy to Production**: Follow deployment guide

## Getting Help

If you encounter issues:

1. Check this guide's [Common Issues](#common-issues) section
2. Review the main [README.md](README.md)
3. Open an issue on GitHub
4. Join our Discord community

---

**Happy Learning! 🎓**

