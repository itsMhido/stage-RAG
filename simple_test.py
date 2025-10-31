print("Backend test starting...")

import sys
import os
from pathlib import Path

# Setup paths
project_root = Path("/home/f1red/Desktop/INPT/Stage INE1/stage-RAG")
sys.path.append(str(project_root / "backend"))
sys.path.append(str(project_root / "main"))

print("Paths configured")

try:
    from fastapi.testclient import TestClient
    from backend.app import app
    
    print("Imports successful")
    
    client = TestClient(app)
    print("TestClient created")
    
    # Test health endpoint
    response = client.get("/health")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print("✓ Backend is working!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
