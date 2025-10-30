# RAG Chatbot System

A web-based chatbot for administrative document question-answering using RAG technology.

## Architecture

```
stage-RAG/
├── main/              # RAG system with LLM integration
├── backend/           # FastAPI REST API
├── frontend/          # React user interface
└── ocr_results/       # Document corpus
```

## Prerequisites

1. **Python 3.8+**: https://www.python.org/downloads/
2. **Node.js 16+**: https://nodejs.org/
3. **Ollama**: https://ollama.ai/ (optional - system works without it)

### Ollama Models (if using Ollama)

```bash
ollama pull llama3
ollama pull mxbai-embed-large
```

## Quick Start

### Option 1: Automatic Setup

```bash
chmod +x start_system.sh
./start_system.sh
```

### Option 2: Manual Setup

1. **Backend Setup**:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

2. **Frontend Setup** (in new terminal):

```bash
cd frontend
npm install
npm start
```

3. **Initialize RAG** (first time only):

```bash
cd main
pip install -r requirements.txt
python main.py
# Type 'q' to exit after initialization
```

## Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## System Behavior

- **With Ollama**: Full RAG functionality with real LLM responses
- **Without Ollama**: Automatic fallback to mock responses (still functional)

## Troubleshooting

1. **Port conflicts**: Change ports in app.py (backend) or package.json (frontend)
2. **Import errors**: Ensure virtual environment is activated
3. **Ollama issues**: System works in fallback mode without Ollama
4. **Reset database**: Delete `main/chroma_db` folder and rerun `python main.py`

## File Structure

```
├── main/               # Original RAG system
│   ├── main.py         # CLI interface
│   ├── vector.py       # Vector store setup
│   └── chroma_db/      # Vector database
├── backend/            # API server
│   ├── app.py          # Main API with Ollama integration
│   └── test_app.py     # Fallback API without Ollama
├── frontend/           # React interface
└── ocr_results/        # 11 administrative documents
```
