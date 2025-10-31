#!/usr/bin/env python3
"""Test script to verify backend startup"""

import sys
import os
sys.path.append('backend')

try:
    # Test importing the app
    print("Testing backend import...")
    from backend.app import app
    print("✓ Backend app imported successfully")
    
    # Test basic FastAPI functionality
    print("Testing FastAPI initialization...")
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test health endpoint
    print("Testing health endpoint...")
    response = client.get("/health")
    print(f"Health check status: {response.status_code}")
    print(f"Health response: {response.json()}")
    
    # Test root endpoint
    print("Testing root endpoint...")
    response = client.get("/")
    print(f"Root status: {response.status_code}")
    print(f"Root response: {response.json()}")
    
    print("\n✓ All basic backend tests passed!")
    
except Exception as e:
    print(f"❌ Backend test failed: {e}")
    import traceback
    traceback.print_exc()
