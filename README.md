# SciPreprocess

[![CI](https://github.com/Tarikul-Islam-Anik/scipreprocess/actions/workflows/ci.yml/badge.svg)](https://github.com/Tarikul-Islam-Anik/scipreprocess/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A modular, open-source pipeline for preprocessing scientific documents in multiple formats (PDF, DOCX, LaTeX, JATS XML, TXT) for LLM consumption and NLP analysis.

## Features

- 📄 **Multi-format support**: PDF, DOCX, TEX, JATS XML, and plain text
- 🔍 **OCR support**: Extract text from scanned documents with Tesseract
- 🧹 **Text cleaning**: Remove citations, normalize unicode, clean special characters
- 🔤 **NLP processing**: Tokenization, lemmatization, stopword removal using spaCy or NLTK
- 📑 **Section detection**: Automatically identify paper sections (Abstract, Introduction, etc.)
- 🔗 **Acronym handling**: Detect and expand acronyms using scispacy
- 📊 **Feature extraction**: TF-IDF and semantic embeddings with sentence-transformers
- 🔎 **Semantic search**: FAISS indexing for efficient similarity search
- 🧩 **Modular design**: Use only the components you need
- 📊 **Export formats**: JSON (default) or CSV output with `--format` flag

## Installation

### From PyPI (Recommended)

```bash
pip install scipreprocess
```

### With Optional Dependencies

Install specific feature sets:

```bash
# PDF support
pip install "scipreprocess[pdf]"

# NLP features
pip install "scipreprocess[nlp]"

# Machine learning features
pip install "scipreprocess[ml]"

# OCR support
pip install "scipreprocess[ocr]"

# Everything
pip install "scipreprocess[all]"
```

### Development Installation

For development or from source:

```bash
git clone https://github.com/Tarikul-Islam-Anik/scipreprocess.git
cd scipreprocess
pip install -e ".[all,dev]"
```

### Post-Installation Setup

For NLP features, download required models:

```bash
# Download spaCy model
python -m spacy download en_core_web_sm

# Install scispacy model (optional but recommended)
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_core_sci_sm-0.5.1.tar.gz
```

## Quick Start

### Basic Usage

```python
from scipreprocess import preprocess_file

# Process a single document
doc_json, clean_text = preprocess_file("path/to/paper.pdf")

# Access the results
print(doc_json['metadata']['title'])
print(doc_json['abstract'])
print(doc_json['sections'])
print(doc_json['acronyms'])
```

### Process Multiple Documents

```python
from scipreprocess import preprocess_documents

# Process multiple documents
files = ["paper1.pdf", "paper2.docx", "paper3.tex"]
results = preprocess_documents(files)

# Access results
documents = results['documents']
tfidf_matrix = results['tfidf']['X']
vectorizer = results['tfidf']['vectorizer']
chunks = results['chunks']
embeddings = results['embeddings']  # if enabled
```

### Custom Configuration

```python
from scipreprocess import PipelineConfig
from scipreprocess.pipeline import PreprocessingPipeline

# Configure the pipeline
config = PipelineConfig(
    use_ocr=True,
    use_spacy=True,
    use_semantic_embeddings=True,
    spacy_model='en_core_sci_sm',
    embedding_model='sentence-transformers/all-MiniLM-L6-v2',
    chunk_target_sentences=(3, 8)
)

# Create pipeline with custom config
pipeline = PreprocessingPipeline(config)
doc_json, text = pipeline.preprocess_file("paper.pdf")
```

## Command Line Interface

SciPreprocess includes a command-line interface for easy document processing:

### Basic CLI Usage

```bash
# Process documents and output JSON (default)
scipreprocess document1.pdf document2.docx

# Process with OCR enabled
scipreprocess --ocr scanned_document.pdf

# Process with layout analysis
scipreprocess --layout complex_document.pdf

# Convert text to lowercase
scipreprocess --lower document.pdf
```

### Export Formats

The CLI supports two output formats:

```bash
# JSON output (default)
scipreprocess document.pdf

# CSV output - one row per document
scipreprocess document.pdf --format csv

# Save to file
scipreprocess document.pdf --format csv --out results.csv
```

### CLI Options

- `inputs`: Paths to documents to process (required)
- `--backend {auto,docling,local}`: Parser backend (default: auto)
- `--ocr`: Enable OCR for scanned documents
- `--layout`: Enable layout analysis
- `--lower`: Convert text to lowercase
- `--format {json,csv}`: Output format (default: json)
- `--out FILE`: Output file path (default: stdout)

### CSV Output Format

When using `--format csv`, the output contains one row per document with flattened nested data:

```csv
abstract,metadata.source_file,metadata.title,metadata.pages,sections
"Abstract text...","document.pdf","Paper Title",12,"[{""heading"": ""Introduction"", ""text"": ""..."", ...}]"
```

- Nested dictionaries are flattened with dotted keys (e.g., `metadata.title`)
- Arrays are JSON-stringified (e.g., `sections`, `figures`, `tables`)
- Only document data is included (excludes `tfidf`, `chunks`, `embeddings`, `index`)

## Pipeline Components

The pipeline is organized into modular components:

- **`parsers`**: Document ingestion (PDF, DOCX, TEX, XML, TXT)
- **`preprocessing`**: Text cleaning, tokenization, lemmatization
- **`acronyms`**: Acronym detection and expansion
- **`sectioning`**: Section splitting and chunking
- **`features`**: TF-IDF and semantic embeddings
- **`pipeline`**: Main orchestration

## Architecture

```
scipreprocess/
├── config.py          # Configuration dataclasses
├── models.py          # Data models (ParsedDocument)
├── utils.py           # Dependency management and helpers
├── parsers.py         # Document parsers for each format
├── preprocessing.py   # Text cleaning and NLP
├── acronyms.py        # Acronym detection/expansion
├── sectioning.py      # Section splitting and chunking
├── features.py        # Feature extraction (TF-IDF, embeddings)
└── pipeline.py        # Main pipeline orchestration
```

## Output Format

The pipeline produces structured JSON for each document:

```python
{
    "metadata": {
        "title": "Paper Title",
        "source_file": "path/to/file.pdf",
        "pages": 12
    },
    "abstract": "Abstract text...",
    "sections": [
        {"heading": "Introduction", "text": "..."},
        {"heading": "Methods", "text": "..."},
        ...
    ],
    "acronyms": {
        "NLP": "Natural Language Processing",
        "ML": "Machine Learning"
    },
    "figures": [],
    "tables": [],
    "equations": [],
    "references": []
}
```

## Dependencies

### Required
- `unidecode`: Unicode normalization

### Optional
- `PyMuPDF`: PDF parsing
- `python-docx`: DOCX parsing
- `lxml`: XML parsing
- `opencv-python` + `pytesseract`: OCR support
- `nltk`: Basic NLP (tokenization, stopwords, lemmatization)
- `spacy` + `scispacy`: Advanced NLP and abbreviation detection
- `pysbd`: Sentence boundary detection
- `scikit-learn`: TF-IDF vectorization
- `sentence-transformers`: Semantic embeddings
- `faiss`: Similarity search

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Tarikul-Islam-Anik/scipreprocess.git
cd scipreprocess

# Install in development mode with dev dependencies
pip install -e ".[all,dev]"

# Run tests
pytest

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## Documentation

- Examples: [examples/basic_usage.py](examples/basic_usage.py)

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scipreprocess --cov-report=html
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this pipeline in your research, please cite:

```bibtex
@software{scipreprocess,
  title = {SciPreprocess: A Modular Scientific Document Preprocessing Pipeline},
  author = {Anik, Tarikul Islam},
  year = {2025},
  url = {https://github.com/Tarikul-Islam-Anik/scipreprocess}
}
```

## Acknowledgments

- Built with [spaCy](https://spacy.io/), [scispacy](https://allenai.github.io/scispacy/), and [sentence-transformers](https://www.sbert.net/)
- Inspired by the needs of scientific text processing and NLP research

