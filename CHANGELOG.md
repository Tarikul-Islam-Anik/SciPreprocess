# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Add support for more document formats (EPUB, HTML)
- Improve table extraction accuracy
- Add support for equation parsing
- Enhanced figure caption extraction
- Multi-language support

## [0.1.0] - 2025-10-01

### Added
- Initial release of SciPreprocess
- Multi-format document parsing (PDF, DOCX, LaTeX, JATS XML, TXT)
- OCR support for scanned documents using Tesseract
- Text cleaning and normalization
- NLP processing with NLTK and spaCy
- Scientific text support with scispacy
- Section detection and splitting
- Acronym detection and expansion
- TF-IDF feature extraction
- Semantic embeddings with sentence-transformers
- FAISS indexing for similarity search
- Modular pipeline architecture
- Comprehensive configuration system
- Example scripts and documentation
- Unit tests and validation framework

### Features
- **Parsers**: Support for PDF (PyMuPDF), DOCX (python-docx), LaTeX, JATS XML, and plain text
- **Preprocessing**: Citation removal, unicode normalization, tokenization, lemmatization
- **Acronyms**: Pattern-based and scispacy-based acronym detection
- **Sectioning**: Smart section splitting with configurable chunking
- **Features**: TF-IDF vectorization and semantic embeddings
- **Models**: Structured output format optimized for LLM consumption

### Documentation
- Comprehensive README with installation and usage guides
- Contributing guidelines
- Setup and quick start guides
- Code examples
- Validation framework documentation

### Known Issues
- Table extraction accuracy varies by PDF format
- Equation parsing is basic (placeholder)
- Figure extraction needs improvement
- Some edge cases in section detection


### Added
- Initial prototype and research code
- Basic PDF parsing functionality
- Simple text cleaning

---

## Release Notes

### Version 0.1.0 - Initial Public Release

This is the first public release of SciPreprocess, designed to fill the gap in scientific document preprocessing for NLP and LLM applications.

**Target Audience:**
- Researchers working with scientific literature
- NLP practitioners processing academic papers
- Anyone building LLM applications that need structured scientific text

**What's Included:**
- Production-ready pipeline for document preprocessing
- Modular architecture - use only what you need
- Extensive documentation and examples
- MIT License for maximum flexibility

**Getting Started:**
```bash
pip install -e ".[all]"
python examples/basic_usage.py
```

**Feedback Welcome:**
This is an early release. Please report bugs, request features, or contribute improvements via GitHub Issues and Pull Requests.
