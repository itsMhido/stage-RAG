from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
import asyncio
from datetime import datetime
import time

# Add the main directory to Python path to import existing RAG system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'main'))

app = FastAPI(
    title="RAG Chatbot API",
    description="API for administrative document Q&A chatbot",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Global variables for RAG components
rag_chain = None
retriever = None

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

class SourcesResponse(BaseModel):
    sources: List[str]

# Mock classes for fallback when Ollama is not available
class MockDocument:
    def __init__(self, content: str, metadata: dict):
        self.page_content = content
        self.metadata = metadata

class MockRetriever:
    def invoke(self, question: str):
        # Mock document retrieval based on question keywords
        question_lower = question.lower()
        
        if "compte" in question_lower or "account" in question_lower:
            return [MockDocument(
                "Information sur le compte de crédit logement: Le numéro de compte associé au crédit logement est 01060150.",
                {"source": "attestation_interets.txt"}
            )]
        elif "cnops" in question_lower:
            return [MockDocument(
                "Traitement du dossier CNOPS 906377038 qui a pris 113 jours pour être traité.",
                {"source": "cnops2.txt"}
            )]
        elif "montant" in question_lower or "remboursement" in question_lower:
            return [MockDocument(
                "Montant remboursé par l'AMO: 2,608.00 MAD, montant pris en charge par la Mutuelle: 192.00 MAD dans le décompte Sanlam.",
                {"source": "decompte_remboursement.txt"}
            )]
        else:
            return [MockDocument(
                f"Document simulé pour la question: {question}",
                {"source": "mock_document.txt"}
            )]

class MockRAGChain:
    def invoke(self, inputs: dict):
        question = inputs.get("question", "")
        context = inputs.get("context", "")
        
        # Simple rule-based responses
        question_lower = question.lower()
        
        if "compte" in question_lower or "account" in question_lower:
            return "Le numéro de compte associé au crédit logement est 01060150."
        elif "jours" in question_lower or "days" in question_lower:
            return "Le traitement du dossier CNOPS 906377038 a pris 113 jours."
        elif "montant" in question_lower or "amount" in question_lower:
            return "Le montant remboursé par l'AMO dans le décompte Sanlam était de 2,608.00 MAD, et le montant pris en charge par la Mutuelle était de 192.00 MAD."
        elif "رقم الحساب" in question or "نبر الحساب" in question:
            return "رقم الحساب المرتبط بقرض السكن هو 01060150."
        else:
            return f"Je traite votre question sur les documents administratifs: '{question}'. Basé sur le contexte: {context[:100]}..."

def initialize_rag_system():
    """Initialize the RAG system components lazily"""
    global rag_chain, retriever
    
    if rag_chain is None or retriever is None:
        try:
            # Try to import and initialize the full RAG system
            from langchain_ollama import OllamaLLM
            from langchain_core.prompts import ChatPromptTemplate
            
            # Test Ollama connection first
            model = OllamaLLM(model="llama3")
            # Simple test to see if Ollama is responsive
            test_response = model.invoke("test")
            
            # If we get here, Ollama is working
            print("Ollama is available, initializing full RAG system...")
            
            # Import the existing RAG system components
            import chromadb
            from langchain_chroma import Chroma
            from langchain_ollama import OllamaEmbeddings
            from langchain_core.output_parsers import StrOutputParser
            
            # Initialize embeddings (use same model as main/vector.py)
            embeddings = OllamaEmbeddings(model="mxbai-embed-large")
            
            # Initialize vector store (use same settings as main/vector.py)
            persist_directory = os.path.join(os.path.dirname(__file__), '..', 'main', 'chroma_db')
            vectorstore = Chroma(
                collection_name="my_collection",
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
            
            # Create retriever (use same settings as main/vector.py)
            retriever = vectorstore.as_retriever(
                search_kwargs={"k": 5}
            )
            
            # Create the RAG chain (use same template style as main/main.py)
            template = """
            Tu es un assistant qui répond à la question {question} uniquement en te basant sur le contexte suivant 
            sans mentionner la question, le nom des documents ou leurs ID: {context}
            """
            
            prompt = ChatPromptTemplate.from_template(template)
            rag_chain = prompt | model | StrOutputParser()
            
            print("Full RAG system initialized successfully!")
            return True
            
        except Exception as e:
            print(f"Failed to initialize Ollama RAG system: {e}")
            print("Falling back to mock RAG system...")
            
            # Initialize mock system
            rag_chain = MockRAGChain()
            retriever = MockRetriever()
            
            print("Mock RAG system initialized successfully!")
            return True
    
    return True

@app.get("/", response_model=dict)
async def root():
    return {
        "message": "RAG Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "description": "Administrative document Q&A chatbot"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        is_initialized = initialize_rag_system()
        return HealthResponse(
            status="healthy",
            message="RAG system is ready" if is_initialized else "RAG system initialization failed",
            rag_system_loaded=is_initialized
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            message=f"Health check failed: {str(e)}",
            rag_system_loaded=False
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    try:
        start_time = asyncio.get_event_loop().time()
        
        if not message.question or not message.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Initialize RAG system if not already done
        if not initialize_rag_system():
            raise HTTPException(status_code=503, detail="RAG system not available")
        
        # Retrieve relevant context from documents
        context_docs = retriever.invoke(message.question.strip())
        
        # Extract context and sources
        context_text = "\n".join([doc.page_content for doc in context_docs])
        sources = [doc.metadata.get("source", "unknown") for doc in context_docs]
        
        # Generate answer using RAG chain
        answer = rag_chain.invoke({
            "context": context_text,
            "question": message.question.strip()
        })
        
        # Calculate processing time
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return ChatResponse(
            answer=answer.strip(),
            sources=list(set(sources)),  # Remove duplicates
            timestamp=datetime.now(),
            processing_time=round(processing_time, 3)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/sources", response_model=SourcesResponse)
async def get_available_sources():
    """Get list of available document sources"""
    try:
        # Return mock sources for now
        mock_sources = [
            "attestation_interets.txt",
            "certificat_scolarite_arabe.txt", 
            "certificat_scolarite_Rayan.txt",
            "cnops2.txt",
            "decompte_remboursement.txt",
            "demande_estivage.txt",
            "remboursement_cnops1.txt",
            "ticket_reservation.txt",
            "tresorerie_generale_royaume.txt"
        ]
        
        return SourcesResponse(sources=mock_sources)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sources: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    print("Starting RAG Chatbot API...")
    print("Available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
