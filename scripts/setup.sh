#!/bin/bash
# Setup script for BharatGen Yojaka

set -e

echo "🎓 Setting up BharatGen Yojaka..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip, setuptools, and wheel
echo -e "${BLUE}Upgrading pip, setuptools, and wheel...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ Core tools upgraded${NC}"

# Install dependencies
echo -e "${BLUE}Installing Python dependencies (this may take several minutes)...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file...${NC}"
    cat > .env << 'EOF'
# Django Settings
SECRET_KEY=django-insecure-$(openssl rand -base64 32)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# RAG Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1:8b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=./data/chromadb

# AI Settings
MAX_CONTEXT_LENGTH=4096
TEMPERATURE=0.7
TOP_K=5

# Content
CONTENT_DIR=./data/learning_content
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create data directories
echo -e "${BLUE}Creating data directories...${NC}"
mkdir -p data/chromadb
mkdir -p data/learning_content
echo -e "${GREEN}✓ Data directories created${NC}"

# Check if Ollama is installed
echo -e "${BLUE}Checking Ollama installation...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is installed${NC}"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama is running${NC}"
        
        # Pull Llama model
        echo -e "${BLUE}Pulling Llama 3.1 model (this may take a while)...${NC}"
        ollama pull llama3.1:8b
        echo -e "${GREEN}✓ Llama 3.1 model ready${NC}"
    else
        echo -e "${RED}✗ Ollama is not running${NC}"
        echo "  Please start Ollama with: ollama serve"
        echo "  Then run this script again"
        exit 1
    fi
else
    echo -e "${RED}✗ Ollama is not installed${NC}"
    echo "  Please install Ollama from: https://ollama.ai"
    echo "  Then run this script again"
    exit 1
fi

# Run migrations
echo -e "${BLUE}Running database migrations...${NC}"
python manage.py migrate
echo -e "${GREEN}✓ Database migrations complete${NC}"

# Create superuser
echo -e "${BLUE}Creating superuser...${NC}"
echo "Please enter superuser details:"
python manage.py createsuperuser

# Load sample content
echo -e "${BLUE}Loading sample AI learning content...${NC}"
python manage.py load_ai_content
echo -e "${GREEN}✓ Sample content loaded${NC}"

# Build RAG index
echo -e "${BLUE}Building RAG index (this may take a few minutes)...${NC}"
python manage.py build_rag_index --clear --compute-similarity
echo -e "${GREEN}✓ RAG index built${NC}"

# Collect static files
echo -e "${BLUE}Collecting static files...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo "To start the development server:"
echo "  1. Make sure Ollama is running: ollama serve"
echo "  2. Activate virtual environment: source venv/bin/activate"
echo "  3. Start Django: python manage.py runserver"
echo ""
echo "Then visit:"
echo "  - Frontend: http://localhost:8000/"
echo "  - Admin: http://localhost:8000/admin/"
echo "  - API: http://localhost:8000/api/"
echo ""
echo "Happy learning! 🎓"

