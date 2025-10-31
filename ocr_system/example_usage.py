#!/usr/bin/env python3
"""
Simple usage example for the OCR System
Demonstrates how to use the OCR system programmatically
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ocr_system.main_ocr import OCRSystem

def example_usage():
    """Example of how to use the OCR system"""
    
    print("OCR System Usage Example")
    print("=" * 30)
    
    # Initialize OCR system (outputs to ocr_results folder)
    ocr = OCRSystem("ocr_results")
    
    # Example 1: Process a single file
    print("\n1. Processing single file:")
    # ocr.process_single_file("example_document.pdf")
    
    # Example 2: Process entire directory
    print("\n2. Processing directory:")
    # ocr.process_directory("documents/")
    
    print("\nFiles will be saved in the 'ocr_results' folder")
    print("Each extracted text file will include:")
    print("- Source file information")
    print("- Extraction date and metadata")
    print("- Extracted text content")

if __name__ == "__main__":
    example_usage()
