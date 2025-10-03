"""Feature extraction including TF-IDF and semantic embeddings."""

from __future__ import annotations

from typing import Any

from .utils import SentenceTransformer, TfidfVectorizer, faiss


def tfidf_features(corpus: list[str]) -> tuple[Any | None, Any | None]:
    """Extract TF-IDF features from a corpus of documents.

    Args:
        corpus: List of document texts.

    Returns:
        Tuple of (feature matrix, fitted vectorizer) or (None, None) if unavailable.
    """
    if TfidfVectorizer is None:
        return None, None

    # Guard against empty/near-empty corpora in tests
    effective_min_df = 1 if len([c for c in corpus if c and c.strip()]) < 2 else 2
    vectorizer = TfidfVectorizer(max_features=50000, ngram_range=(1, 2), min_df=effective_min_df)
    if not corpus:
        return None, vectorizer
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Empty vocabulary; fallback to no features
        return None, vectorizer

    return tfidf_matrix, vectorizer


def maybe_build_embeddings(
    chunks: list[dict[str, Any]], model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> tuple[Any | None, Any | None]:
    """Build semantic embeddings for text chunks.

    Args:
        chunks: List of chunks with 'text' key.
        model_name: Name of the sentence-transformer model.

    Returns:
        Tuple of (embeddings array, FAISS index) or (None, None) if unavailable.
    """
    if SentenceTransformer is None:
        return None, None

    model = SentenceTransformer(model_name)
    texts = [c["text"] for c in chunks]

    embeddings = model.encode(
        texts, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True
    )

    # Build FAISS index if available
    index = None
    if faiss is not None:
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)  # Inner product for normalized vectors
        index.add(embeddings)

    return embeddings, index
