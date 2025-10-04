"""Scientific Document Preprocessing Pipeline.

A modular pipeline for preprocessing scientific documents (PDF, DOCX, TEX, XML, TXT)
with support for OCR, text cleaning, acronym detection, section splitting, and embeddings.
"""

from __future__ import annotations

from .config import PipelineConfig
from .models import ParsedDocument
from .pipeline import preprocess_documents, preprocess_file
from .utils import serialize_output

__version__ = "0.1.0"

__all__ = [
    "PipelineConfig",
    "ParsedDocument",
    "preprocess_file",
    "preprocess_documents",
    "serialize_output",
]
