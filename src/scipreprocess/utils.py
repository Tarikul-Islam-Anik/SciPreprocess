"""Utility functions for dependency management and model loading."""

from __future__ import annotations

from typing import Any

# Guarded imports for optional dependencies
fitz: Any | None = None
try:
    import fitz as _fitz  # PyMuPDF

    fitz = _fitz
except Exception:
    pass

docx: Any | None = None
try:
    import docx as _docx  # python-docx

    docx = _docx
except Exception:
    pass

ET: Any | None = None
try:
    import lxml.etree as _ET

    ET = _ET
except Exception:
    pass

cv2: Any | None = None
try:
    import cv2 as _cv2  # OpenCV

    cv2 = _cv2
except Exception:
    pass

pytesseract: Any | None = None
try:
    import pytesseract as _pytesseract

    pytesseract = _pytesseract
except Exception:
    pass

nltk: Any | None = None
try:
    import nltk as _nltk

    nltk = _nltk
except Exception:
    pass

spacy: Any | None = None
AbbreviationDetector: Any | None = None
try:
    import spacy as _spacy
    from scispacy.abbreviation import AbbreviationDetector as _AbbreviationDetector  # type: ignore

    spacy = _spacy
    AbbreviationDetector = _AbbreviationDetector
except Exception:
    pass

pysbd: Any | None = None
try:
    import pysbd as _pysbd  # type: ignore

    pysbd = _pysbd
except Exception:
    pass

TfidfVectorizer: Any | None = None
try:
    from sklearn.feature_extraction.text import TfidfVectorizer as _TfidfVectorizer

    TfidfVectorizer = _TfidfVectorizer
except Exception:
    pass

SentenceTransformer: Any | None = None
try:
    from sentence_transformers import SentenceTransformer as _SentenceTransformer

    SentenceTransformer = _SentenceTransformer
except Exception:
    pass

faiss: Any | None = None
try:
    import faiss as _faiss  # type: ignore

    faiss = _faiss
except Exception:
    pass


def is_available(name: str) -> bool:
    """Check if a dependency is available."""
    return globals().get(name) is not None


def ensure_nltk_resources() -> None:
    """Download required NLTK resources if not present."""
    if nltk is None:
        return

    resources = [
        ("tokenizers/punkt", "punkt"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
    ]

    for resource_path, download_name in resources:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(download_name, quiet=True)


def load_spacy_model(model_name: str = "en_core_web_sm") -> Any | None:
    """Load a spaCy model with optional abbreviation detector.

    Args:
        model_name: Name of the spaCy model to load.

    Returns:
        Loaded spaCy nlp object or None if unavailable.
    """
    if spacy is None:
        return None

    try:
        nlp = spacy.load(model_name)
    except Exception:
        return None

    # Try to add abbreviation detector
    if AbbreviationDetector is not None:
        try:
            nlp.add_pipe("abbreviation_detector")
        except Exception:
            try:
                abbreviation_pipe = AbbreviationDetector(nlp)
                nlp.add_pipe(abbreviation_pipe)
            except Exception:
                pass

    return nlp


def print_availability_status(nlp_model: Any | None = None) -> dict[str, bool]:
    """Print and return the availability status of all dependencies.

    Args:
        nlp_model: Optional loaded spaCy model to check.

    Returns:
        Dictionary mapping dependency names to availability status.
    """
    status = {
        "PyMuPDF": is_available("fitz"),
        "python-docx": is_available("docx"),
        "lxml": is_available("ET"),
        "OpenCV": is_available("cv2"),
        "pytesseract": is_available("pytesseract"),
        "spaCy": nlp_model is not None,
        "pysbd": is_available("pysbd"),
        "sklearn": TfidfVectorizer is not None,
        "sentence-transformers": SentenceTransformer is not None,
        "faiss": faiss is not None,
    }
    print(status)
    return status
