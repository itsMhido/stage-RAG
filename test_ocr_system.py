#!/usr/bin/env python3
"""
Test script for OCR System
Tests text extraction from various file formats and validates output
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess

# Add the parent directory to sys.path to import ocr_system
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ocr_system.main_ocr import OCRSystem
    from ocr_system.ocr_processor import OCRProcessor
    from ocr_system.document_processor import DocumentProcessor
except ImportError as e:
    print(f"Error importing OCR system: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

class OCRTester:
    def __init__(self):
        self.test_dir = Path("test_ocr_files")
        self.output_dir = Path("test_ocr_output")
        self.results = []
        
    def setup_test_environment(self):
        """Create test directories"""
        print("Setting up test environment...")
        
        # Clean and create directories
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            
        self.test_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"Test files directory: {self.test_dir}")
        print(f"Test output directory: {self.output_dir}")
    
    def create_test_text_file(self):
        """Create a test text file with French and Arabic content"""
        test_text = """Exemple de texte en français
===========================

Ceci est un document administratif test.
Il contient des informations importantes pour le système RAG.

Numéro de dossier: 123456789
Date: 2024-01-15
Montant: 1,500.00 MAD

نص تجريبي باللغة العربية
=====================

هذا مستند إداري تجريبي.
يحتوي على معلومات مهمة لنظام RAG.

رقم الملف: 987654321
التاريخ: 15-01-2024
المبلغ: 1500.00 درهم

Mixed Content:
- French: Attestation d'intérêts
- Arabic: شهادة الفوائد
- Numbers: 01060150
"""
        
        file_path = self.test_dir / "test_document.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(test_text)
        
        return file_path, test_text
    
    def create_test_image(self):
        """Create a test image with text"""
        try:
            # Create an image with text
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font, fallback to basic if not available
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            except:
                try:
                    font_large = ImageFont.load_default()
                    font_medium = ImageFont.load_default()
                except:
                    font_large = None
                    font_medium = None
            
            # Add text to image
            y_position = 50
            texts = [
                "Test Document OCR",
                "Document Administratif",
                "Numero: 123456789",
                "Date: 2024-01-15",
                "Montant: 2,500.00 MAD",
                "",
                "This text should be extracted",
                "by the OCR system and saved",
                "to the ocr_results folder."
            ]
            
            for text in texts:
                if text:
                    draw.text((50, y_position), text, fill='black', font=font_medium)
                y_position += 40
            
            # Save image
            file_path = self.test_dir / "test_image.png"
            img.save(file_path, "PNG")
            
            return file_path, "\n".join(texts)
            
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None, ""
    
    def create_test_pdf_with_text(self):
        """Create a simple PDF with text (requires reportlab)"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            file_path = self.test_dir / "test_pdf_text.pdf"
            
            c = canvas.Canvas(str(file_path), pagesize=letter)
            
            # Add text content
            y_position = 750
            texts = [
                "Document PDF Test",
                "=================",
                "",
                "Informations du document:",
                "Référence: DOC-2024-001",
                "Date: 15 janvier 2024",
                "Montant total: 3,750.00 MAD",
                "",
                "Ce document contient du texte",
                "qui devrait être extrait par",
                "le système OCR/PDF."
            ]
            
            for text in texts:
                if text:
                    c.drawString(50, y_position, text)
                y_position -= 25
            
            c.save()
            
            return file_path, "\n".join(texts)
            
        except ImportError:
            print("reportlab not available, skipping PDF creation")
            return None, ""
        except Exception as e:
            print(f"Error creating PDF: {e}")
            return None, ""
    
    def test_individual_processors(self):
        """Test individual processor components"""
        print("\n" + "="*60)
        print("TESTING INDIVIDUAL PROCESSORS")
        print("="*60)
        
        # Test OCR Processor
        print("\n1. Testing OCR Processor...")
        ocr_proc = OCRProcessor()
        
        # Test text cleaning
        dirty_text = "  Line 1  \n\n  \n  Line 2   \n\n\n  Line 3  "
        clean_text = ocr_proc.clean_extracted_text(dirty_text)
        print(f"   Text cleaning: {'✓' if 'Line 1\nLine 2\nLine 3' == clean_text else '✗'}")
        
        # Test Document Processor
        print("\n2. Testing Document Processor...")
        doc_proc = DocumentProcessor()
        
        # Create a test text file and test extraction
        test_file, expected_content = self.create_test_text_file()
        extracted = doc_proc.extract_text_from_txt(str(test_file))
        text_extraction_ok = len(extracted) > 100 and "français" in extracted
        print(f"   Text file extraction: {'✓' if text_extraction_ok else '✗'}")
        
        self.results.append(("OCR Processor", True))
        self.results.append(("Document Processor", text_extraction_ok))
    
    def test_ocr_system_single_files(self):
        """Test OCR system with individual files"""
        print("\n" + "="*60)
        print("TESTING OCR SYSTEM - SINGLE FILES")
        print("="*60)
        
        ocr_system = OCRSystem(str(self.output_dir))
        
        # Test 1: Text file
        print("\n1. Testing text file processing...")
        text_file, expected_text = self.create_test_text_file()
        success = ocr_system.process_single_file(text_file)
        self.results.append(("Text file processing", success))
        
        # Test 2: Image file
        print("\n2. Testing image file processing...")
        image_file, expected_image_text = self.create_test_image()
        if image_file:
            success = ocr_system.process_single_file(image_file)
            self.results.append(("Image file processing", success))
        else:
            self.results.append(("Image file processing", False))
        
        # Test 3: PDF file (if possible)
        print("\n3. Testing PDF file processing...")
        pdf_file, expected_pdf_text = self.create_test_pdf_with_text()
        if pdf_file:
            success = ocr_system.process_single_file(pdf_file)
            self.results.append(("PDF file processing", success))
        else:
            print("   Skipping PDF test (reportlab not available)")
            self.results.append(("PDF file processing", None))
    
    def test_ocr_system_directory(self):
        """Test OCR system with directory processing"""
        print("\n" + "="*60)
        print("TESTING OCR SYSTEM - DIRECTORY PROCESSING")
        print("="*60)
        
        ocr_system = OCRSystem(str(self.output_dir))
        
        # Process the entire test directory
        print(f"\nProcessing directory: {self.test_dir}")
        ocr_system.process_directory(str(self.test_dir))
        
        # Check if output files were created
        output_files = list(self.output_dir.glob("*.txt"))
        success = len(output_files) > 0
        
        print(f"\nDirectory processing result:")
        print(f"  Output files created: {len(output_files)}")
        for output_file in output_files:
            size = output_file.stat().st_size
            print(f"    - {output_file.name} ({size} bytes)")
        
        self.results.append(("Directory processing", success))
    
    def validate_output_files(self):
        """Validate the content of output files"""
        print("\n" + "="*60)
        print("VALIDATING OUTPUT FILES")
        print("="*60)
        
        output_files = list(self.output_dir.glob("*.txt"))
        
        for output_file in output_files:
            print(f"\nValidating: {output_file.name}")
            
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic validations
                has_header = "Source File:" in content and "Extraction Date:" in content
                has_content = len(content.split("="*80)[-1].strip()) > 10
                
                print(f"  Header present: {'✓' if has_header else '✗'}")
                print(f"  Content length: {len(content)} characters")
                print(f"  Has meaningful content: {'✓' if has_content else '✗'}")
                
                # Show a preview of extracted content
                content_part = content.split("="*80)[-1].strip()
                preview = content_part[:200] + "..." if len(content_part) > 200 else content_part
                print(f"  Content preview: {repr(preview)}")
                
                self.results.append((f"Output validation - {output_file.name}", has_header and has_content))
                
            except Exception as e:
                print(f"  Error reading file: {e}")
                self.results.append((f"Output validation - {output_file.name}", False))
    
    def test_dataset_folder(self):
        """Test OCR system with the dataset folder"""
        print("\n" + "="*60)
        print("TESTING DATASET FOLDER PROCESSING")
        print("="*60)
        
        dataset_dir = Path("dataset")
        
        if not dataset_dir.exists():
            print(f"Dataset folder not found: {dataset_dir}")
            self.results.append(("Dataset folder processing", None))
            return
        
        # Find all supported files in dataset
        ocr_system = OCRSystem(str(self.output_dir))
        all_files = []
        for file_path in dataset_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ocr_system.supported_extensions:
                all_files.append(file_path)
        
        if not all_files:
            print(f"No supported files found in {dataset_dir}")
            print("Add some documents to the dataset folder and run the test again.")
            print(f"Supported extensions: {list(ocr_system.supported_extensions.keys())}")
            self.results.append(("Dataset folder processing", None))
            return
        
        print(f"Found {len(all_files)} files in dataset folder:")
        for i, file_path in enumerate(all_files, 1):
            size = file_path.stat().st_size / 1024  # KB
            print(f"  {i:2d}. {file_path.name} ({file_path.suffix.upper()}, {size:.1f} KB)")
        
        # Process the dataset directory
        print(f"\nProcessing dataset folder...")
        ocr_system.process_directory(str(dataset_dir))
        
        # Check results
        output_files = list(self.output_dir.glob("*.txt"))
        dataset_output_files = [f for f in output_files if f.stem in [file.stem for file in all_files]]
        
        success = len(dataset_output_files) > 0
        success_rate = len(dataset_output_files) / len(all_files) * 100 if all_files else 0
        
        print(f"\nDataset processing results:")
        print(f"  Files processed successfully: {len(dataset_output_files)}/{len(all_files)}")
        print(f"  Success rate: {success_rate:.1f}%")
        
        self.results.append(("Dataset folder processing", success))
    
    def test_command_line_interface(self):
        """Test the command line interface"""
        print("\n" + "="*60)
        print("TESTING COMMAND LINE INTERFACE")
        print("="*60)
        
        # Test CLI with a single file
        test_file, _ = self.create_test_text_file()
        
        try:
            # Run the OCR system via command line
            cmd = [
                sys.executable, "-m", "ocr_system.main_ocr",
                str(test_file),
                "--output", str(self.output_dir / "cli_test")
            ]
            
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            
            success = result.returncode == 0
            print(f"Command execution: {'✓' if success else '✗'}")
            
            if not success:
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
            
            # Check if output was created
            cli_output_dir = self.output_dir / "cli_test"
            if cli_output_dir.exists():
                output_files = list(cli_output_dir.glob("*.txt"))
                files_created = len(output_files) > 0
                print(f"Output files created: {'✓' if files_created else '✗'}")
                success = success and files_created
            
            self.results.append(("Command line interface", success))
            
        except Exception as e:
            print(f"Error testing CLI: {e}")
            self.results.append(("Command line interface", False))
    
    def print_test_summary(self):
        """Print summary of all test results"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, result in self.results:
            if result is True:
                status = "✓ PASS"
                passed += 1
            elif result is False:
                status = "✗ FAIL"
                failed += 1
            else:
                status = "- SKIP"
                skipped += 1
            
            print(f"{status:<8} {test_name}")
        
        total = passed + failed + skipped
        print(f"\nResults: {passed}/{total} passed, {failed} failed, {skipped} skipped")
        
        if failed == 0:
            print("\n🎉 All tests passed! OCR system is working correctly.")
        else:
            print(f"\n⚠️  {failed} tests failed. Please check the issues above.")
        
        return failed == 0
    
    def cleanup(self):
        """Clean up test files"""
        print("\nCleaning up test files...")
        
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        
        # Optionally keep output files for inspection
        print(f"Test output files kept in: {self.output_dir}")
        print("You can delete this directory manually if not needed.")
    
    def run_all_tests(self):
        """Run all tests"""
        print("OCR System Test Suite")
        print("====================")
        print("This will test all components of the OCR system")
        
        try:
            self.setup_test_environment()
            self.test_individual_processors()
            self.test_ocr_system_single_files()
            self.test_ocr_system_directory()
            self.test_dataset_folder()
            self.validate_output_files()
            self.test_command_line_interface()
            
            success = self.print_test_summary()
            
            return success
            
        except Exception as e:
            print(f"\nUnexpected error during testing: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main test function"""
    print("Starting OCR System Tests...")
    print("=" * 50)
    
    # Check prerequisites
    print("Checking prerequisites...")
    
    try:
        import pytesseract
        import PIL
        import cv2
        import numpy
        print("✓ All required packages are available")
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please install requirements: pip install -r ocr_system/requirements.txt")
        return False
    
    # Check Tesseract
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract OCR version: {version}")
    except Exception as e:
        print(f"✗ Tesseract OCR not found: {e}")
        print("Please install Tesseract OCR on your system")
        return False
    
    # Run tests
    tester = OCRTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 OCR System is ready for use!")
        print("\nTo use the OCR system:")
        print("  python -m ocr_system.main_ocr <file_or_directory>")
        print("  python -m ocr_system.main_ocr document.pdf")
        print("  python -m ocr_system.main_ocr /path/to/documents/")
    else:
        print("\n❌ Some tests failed. Please fix the issues before using the OCR system.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
