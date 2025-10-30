"""Summarization utilities for short scientific text spans."""

from __future__ import annotations

from collections import Counter
import re
from typing import Any, Sequence

from .preprocessing import clean_text, lemmatize, remove_stopwords, sentence_split, tokenize


def _basic_tokenize(text: str) -> list[str]:
    """Lightweight tokenizer that keeps alphabetic tokens only."""

    return [tok for tok in re.findall(r"[A-Za-z][A-Za-z0-9\-']*", text) if tok]


def _prepare_tokens(text: str, nlp_model: Any | None = None) -> list[str]:
    """Tokenize, normalize, and filter tokens for scoring."""

    tokens = tokenize(text, nlp_model)
    if not tokens and nlp_model is not None:
        tokens = tokenize(text, None)

    filtered = [tok for tok in tokens if tok and re.search(r"[A-Za-z]", tok)]
    if not filtered:
        filtered = _basic_tokenize(text)

    filtered = remove_stopwords(filtered, nlp_model) if filtered else filtered

    if filtered:
        lemmas = lemmatize(filtered, nlp_model)
        if not lemmas and nlp_model is not None:
            lemmas = lemmatize(filtered, None)
    else:
        lemmas = []

    normalized = [tok.lower() for tok in lemmas if tok]
    if not normalized:
        normalized = [tok.lower() for tok in filtered if tok]

    return normalized


def _score_sentences(
    sentences: Sequence[str], token_weights: Counter[str], nlp_model: Any | None = None
) -> list[tuple[int, float]]:
    """Score sentences according to token weights."""

    scores: list[tuple[int, float]] = []
    for idx, sentence in enumerate(sentences):
        sent_tokens = _prepare_tokens(sentence, nlp_model)
        if not sent_tokens:
            sent_tokens = _basic_tokenize(sentence)

        if not sent_tokens:
            scores.append((idx, 0.0))
            continue

        score = sum(token_weights.get(tok, 0) for tok in sent_tokens) / len(sent_tokens)
        scores.append((idx, score))

    return scores


def _trim_to_word_limit(text: str, word_limit: int) -> str:
    """Trim text to a maximum word length while preserving whole words."""

    if word_limit <= 0:
        return ""

    words = text.split()
    if len(words) <= word_limit:
        return text

    return " ".join(words[:word_limit]) + " ..."


def summarize_caption(
    caption: str,
    nlp_model: Any | None = None,
    max_sentences: int = 2,
    max_words: int = 60,
) -> str:
    """Generate a concise summary for a figure caption."""

    if not caption:
        return ""

    cleaned = clean_text(caption, lower=False)
    if not cleaned:
        return ""

    sentences: list[str] = []
    if nlp_model is not None:
        try:
            doc = nlp_model(cleaned)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        except Exception:
            sentences = []

    if not sentences:
        sentences = sentence_split(cleaned)

    if not sentences:
        return _trim_to_word_limit(cleaned, max_words)

    if len(sentences) == 1:
        return _trim_to_word_limit(sentences[0], max_words)

    caption_tokens = _prepare_tokens(cleaned, nlp_model)
    if not caption_tokens:
        caption_tokens = _prepare_tokens(cleaned, None)

    token_weights: Counter[str]
    if caption_tokens:
        token_weights = Counter(caption_tokens)
    else:
        token_weights = Counter(_basic_tokenize(cleaned))

    scored = _score_sentences(sentences, token_weights, nlp_model)
    scored.sort(key=lambda item: (-item[1], item[0]))

    top_n = min(max_sentences, len(sentences))
    selected_indices = sorted(idx for idx, _ in scored[:top_n])

    summary_parts = [sentences[idx] for idx in selected_indices]
    summary = " ".join(summary_parts).strip()

    if not summary:
        summary = sentences[0]

    summary = _trim_to_word_limit(summary, max_words)

    # Guard against summaries that are longer than the cleaned caption
    if len(summary) > len(cleaned):
        summary = _trim_to_word_limit(cleaned, max_words)

    return summary

