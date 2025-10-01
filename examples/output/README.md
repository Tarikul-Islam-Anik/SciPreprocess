# Output Directory

This directory contains the processed output files from the scipreprocess pipeline.

## Output Format
Each processed document generates a JSON file with the following structure:

```json
{
  "metadata": {
    "title": "Paper title",
    "source_file": "path/to/source.pdf",
    "pages": 13
  },
  "abstract": "Paper abstract text...",
  "sections": [
    {"heading": "Introduction", "text": "..."},
    {"heading": "Methods", "text": "..."},
    ...
  ],
  "figures": [
    {"type": "figure", "number": "1", "caption": "...", "page": 1}
  ],
  "tables": [
    {"type": "table", "number": "1", "caption": "...", "page": 3}
  ],
  "equations": [
    {"type": "equation", "number": "1", "page": 2}
  ],
  "references": [
    {"number": "1", "text": "Author et al. ..."}
  ],
  "acronyms": {
    "NLP": "Natural Language Processing",
    "CV": "Computer Vision"
  }
}
```

## Files
Output files are automatically saved here when running the examples.
