#!/usr/bin/env python3
"""
Test script for the upload functionality
"""

import requests
import json
from pathlib import Path

def test_upload_endpoint():
    """Test the upload endpoint with a sample file"""
    
    # Create a test file
    test_file_content = """
    Test Document
    =============
    
    This is a test document for OCR processing.
    It contains some French text: Bonjour, ceci est un test.
    And some Arabic text: مرحبا، هذا اختبار.
    
    Number: 12345
    Date: 2025-10-31
    """
    
    test_file_path = Path("test_upload.txt")
    
    try:
        # Create test file
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_file_content)
        
        print("Testing upload endpoint...")
        
        # Test upload
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_upload.txt", f, "text/plain")}
            response = requests.post("http://localhost:8000/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Upload successful!")
            print(f"  Status: {result['status']}")
            print(f"  Message: {result['message']}")
            print(f"  Filename: {result['filename']}")
            print(f"  File ID: {result['file_id']}")
            
            # Test status checking
            file_id = result['file_id']
            print(f"\nChecking processing status...")
            
            import time
            for i in range(10):  # Check for up to 20 seconds
                status_response = requests.get(f"http://localhost:8000/upload/status/{file_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"  Status: {status['status']} - {status['message']}")
                    
                    if status['status'] in ['completed', 'error']:
                        break
                
                time.sleep(2)
            
        else:
            print(f"✗ Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to backend. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Clean up test file
        if test_file_path.exists():
            test_file_path.unlink()

if __name__ == "__main__":
    test_upload_endpoint()
