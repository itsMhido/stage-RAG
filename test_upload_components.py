#!/usr/bin/env python3
"""
Simple test of upload functionality components
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test FastAPI imports
        from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
        print("✓ FastAPI imports successful")
        
        # Test other imports
        import subprocess
        import uuid
        from pathlib import Path
        print("✓ Standard library imports successful")
        
        # Test creating FastAPI app
        app = FastAPI()
        print("✓ FastAPI app creation successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_ocr_system():
    """Test if OCR system can be accessed"""
    try:
        print("\nTesting OCR system access...")
        
        # Test if we can run the OCR system
        import subprocess
        
        venv_python = project_root / ".venv" / "bin" / "python"
        
        if not venv_python.exists():
            print(f"✗ Python virtual environment not found at {venv_python}")
            return False
            
        # Test if OCR system module exists
        ocr_module = project_root / "ocr_system" / "main_ocr.py"
        if not ocr_module.exists():
            print(f"✗ OCR system not found at {ocr_module}")
            return False
            
        print("✓ OCR system files found")
        
        # Test help command
        result = subprocess.run([
            str(venv_python), "-m", "ocr_system.main_ocr", "--help"
        ], cwd=str(project_root), capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ OCR system accessible")
            return True
        else:
            print(f"✗ OCR system error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ OCR system test failed: {e}")
        return False

def test_dataset_folder():
    """Test dataset folder access"""
    try:
        print("\nTesting dataset folder...")
        
        dataset_dir = project_root / "dataset"
        dataset_dir.mkdir(exist_ok=True)
        
        if dataset_dir.exists() and dataset_dir.is_dir():
            print(f"✓ Dataset folder accessible at {dataset_dir}")
            return True
        else:
            print(f"✗ Dataset folder not accessible")
            return False
            
    except Exception as e:
        print(f"✗ Dataset folder test failed: {e}")
        return False

if __name__ == "__main__":
    print("Upload System Component Test")
    print("=" * 40)
    
    all_tests_passed = True
    
    all_tests_passed &= test_imports()
    all_tests_passed &= test_ocr_system()
    all_tests_passed &= test_dataset_folder()
    
    print("\n" + "=" * 40)
    if all_tests_passed:
        print("✅ All component tests passed!")
        print("Upload system should work correctly.")
    else:
        print("❌ Some tests failed.")
        print("Please fix the issues before using upload system.")
