# RAG Chatbot System

A web-based chatbot for administrative document question-answering using RAG technology.

## Architecture

```
stage-RAG/
├── main/              # RAG system with LLM integration
├── backend/           # FastAPI REST API
├── frontend/          # React user interface
└── ocr_results/       # Document corpus
```

## Prerequisites

1. **Python 3.8+**: https://www.python.org/downloads/
2. **Node.js 16+**: https://nodejs.org/
3. **Ollama**: https://ollama.ai/ (optional - system works without it)
4. **Tesseract OCR**: Required for image processing

### Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-ara tesseract-ocr-fra
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### Ollama Models (if using Ollama)

```bash
ollama pull llama3
ollama pull mxbai-embed-large
```

## Quick Start

### Option 1: Automatic Setup

```bash
chmod +x start_system.sh
./start_system.sh
```

### Option 2: Manual Setup

1. **Backend Setup**:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

2. **Frontend Setup** (in new terminal):

```bash
cd frontend
npm install
npm start
```

3. **Initialize RAG** (first time only):

```bash
cd main
pip install -r requirements.txt
python main.py
# Type 'q' to exit after initialization
```

## Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## System Behavior

- **With Ollama**: Full RAG functionality with real LLM responses
- **Without Ollama**: Automatic fallback to mock responses (still functional)

## Troubleshooting

1. **Port conflicts**: Change ports in app.py (backend) or package.json (frontend)
2. **Import errors**: Ensure virtual environment is activated
3. **Ollama issues**: System works in fallback mode without Ollama
4. **Reset database**: Delete `main/chroma_db` folder and rerun `python main.py`

## OCR System Usage

Extract text from documents for RAG training:

```bash
# Install OCR dependencies
cd ocr_system && pip install -r requirements.txt

# Process single file
python -m ocr_system.main_ocr document.pdf

# Process directory
python -m ocr_system.main_ocr /path/to/documents/

# Test OCR system
python test_ocr_system.py
```

## File Structure

```
├── main/               # Original RAG system
│   ├── main.py         # CLI interface
│   ├── vector.py       # Vector store setup
│   └── chroma_db/      # Vector database
├── backend/            # API server
│   ├── app.py          # Main API with Ollama integration
│   └── test_app.py     # Fallback API without Ollama
├── frontend/           # React interface
├── ocr_system/         # OCR text extraction system
│   ├── main_ocr.py     # OCR command line interface
│   ├── ocr_processor.py # Image OCR processing
│   └── document_processor.py # PDF/DOCX processing
├── ocr_results/        # Extracted text files (RAG corpus)
└── test_ocr_system.py  # OCR system test suite
```

### OCR System Features

- **Multi-language support**: French and Arabic text recognition
- **Document processing**: PDF, DOCX, TXT files
- **Image processing**: PNG, JPG, TIFF, BMP, GIF files
- **Smart naming conflict resolution**: 
  - Detects if a file from the same source was already processed
  - Warns when files would be skipped due to existing extraction
  - Generates alternative names for different sources with same base name
  - Preserves extraction metadata for conflict detection
- **Batch processing**: Process entire directories recursively
- **Utility commands**: List, clean, and analyze output files

### OCR CLI Commands

```bash
# Process single file
python -m ocr_system.main_ocr document.pdf

# Process directory
python -m ocr_system.main_ocr dataset/

# Check for naming conflicts without processing
python -m ocr_system.main_ocr dataset/ --check-conflicts

# List existing extracted files
python -m ocr_system.main_ocr --list

# Clean output directory
python -m ocr_system.main_ocr --clean

# Use custom output directory
python -m ocr_system.main_ocr dataset/ --output ./custom_output/
```

### Naming Conflict Handling

The OCR system implements smart naming conflict resolution:

1. **Same source file**: If a file has already been extracted from the same source:
   - Shows warning with extraction date
   - Skips processing to avoid duplication
   - Preserves existing extracted text

2. **Different source, same name**: If different source files have the same base name:
   - Shows warning with source information
   - Creates alternative filename (e.g., `document_1.txt`, `document_2.txt`)
   - Processes both files without data loss

3. **Metadata tracking**: Each extracted file includes:
   - Source filename and full path
   - Extraction date and time
   - File type and text length
   - Original content with proper formatting

## Testing

### OCR System Testing

To test the OCR system functionality:

```bash
# Run the comprehensive OCR test suite
python test_ocr_system.py
```

This test will:
- Create sample files in different formats (PDF, DOCX, TXT, images)
- Test text extraction from each format
- Validate French and Arabic language support
- Test naming conflict handling
- Verify output file creation and content
- Clean up test files automatically

### Manual Testing

1. **Add test documents** to the `dataset/` folder
2. **Check for conflicts** (optional):
   ```bash
   python -m ocr_system.main_ocr dataset/ --check-conflicts
   ```
3. **Process documents**:
   ```bash
   python -m ocr_system.main_ocr dataset/
   ```
4. **Verify results**:
   ```bash
   python -m ocr_system.main_ocr --list
   ```

## Dataset Management

### Adding Documents for OCR Processing

The `dataset/` folder is where you should place documents that you want to process with the OCR system:

#### Supported File Types
- **PDF files**: `.pdf`
- **Word documents**: `.docx`, `.doc`
- **Text files**: `.txt`
- **Image files**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.tif`, `.bmp`, `.gif`

#### Usage Workflow

1. **Add documents**: Place your files in the `dataset/` folder (subdirectories are supported)

2. **Check for conflicts** (optional):
   ```bash
   python -m ocr_system.main_ocr dataset/ --check-conflicts
   ```

3. **Process documents**:
   ```bash
   python -m ocr_system.main_ocr dataset/
   ```

4. **Verify extraction**:
   ```bash
   python -m ocr_system.main_ocr --list
   ```

#### Notes

- Files can be organized in subdirectories within `dataset/`
- Supports French and Arabic text recognition
- Processing the same file twice will be automatically skipped
- Large files may take longer to process
- Image-based PDFs will use OCR (slower but more accurate)
