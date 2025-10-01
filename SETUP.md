# Setup Guide

Quick start guide for installing and using SciPreprocess.

## Installation

### Option 1: Basic Installation (Recommended for Testing)

```bash
# Clone or navigate to the project
cd /path/to/scipreprocess

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with all features
pip install -e ".[all]"
```

### Option 2: Minimal Installation

```bash
# Install only core dependencies
pip install -e .

# Then add features as needed
pip install -e ".[pdf]"    # PDF support
pip install -e ".[nlp]"    # NLP features
pip install -e ".[ml]"     # Machine learning
```

### Option 3: From Requirements File

```bash
# Generate requirements.txt (if needed)
pip install pip-tools
pip-compile pyproject.toml

# Install from requirements
pip install -r requirements.txt
```

## Post-Installation Setup

### 1. Download NLP Models

```bash
# Download spaCy model
python -m spacy download en_core_web_sm

# For scientific text (optional but recommended)
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_core_sci_sm-0.5.1.tar.gz
```

### 2. Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### 3. Install Tesseract (for OCR)

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

## Verification

Test your installation:

```bash
python -c "from scipreprocess import preprocess_file; print('Installation successful!')"
```

Run the example:

```bash
python examples/basic_usage.py
```

## Quick Test

Create a test script `test_install.py`:

```python
from scipreprocess import PipelineConfig
from scipreprocess.preprocessing import clean_text
from scipreprocess.acronyms import detect_acronyms

# Test basic functionality
text = "Natural Language Processing (NLP) is important."
cleaned = clean_text(text)
acronyms = detect_acronyms(text)

print(f"Cleaned text: {cleaned}")
print(f"Detected acronyms: {acronyms}")
print("\n✅ Installation successful!")
```

Run it:
```bash
python test_install.py
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'scipreprocess'`

**Solution:**
```bash
# Make sure you're in the project directory
cd /path/to/scipreprocess

# Install in editable mode
pip install -e .
```

### Issue: `RuntimeError: PyMuPDF not available`

**Solution:**
```bash
pip install PyMuPDF
# or
pip install -e ".[pdf]"
```

### Issue: `OSError: [E050] Can't find model 'en_core_web_sm'`

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: Tesseract not found

**Solution:**
- Install Tesseract (see instructions above)
- Make sure it's in your PATH
- On Windows, you may need to set: `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

### Issue: Import errors with spaCy

**Solution:**
```bash
# Reinstall spaCy and scispacy
pip install --upgrade spacy
pip install scispacy
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_core_sci_sm-0.5.1.tar.gz
```

## Dependency Check

Run this to check what's available:

```python
from scipreprocess.utils import print_availability_status, load_spacy_model

nlp = load_spacy_model('en_core_web_sm')
print_availability_status(nlp)
```

Expected output:
```python
{
    'PyMuPDF': True,
    'python-docx': True,
    'lxml': True,
    'OpenCV': True,
    'pytesseract': True,
    'spaCy': True,
    'pysbd': True,
    'sklearn': True,
    'sentence-transformers': True,
    'faiss': True
}
```

## Development Setup

For contributing to the project:

```bash
# Install with development dependencies
pip install -e ".[all,dev]"

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
pytest

# Format code
black src/ tests/

# Lint
ruff check src/ tests/
```

## Docker Setup (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy and install
COPY . .
RUN pip install -e ".[all]"

# Download models
RUN python -m spacy download en_core_web_sm
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

CMD ["python"]
```

Build and run:
```bash
docker build -t scipreprocess .
docker run -it scipreprocess python examples/basic_usage.py
```

## Next Steps

1. ✅ Check the [README.md](README.md) for usage documentation
2. ✅ Look at [examples/basic_usage.py](examples/basic_usage.py) for code samples
3. ✅ See [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute

## Getting Help

- 📖 Read the documentation in README.md
- 💡 Check the examples in `examples/`
- 🐛 Report bugs or request features via GitHub Issues
- 💬 Ask questions in GitHub Discussions

## Minimal Working Example

After setup, this should work:

```python
from scipreprocess import preprocess_file

# Process a document
doc_json, text = preprocess_file("path/to/paper.pdf")

print(f"Title: {doc_json['metadata']['title']}")
print(f"Sections: {len(doc_json['sections'])}")
print(f"Acronyms: {doc_json['acronyms']}")
```

Happy preprocessing! 🎉

