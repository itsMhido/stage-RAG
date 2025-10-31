#!/usr/bin/env python3
"""
Test backend components directly without server
"""

import sys
import os
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.append(str(project_root / 'backend'))
sys.path.append(str(project_root / 'main'))

def test_backend_import():
    """Test if we can import the backend app"""
    try:
        print("Testing backend imports...")
        from fastapi import FastAPI
        print("✓ FastAPI imported")
        
        # Try importing our app
        import backend.app as app_module
        print("✓ Backend app module imported")
        
        app = app_module.app
        print(f"✓ FastAPI app instance: {type(app)}")
        
        # Test with TestClient
        from fastapi.testclient import TestClient
        client = TestClient(app)
        print("✓ TestClient created")
        
        return client
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_endpoints(client):
    """Test API endpoints"""
    try:
        print("\nTesting API endpoints...")
        
        # Test root endpoint
        response = client.get("/")
        print(f"✓ Root endpoint: {response.status_code}")
        print(f"  Response: {response.json()}")
        
        # Test health endpoint
        response = client.get("/health")
        print(f"✓ Health endpoint: {response.status_code}")
        result = response.json()
        print(f"  Status: {result.get('status')}")
        print(f"  RAG loaded: {result.get('rag_system_loaded')}")
        
        return True
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_upload_endpoint(client):
    """Test upload endpoint"""
    try:
        print("\nTesting upload endpoint...")
        
        # Create test file content
        test_content = b"Test document for upload.\nThis is sample content for OCR processing."
        
        # Test upload
        files = {"file": ("test.txt", test_content, "text/plain")}
        response = client.post("/upload", files=files)
        
        print(f"✓ Upload endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Upload result: {result}")
            
            file_id = result.get('file_id')
            if file_id:
                # Test status endpoint
                status_response = client.get(f"/upload/status/{file_id}")
                print(f"✓ Status endpoint: {status_response.status_code}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"  Status: {status}")
                
        else:
            print(f"  Error: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chat_endpoint(client):
    """Test chat endpoint"""
    try:
        print("\nTesting chat endpoint...")
        
        chat_data = {"question": "What is this document about?"}
        response = client.post("/chat", json=chat_data)
        
        print(f"✓ Chat endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Answer: {result.get('answer', '')[:100]}...")
            print(f"  Sources: {result.get('sources', [])}")
        else:
            print(f"  Error: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing backend components directly...\n")
    
    # Test imports
    client = test_backend_import()
    if not client:
        print("\n❌ Cannot continue without successful imports")
        return
    
    # Test endpoints
    endpoints_ok = test_endpoints(client)
    upload_ok = test_upload_endpoint(client)
    chat_ok = test_chat_endpoint(client)
    
    print("\n" + "="*60)
    print("📊 Test Results:")
    print(f"  Imports: ✓")
    print(f"  Basic Endpoints: {'✓' if endpoints_ok else '❌'}")
    print(f"  Upload Endpoint: {'✓' if upload_ok else '❌'}")
    print(f"  Chat Endpoint: {'✓' if chat_ok else '❌'}")
    
    if endpoints_ok and upload_ok and chat_ok:
        print("\n🎉 All backend tests passed!")
        print("The backend is working correctly. You can now:")
        print("1. Start the server: uvicorn app:app --host 127.0.0.1 --port 8001")
        print("2. Test with the frontend")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
