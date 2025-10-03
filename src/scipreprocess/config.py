"""Configuration management for the preprocessing pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PipelineConfig:
    """Configuration for the document preprocessing pipeline.

    Attributes:
        use_layout: Enable layout analysis (requires OpenCV).
        use_ocr: Enable OCR for scanned documents (requires pytesseract).
        use_spacy: Use spaCy for NLP tasks (tokenization, lemmatization).
        use_semantic_embeddings: Generate semantic embeddings for chunks.
        spacy_model: Name of the spaCy model to load.
        embedding_model: Name of the sentence-transformer model.
        chunk_target_sentences: Min and max sentences per chunk.
    """

    use_layout: bool = False
    use_ocr: bool = False
    use_spacy: bool = True
    use_semantic_embeddings: bool = False
    # Backend selection for parsing; "auto" defaults to local
    parser_backend: str = "auto"
    spacy_model: str = "en_core_web_sm"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_target_sentences: tuple[int, int] = (3, 8)
