#!/usr/bin/env python3
"""
Comprehensive test for upload flow
"""

import requests
import json
import time
import os
from pathlib import Path

# Test configuration
API_BASE = "http://localhost:8001"  # Using port 8001

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        print(f"✓ Backend health: {response.status_code}")
        print(f"  Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_upload_flow():
    """Test complete upload and OCR flow"""
    try:
        # Create a test text file
        test_content = """Test Document

This is a test document for uploading to the RAG system.
It contains sample text that should be processed by OCR.

Key information:
- Document type: Test
- Content: Sample administrative text
- Purpose: System verification
"""
        
        test_file_path = Path("/tmp/test_upload.txt")
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print("📤 Testing file upload...")
        
        # Upload the file
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_upload.txt', f, 'text/plain')}
            response = requests.post(f"{API_BASE}/upload", files=files, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
        
        upload_result = response.json()
        print(f"✓ Upload successful: {upload_result}")
        
        file_id = upload_result.get('file_id')
        if not file_id:
            print("❌ No file_id returned")
            return False
        
        # Poll for processing status
        print("⏳ Polling for processing status...")
        max_polls = 30  # Max 1 minute wait
        poll_count = 0
        
        while poll_count < max_polls:
            try:
                status_response = requests.get(f"{API_BASE}/upload/status/{file_id}", timeout=5)
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"  Status: {status['status']} - {status['message']}")
                    
                    if status['status'] == 'completed':
                        print("✓ Processing completed successfully!")
                        
                        # Check if OCR output file was created
                        ocr_output_path = Path('/home/f1red/Desktop/INPT/Stage INE1/stage-RAG/ocr_results/test_upload.txt')
                        if ocr_output_path.exists():
                            print("✓ OCR output file created successfully!")
                            with open(ocr_output_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                print(f"  OCR content preview: {content[:100]}...")
                        else:
                            print("⚠️ OCR output file not found")
                        
                        return True
                    
                    elif status['status'] == 'error':
                        print(f"❌ Processing failed: {status['message']}")
                        return False
                    
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Status check error: {e}")
                return False
            
            poll_count += 1
            time.sleep(2)  # Wait 2 seconds between polls
        
        print("❌ Processing timed out")
        return False
        
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test file
        if test_file_path.exists():
            test_file_path.unlink()

def test_chat_functionality():
    """Test chat endpoint"""
    try:
        print("💬 Testing chat functionality...")
        
        chat_data = {
            "question": "What is this document about?"
        }
        
        response = requests.post(
            f"{API_BASE}/chat", 
            json=chat_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Chat response received")
            print(f"  Answer: {result.get('answer', '')[:100]}...")
            print(f"  Sources: {result.get('sources', [])}")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting comprehensive backend tests...\n")
    
    # Test 1: Backend health
    if not test_backend_health():
        print("\n❌ Backend not running. Please start the backend first.")
        print("Run: cd backend && uvicorn app:app --host 0.0.0.0 --port 8001")
        return
    
    print("\n" + "="*50)
    
    # Test 2: Upload and OCR flow
    upload_success = test_upload_flow()
    
    print("\n" + "="*50)
    
    # Test 3: Chat functionality
    chat_success = test_chat_functionality()
    
    print("\n" + "="*50)
    print("📊 Test Summary:")
    print(f"  Backend Health: ✓")
    print(f"  Upload Flow: {'✓' if upload_success else '❌'}")
    print(f"  Chat Function: {'✓' if chat_success else '❌'}")
    
    if upload_success and chat_success:
        print("\n🎉 All tests passed! The system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
