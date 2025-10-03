"""Text preprocessing utilities including cleaning, tokenization, and lemmatization."""

from __future__ import annotations

import re
from typing import Any

from unidecode import unidecode

from .utils import cv2, nltk, pytesseract

# Citation patterns
CITATION_PATTERN = re.compile(r"\(([A-Z][A-Za-z\-]+)( et al\.)?,\s*\d{4}[a-z]?\)")
BRACKET_CITATION = re.compile(r"\[[0-9]{1,3}\]")

# NLTK resources
STOPWORDS = set()
WN = None

if nltk is not None:
    try:
        from nltk.corpus import stopwords as nltk_stopwords

        STOPWORDS = set(nltk_stopwords.words("english"))
    except Exception:
        STOPWORDS = set()

    try:
        from nltk.stem import WordNetLemmatizer

        WN = WordNetLemmatizer()
    except Exception:
        WN = None


def clean_text(text: str, lower: bool = False) -> str:
    """Clean and normalize text.

    Removes unicode artifacts, citations, special characters, and normalizes whitespace.

    Args:
        text: Input text to clean.
        lower: Whether to convert to lowercase.

    Returns:
        Cleaned text.
    """
    # Unicode normalization
    t = unidecode(text)

    # Replace non-breaking spaces
    t = t.replace("\u00a0", " ")

    # Normalize whitespace
    t = re.sub(r"\s+", " ", t)

    # Remove citations
    t = BRACKET_CITATION.sub("", t)
    t = CITATION_PATTERN.sub("", t)

    # Remove special characters (keep basic punctuation)
    t = re.sub(r"[^\w\s\-.,;:()\[\]]", " ", t)

    # Final whitespace normalization
    t = re.sub(r"\s+", " ", t).strip()

    if lower:
        t = t.lower()

    return t


def tokenize(text: str, nlp_model: Any | None = None) -> list[str]:
    """Tokenize text into words.

    Uses spaCy if available, falls back to NLTK, then regex.

    Args:
        text: Input text to tokenize.
        nlp_model: Optional spaCy model to use.

    Returns:
        List of tokens.
    """
    if nlp_model is not None:
        doc = nlp_model.make_doc(text)
        return [t.text for t in doc if not t.is_space]

    if nltk is not None:
        try:
            tokens: list[str] = nltk.word_tokenize(text)
            return tokens
        except Exception:
            # Fallback when punkt resources are missing
            pass

    return re.findall(r"[A-Za-z0-9_\-']+", text)


def lemmatize(tokens: list[str], nlp_model: Any | None = None) -> list[str]:
    """Lemmatize tokens to their base forms.

    Uses spaCy if available, falls back to NLTK WordNet lemmatizer.

    Args:
        tokens: List of tokens to lemmatize.
        nlp_model: Optional spaCy model to use.

    Returns:
        List of lemmatized tokens.
    """
    if nlp_model is not None:
        doc = nlp_model(" ".join(tokens))
        return [t.lemma_ if t.lemma_ else t.text for t in doc if not t.is_space]

    if WN is not None:
        return [WN.lemmatize(tok) for tok in tokens]

    return tokens


def remove_stopwords(tokens: list[str], nlp_model: Any | None = None) -> list[str]:
    """Remove stopwords from tokens.

    Uses spaCy if available, falls back to NLTK stopwords.

    Args:
        tokens: List of tokens to filter.
        nlp_model: Optional spaCy model to use.

    Returns:
        List of tokens with stopwords removed.
    """
    if nlp_model is not None:
        doc = nlp_model.make_doc(" ".join(tokens))
        return [t.text for t in doc if not (t.is_space or t.is_stop)]

    if STOPWORDS:
        return [t for t in tokens if t.lower() not in STOPWORDS]

    return tokens


def ocr_image_to_text(img) -> str:
    """Apply OCR to an image to extract text.

    Args:
        img: Image as numpy array or PyMuPDF pixmap.

    Returns:
        Extracted text or empty string if OCR fails.
    """
    if pytesseract is None or img is None:
        return ""

    try:
        if cv2 is not None:
            # Preprocess image for better OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        else:
            gray = img

        text: str = pytesseract.image_to_string(gray)
        return text
    except Exception:
        return ""


def sentence_split(text: str) -> list[str]:
    """Split text into sentences.

    Uses pysbd if available, falls back to regex-based splitting.

    Args:
        text: Input text to split.

    Returns:
        List of sentences.
    """
    from .utils import pysbd

    if pysbd is not None:
        seg = pysbd.Segmenter(language="en", clean=True)
        return [s.strip() for s in seg.segment(text) if s.strip()]

    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
