# Contributing to SciPreprocess

Thank you for your interest in contributing to SciPreprocess! This document provides guidelines and instructions for contributing.

## Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/Tarikul-Islam-Anik/scipreprocess.git
   cd scipreprocess
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[all,dev]"
   ```

4. **Install pre-commit hooks (optional but recommended)**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Project Structure

```
scipreprocess/
├── src/scipreprocess/    # Main package code
│   ├── config.py         # Configuration
│   ├── models.py         # Data models
│   ├── utils.py          # Utilities
│   ├── parsers.py        # Document parsers
│   ├── preprocessing.py  # Text preprocessing
│   ├── acronyms.py       # Acronym handling
│   ├── sectioning.py     # Section detection
│   ├── features.py       # Feature extraction
│   └── pipeline.py       # Main pipeline
├── tests/                # Test files
├── examples/             # Usage examples
└── docs/                 # Documentation
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use prefixes:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/changes

### 2. Make Changes

- Write clean, readable code
- Follow the existing code style
- Add docstrings to functions and classes
- Keep functions focused and modular

### 3. Write Tests

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=scipreprocess --cov-report=html

# Run specific test file
pytest tests/test_pipeline.py -v
```

### 4. Format and Lint

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type check with mypy
mypy src/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add support for new document format"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python Style

- Follow PEP 8
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings (Google style)

Example:
```python
def extract_text(file_path: str, use_ocr: bool = False) -> ParsedDocument:
    """Extract text from a document.
    
    Args:
        file_path: Path to the document file.
        use_ocr: Whether to use OCR for scanned documents.
        
    Returns:
        ParsedDocument with extracted text and metadata.
        
    Raises:
        ValueError: If the file format is not supported.
    """
    # Implementation
```

### Imports

Order imports:
1. Standard library
2. Third-party libraries
3. Local imports

```python
import os
from pathlib import Path
from typing import List, Dict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .models import ParsedDocument
from .utils import load_spacy_model
```

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names

```python
def test_clean_text_removes_citations():
    """Test that citations are properly removed."""
    text = "Some text [1] with citation (Smith, 2020)"
    cleaned = clean_text(text)
    assert "[1]" not in cleaned
    assert "Smith" not in cleaned
```

### Test Coverage

Aim for high test coverage, especially for:
- Core parsing logic
- Text preprocessing functions
- Error handling

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """Short description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 0.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When and why this is raised.
    """
```

### README and Examples

- Update README.md if adding new features
- Add examples to `examples/` directory
- Keep documentation up-to-date

## Adding New Features

### New Document Format

1. Add parser to `parsers.py`
2. Update `detect_format()` function
3. Update `ingest()` function
4. Add tests
5. Update documentation

### New Preprocessing Feature

1. Add function to appropriate module
2. Update pipeline if needed
3. Add configuration option if needed
4. Add tests
5. Update documentation

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted (black)
- [ ] No linting errors (ruff)
- [ ] Documentation is updated
- [ ] New features have tests
- [ ] Commit messages are clear

### PR Description

Include:
1. What changes were made
2. Why these changes are needed
3. How to test the changes
4. Any breaking changes
5. Related issues

Example:
```markdown
## Description
Add support for parsing EPUB documents.

## Motivation
Many scientific documents are distributed as EPUB files.

## Changes
- Added `extract_text_from_epub()` in parsers.py
- Updated format detection
- Added tests for EPUB parsing

## Testing
- Added unit tests for EPUB parsing
- Tested with sample EPUB files

## Breaking Changes
None

## Related Issues
Closes #42
```

## Review Process

1. Automated checks run (tests, linting)
2. Code review by maintainers
3. Address feedback
4. Merge when approved

## Community

- Be respectful and constructive
- Help others in issues and discussions
- Share your use cases and feedback

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

