# Quick Start Guide

Get started with SciPreprocess in 5 minutes!

## 1. Install

```bash
# Install the package
pip install -e ".[all]"

# Download NLP models
python -m spacy download en_core_web_sm
```

## 2. Basic Usage

```python
from scipreprocess import preprocess_file

# Process a single document
doc_json, clean_text = preprocess_file("path/to/paper.pdf")

# Access the results
print(doc_json['metadata']['title'])
print(doc_json['abstract'])
print(doc_json['acronyms'])
```

## 3. Process Multiple Documents

```python
from scipreprocess import preprocess_documents

# Process multiple documents
files = ["paper1.pdf", "paper2.docx", "paper3.tex"]
results = preprocess_documents(files)

# Access results
for doc in results['documents']:
    print(doc['metadata']['title'])
```

## 4. Custom Configuration

```python
from scipreprocess import PipelineConfig
from scipreprocess.pipeline import PreprocessingPipeline

# Configure the pipeline
config = PipelineConfig(
    use_ocr=True,
    use_spacy=True,
    use_semantic_embeddings=True
)

# Create pipeline
pipeline = PreprocessingPipeline(config)
doc_json, text = pipeline.preprocess_file("paper.pdf")
```

## Need More Help?

- 📖 **Full documentation**: See [README.md](README.md)
- 🚀 **Installation guide**: See [SETUP.md](SETUP.md)

That's it! You're ready to go! 🎉
