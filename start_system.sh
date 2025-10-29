#!/bin/bash

echo "Starting RAG Chatbot System..."

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    echo -e "${YELLOW}Killing process on port $port...${NC}"
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed${NC}"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}Warning: Ollama is not installed${NC}"
    echo -e "${YELLOW}Please install Ollama first: curl -fsSL https://ollama.ai/install.sh | sh${NC}"
    exit 1
fi

echo -e "${GREEN}All prerequisites found${NC}"

# Check if ports are available
if check_port 8000; then
    echo -e "${YELLOW}Warning: Port 8000 is already in use${NC}"
    read -p "Kill process on port 8000? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill_port 8000
    else
        echo -e "${RED}Error: Cannot start backend on port 8000${NC}"
        exit 1
    fi
fi

if check_port 3000; then
    echo -e "${YELLOW}Warning: Port 3000 is already in use${NC}"
    read -p "Kill process on port 3000? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill_port 3000
    else
        echo -e "${RED}Error: Cannot start frontend on port 3000${NC}"
        exit 1
    fi
fi

# Start Ollama in background if not running
echo -e "${BLUE}Checking Ollama service...${NC}"
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}Starting Ollama service...${NC}"
    ollama serve &
    sleep 3
fi

# Pull required models
echo -e "${BLUE}Checking Ollama models...${NC}"
ollama list | grep -q "llama3" || {
    echo -e "${YELLOW}Pulling llama3 model (this may take a while)...${NC}"
    ollama pull llama3
}

ollama list | grep -q "mxbai-embed-large" || {
    echo -e "${YELLOW}Pulling mxbai-embed-large model...${NC}"
    ollama pull mxbai-embed-large
}

# Start backend
echo -e "${BLUE}Starting backend...${NC}"
cd backend

# Setup Python virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Start FastAPI in background
python app.py &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}Error: Backend failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}Backend started successfully${NC}"

# Start frontend
echo -e "${BLUE}Starting frontend...${NC}"
cd ../frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Start React app
npm start &
FRONTEND_PID=$!

echo -e "${GREEN}System started successfully!${NC}"
echo -e "${BLUE}Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}Backend API: http://localhost:8000${NC}"
echo -e "${BLUE}📚 API Docs: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for user to stop
wait
