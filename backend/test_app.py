from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import time
from datetime import datetime

app = FastAPI(title="Test RAG Chatbot API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    timestamp: datetime
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    message: str
    rag_system_loaded: bool

@app.get("/", response_model=dict)
async def root():
    return {
        "message": "Test RAG Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        message="Test API is running (Ollama not required)",
        rag_system_loaded=True  # Fake it for testing
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    start_time = time.time()
    
    try:
        if not message.question or not message.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Simulate processing time
        time.sleep(1)
        
        # Simple test responses based on keywords
        question = message.question.lower()
        
        if "compte" in question or "account" in question:
            answer = "Le numéro de compte associé au crédit logement est 01060150."
            sources = ["attestation_interets.txt"]
        elif "jours" in question or "days" in question:
            answer = "Le traitement du dossier CNOPS 906377038 a pris 113 jours."
            sources = ["cnops2.txt"]
        elif "montant" in question or "amount" in question:
            answer = "Le montant remboursé par l'AMO dans le décompte Sanlam était de 2,608.00 MAD."
            sources = ["decompte_remboursement.txt"]
        elif "نبر الحساب" in question or "رقم الحساب" in question:
            answer = "رقم الحساب المرتبط بقرض السكن هو 01060150."
            sources = ["attestation_interets.txt"]
        else:
            answer = f"Je traite votre question: '{message.question}'. Ceci est une réponse de test car le système RAG complet n'est pas encore connecté."
            sources = ["test_document.txt"]
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            timestamp=datetime.now(),
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/sources")
async def get_available_sources():
    return {
        "sources": [
            "attestation_interets.txt",
            "cnops2.txt", 
            "decompte_remboursement.txt",
            "certificat_scolarite_arabe.txt",
            "test_document.txt"
        ], 
        "count": 5
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Test RAG Chatbot API...")
    print("✅ No Ollama required for testing")
    print("🌟 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
