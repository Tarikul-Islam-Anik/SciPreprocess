"""Feature extraction including TF-IDF and semantic embeddings."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .utils import TfidfVectorizer, SentenceTransformer, faiss


def tfidf_features(corpus: List[str]) -> Tuple[Optional[Any], Optional[Any]]:
    """Extract TF-IDF features from a corpus of documents.
    
    Args:
        corpus: List of document texts.
        
    Returns:
        Tuple of (feature matrix, fitted vectorizer) or (None, None) if unavailable.
    """
    if TfidfVectorizer is None:
        return None, None
    
    vectorizer = TfidfVectorizer(
        max_features=50000,
        ngram_range=(1, 2),
        min_df=2
    )
    X = vectorizer.fit_transform(corpus)
    
    return X, vectorizer


def maybe_build_embeddings(
    chunks: List[Dict[str, Any]],
    model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
) -> Tuple[Optional[Any], Optional[Any]]:
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
    texts = [c['text'] for c in chunks]
    
    embeddings = model.encode(
        texts,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    
    # Build FAISS index if available
    index = None
    if faiss is not None:
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)  # Inner product for normalized vectors
        index.add(embeddings)
    
    return embeddings, index

