import os
import argparse
from pathlib import Path
from datetime import datetime
from .document_processor import DocumentProcessor
from .ocr_processor import OCRProcessor

class OCRSystem:
    def __init__(self, output_dir="./ocr_results"):
        self.output_dir = Path(output_dir).resolve()
        self.doc_processor = DocumentProcessor()
        self.ocr_processor = OCRProcessor()
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Supported file extensions and their processors
        self.supported_extensions = {
            '.pdf': self.doc_processor.extract_text_from_pdf,
            '.docx': self.doc_processor.extract_text_from_docx,
            '.doc': self.doc_processor.extract_text_from_docx,  # Try with .doc too
            '.txt': self.doc_processor.extract_text_from_txt,
            '.png': self.ocr_processor.extract_text_from_image,
            '.jpg': self.ocr_processor.extract_text_from_image,
            '.jpeg': self.ocr_processor.extract_text_from_image,
            '.tiff': self.ocr_processor.extract_text_from_image,
            '.tif': self.ocr_processor.extract_text_from_image,
            '.bmp': self.ocr_processor.extract_text_from_image,
            '.gif': self.ocr_processor.extract_text_from_image,
        }
    
    def generate_output_filename(self, input_path):
        """Generate output filename and handle naming conflicts"""
        input_path = Path(input_path)
        base_name = input_path.stem
        
        # Clean filename for safe storage
        import re
        safe_name = re.sub(r'[^\w\-_\.]', '_', base_name)
        
        output_file = self.output_dir / f"{safe_name}.txt"
        
        # Check if file already exists
        if output_file.exists():
            conflict_info = self._check_naming_conflict(output_file, input_path)
            
            if conflict_info['is_same_source']:
                # Same source file already processed
                print(f"⚠️  WARNING: File '{safe_name}.txt' already exists from the same source")
                print(f"   Source: {input_path.name}")
                print(f"   Full path: {input_path}")
                if conflict_info['extraction_date']:
                    print(f"   Previously extracted: {conflict_info['extraction_date']}")
                print(f"   Skipping extraction (file already processed)")
                return None
            else:
                # Different source file with same name
                print(f"⚠️  WARNING: File '{safe_name}.txt' already exists from different source")
                if conflict_info['existing_source']:
                    print(f"   Existing source: {conflict_info['existing_source']}")
                print(f"   New source: {input_path.name}")
                
                # Generate alternative name
                counter = 1
                original_output = output_file
                while output_file.exists():
                    output_file = self.output_dir / f"{safe_name}_{counter}.txt"
                    counter += 1
                
                print(f"   Creating alternative name: {output_file.name}")
        
        return output_file
    
    def _check_naming_conflict(self, output_file, input_path):
        """Check if an output file conflicts with the input and extract metadata"""
        conflict_info = {
            'is_same_source': False,
            'existing_source': None,
            'extraction_date': None,
            'file_path': None
        }
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 characters for metadata
                
            lines = content.split('\n')
            for line in lines:
                if line.startswith("Source File:"):
                    conflict_info['existing_source'] = line.split(":", 1)[1].strip()
                elif line.startswith("File Path:"):
                    conflict_info['file_path'] = line.split(":", 1)[1].strip()
                elif line.startswith("Extraction Date:"):
                    conflict_info['extraction_date'] = line.split(":", 1)[1].strip()
            
            # Check if it's the same source file
            if conflict_info['existing_source'] == input_path.name:
                # Additional check: compare file paths if available
                if conflict_info['file_path']:
                    conflict_info['is_same_source'] = str(input_path) == conflict_info['file_path']
                else:
                    # Fallback to name comparison only
                    conflict_info['is_same_source'] = True
            
        except Exception as e:
            print(f"⚠️  WARNING: Could not read existing file metadata: {e}")
            # Conservative approach: assume different source to avoid overwriting
            conflict_info['existing_source'] = "Unknown (error reading file)"
        
        return conflict_info
    
    def process_single_file(self, file_path):
        """Process a single file and extract text"""
        file_path = Path(file_path).resolve()
        
        if not file_path.exists():
            print(f"Error: File {file_path} does not exist")
            return False
        
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_extensions:
            print(f"Unsupported file type: {extension}")
            print(f"Supported types: {list(self.supported_extensions.keys())}")
            return False
        
        print(f"\n{'='*60}")
        print(f"Processing: {file_path.name}")
        print(f"Type: {extension.upper()} file")
        print(f"Size: {file_path.stat().st_size / 1024:.1f} KB")
        print(f"{'='*60}")
        
        try:
            # Extract text using appropriate method
            extractor = self.supported_extensions[extension]
            text = extractor(str(file_path))
            
            if text and len(text.strip()) > 10:
                # Generate output filename and check for conflicts
                output_file = self.generate_output_filename(file_path)
                
                if output_file is None:
                    # File already exists from same source, skip processing
                    print(f"⏭️  SKIPPED: File already processed")
                    return True  # Return True as this is not an error
                
                # Save extracted text
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Source File: {file_path.name}\n")
                    f.write(f"File Path: {file_path}\n")
                    f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"File Type: {extension.upper()}\n")
                    f.write(f"Text Length: {len(text)} characters\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(text)
                
                print(f"✓ SUCCESS: Text extracted and saved")
                print(f"  Output file: {output_file.name}")
                print(f"  Text length: {len(text):,} characters")
                print(f"  Lines: {len(text.splitlines()):,}")
                return True
            else:
                print(f"✗ FAILED: No significant text found")
                print(f"  Extracted text length: {len(text.strip()) if text else 0} characters")
                return False
                
        except Exception as e:
            print(f"✗ ERROR: Failed to process file")
            print(f"  Error details: {str(e)}")
            return False
    
    def process_directory(self, directory_path):
        """Process all supported files in a directory"""
        directory_path = Path(directory_path).resolve()
        
        if not directory_path.exists():
            print(f"Error: Directory {directory_path} does not exist")
            return
        
        print(f"\n{'='*80}")
        print(f"SCANNING DIRECTORY: {directory_path}")
        print(f"{'='*80}")
        
        # Find all supported files
        all_files = []
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                all_files.append(file_path)
        
        if not all_files:
            print(f"No supported files found in {directory_path}")
            print(f"Supported extensions: {list(self.supported_extensions.keys())}")
            return
        
        print(f"Found {len(all_files)} supported files:")
        for i, file_path in enumerate(all_files, 1):
            print(f"  {i:2d}. {file_path.name} ({file_path.suffix.upper()})")
        
        # Pre-scan for naming conflicts
        conflicts_summary = self._analyze_directory_conflicts(all_files)
        if conflicts_summary['skipped_files']:
            print(f"\n📋 CONFLICT ANALYSIS:")
            print(f"Files to skip (already processed): {len(conflicts_summary['skipped_files'])}")
            for file_path in conflicts_summary['skipped_files']:
                print(f"  - {file_path.name}")
            if conflicts_summary['alternative_names']:
                print(f"Files requiring alternative names: {len(conflicts_summary['alternative_names'])}")
                for orig, alt in conflicts_summary['alternative_names']:
                    print(f"  - {orig} -> {alt}")
        
        processed_count = 0
        failed_count = 0
        skipped_count = 0
        
        # Process each file
        for i, file_path in enumerate(all_files, 1):
            print(f"\n[{i}/{len(all_files)}] ", end="")
            
            # Check if this file should be skipped
            if file_path in conflicts_summary['skipped_files']:
                print(f"⏭️  SKIPPING: {file_path.name} (already processed)")
                skipped_count += 1
                continue
            
            result = self.process_single_file(file_path)
            if result:
                processed_count += 1
            else:
                failed_count += 1
        
        # Summary
        print(f"\n{'='*80}")
        print(f"PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"Total files found: {len(all_files)}")
        print(f"Successfully processed: {processed_count}")
        print(f"Failed: {failed_count}")
        print(f"Skipped (already processed): {skipped_count}")
        print(f"Success rate: {(processed_count/(len(all_files)-skipped_count)*100):.1f}%" if (len(all_files)-skipped_count) > 0 else "No files to process")
        print(f"Output directory: {self.output_dir}")
        
        # List output files
        output_files = list(self.output_dir.glob("*.txt"))
        if output_files:
            print(f"\nExtracted text files ({len(output_files)}):")
            for output_file in sorted(output_files):
                size = output_file.stat().st_size
                print(f"  - {output_file.name} ({size:,} bytes)")
    
    def _analyze_directory_conflicts(self, all_files):
        """Analyze naming conflicts for a batch of files before processing"""
        conflicts = {
            'skipped_files': [],
            'alternative_names': []
        }
        
        for file_path in all_files:
            # Generate the expected output filename
            import re
            base_name = file_path.stem
            safe_name = re.sub(r'[^\w\-_\.]', '_', base_name)
            expected_output = self.output_dir / f"{safe_name}.txt"
            
            if expected_output.exists():
                conflict_info = self._check_naming_conflict(expected_output, file_path)
                
                if conflict_info['is_same_source']:
                    conflicts['skipped_files'].append(file_path)
                else:
                    # Will need alternative name
                    counter = 1
                    while (self.output_dir / f"{safe_name}_{counter}.txt").exists():
                        counter += 1
                    alt_name = f"{safe_name}_{counter}.txt"
                    conflicts['alternative_names'].append((file_path.name, alt_name))
        
        return conflicts
    
    def list_existing_files(self):
        """List all existing extracted text files"""
        output_files = list(self.output_dir.glob("*.txt"))
        
        if output_files:
            print(f"\nExisting extracted files ({len(output_files)}):")
            for output_file in sorted(output_files):
                size = output_file.stat().st_size
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        first_lines = f.read(200)
                    source_file = "Unknown"
                    for line in first_lines.split('\n'):
                        if line.startswith("Source File:"):
                            source_file = line.split(":", 1)[1].strip()
                            break
                    print(f"  - {output_file.name} ({size:,} bytes) <- {source_file}")
                except:
                    print(f"  - {output_file.name} ({size:,} bytes) <- [Error reading source]")
        else:
            print(f"\nNo existing extracted files in {self.output_dir}")
    
    def clean_output_directory(self):
        """Clean all extracted text files"""
        output_files = list(self.output_dir.glob("*.txt"))
        
        if output_files:
            print(f"Removing {len(output_files)} existing files...")
            for output_file in output_files:
                output_file.unlink()
            print("✓ Output directory cleaned")
        else:
            print("Output directory is already empty")
    
    def check_conflicts_only(self, input_path):
        """Check for naming conflicts without processing files"""
        input_path = Path(input_path).resolve()
        
        if not input_path.exists():
            print(f"Error: Path {input_path} does not exist")
            return
        
        print(f"\n{'='*80}")
        print(f"CHECKING NAMING CONFLICTS: {input_path}")
        print(f"{'='*80}")
        
        # Find all supported files
        if input_path.is_file():
            all_files = [input_path] if input_path.suffix.lower() in self.supported_extensions else []
        else:
            all_files = []
            for file_path in input_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    all_files.append(file_path)
        
        if not all_files:
            print(f"No supported files found")
            return
        
        print(f"Analyzing {len(all_files)} supported files...")
        
        conflicts_summary = self._analyze_directory_conflicts(all_files)
        
        print(f"\n📋 CONFLICT ANALYSIS RESULTS:")
        print(f"{'='*50}")
        
        total_conflicts = len(conflicts_summary['skipped_files']) + len(conflicts_summary['alternative_names'])
        
        if total_conflicts == 0:
            print("✅ No naming conflicts detected!")
            print("All files can be processed without issues.")
        else:
            print(f"⚠️  Found {total_conflicts} potential conflicts:")
            
            if conflicts_summary['skipped_files']:
                print(f"\n🔄 Files that will be SKIPPED (already processed):")
                for file_path in conflicts_summary['skipped_files']:
                    # Get details about existing file
                    import re
                    safe_name = re.sub(r'[^\w\-_\.]', '_', file_path.stem)
                    existing_file = self.output_dir / f"{safe_name}.txt"
                    conflict_info = self._check_naming_conflict(existing_file, file_path)
                    
                    print(f"  - {file_path.name}")
                    print(f"    Reason: Already processed")
                    if conflict_info['extraction_date']:
                        print(f"    Previous extraction: {conflict_info['extraction_date']}")
            
            if conflicts_summary['alternative_names']:
                print(f"\n🔄 Files requiring ALTERNATIVE NAMES:")
                for orig_name, alt_name in conflicts_summary['alternative_names']:
                    print(f"  - {orig_name} -> {alt_name}")
                    print(f"    Reason: Different source file with same base name")
        
        print(f"\nOutput directory: {self.output_dir}")
        
        # Show existing files for context
        existing_files = list(self.output_dir.glob("*.txt"))
        if existing_files:
            print(f"\nExisting extracted files ({len(existing_files)}):")
            for output_file in sorted(existing_files)[:10]:  # Show max 10
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read(200)
                    source_file = "Unknown"
                    for line in content.split('\n'):
                        if line.startswith("Source File:"):
                            source_file = line.split(":", 1)[1].strip()
                            break
                    print(f"  - {output_file.name} <- {source_file}")
                except:
                    print(f"  - {output_file.name} <- [Error reading source]")
            
            if len(existing_files) > 10:
                print(f"  ... and {len(existing_files) - 10} more files")

def main():
    parser = argparse.ArgumentParser(
        description='OCR System for RAG Document Processing (French/Arabic Support)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ocr_system.main_ocr document.pdf
  python -m ocr_system.main_ocr /path/to/documents/
  python -m ocr_system.main_ocr image.png --output ./custom_output/
  python -m ocr_system.main_ocr --list
  python -m ocr_system.main_ocr --clean
        """
    )
    
    # Main positional argument (optional when using utility commands)
    parser.add_argument('input', nargs='?', help='Input file or directory path')
    parser.add_argument('--output', '-o', default='./ocr_results', 
                       help='Output directory (default: ./ocr_results)')
    
    # Utility commands
    parser.add_argument('--list', '-l', action='store_true',
                       help='List all existing extracted files')
    parser.add_argument('--clean', '-c', action='store_true',
                       help='Clean all extracted files from output directory')
    parser.add_argument('--check-conflicts', action='store_true',
                       help='Check for potential naming conflicts without processing')
    
    args = parser.parse_args()
    
    print("OCR System for RAG Document Processing")
    print("====================================")
    print("Supports: PDF, DOCX, TXT, Images (PNG, JPG, TIFF, BMP)")
    print("Languages: French, Arabic, English")
    
    # Initialize OCR system
    ocr_system = OCRSystem(args.output)
    
    # Handle utility commands
    if args.list:
        ocr_system.list_existing_files()
        return
    
    if args.clean:
        ocr_system.clean_output_directory()
        return
    
    if args.check_conflicts:
        if not args.input:
            print("Error: Input path required for conflict checking")
            return
        ocr_system.check_conflicts_only(args.input)
        return
    
    # Main processing
    if not args.input:
        print("Error: Input path required")
        parser.print_help()
        return
    
    # Process input
    input_path = Path(args.input).resolve()
    
    if input_path.is_file():
        ocr_system.process_single_file(input_path)
    elif input_path.is_dir():
        ocr_system.process_directory(input_path)
    else:
        print(f"Error: {input_path} is not a valid file or directory")

if __name__ == "__main__":
    main()
