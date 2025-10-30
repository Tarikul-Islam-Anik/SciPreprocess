"""Utility helpers for generating short summaries of document artifacts."""

from __future__ import annotations

from typing import Iterable

from .preprocessing import clean_text


def _first_sentences(text: str, max_sentences: int = 2) -> str:
    """Return the first ``max_sentences`` sentences from the input text."""

    if not text:
        return ""

    # A lightweight sentence split using punctuation boundaries keeps the
    # implementation dependency-free for tests.
    sentences: list[str] = []
    buffer: list[str] = []
    delimiters: Iterable[str] = {".", "!", "?"}

    for char in text:
        buffer.append(char)
        if char in delimiters:
            sentence = "".join(buffer).strip()
            if sentence:
                sentences.append(sentence)
            buffer = []
        if len(sentences) >= max_sentences:
            break

    if len(sentences) < max_sentences and buffer:
        tail = "".join(buffer).strip()
        if tail:
            sentences.append(tail)

    return " ".join(sentences[:max_sentences]).strip()


def summarize_caption(caption: str | object, *, max_sentences: int = 2) -> str:
    """Summarize a figure caption to a concise, cleaned snippet.

    Non-string inputs are ignored to prevent downstream processing errors.
    """

    if not isinstance(caption, str):
        return ""

    cleaned = clean_text(caption)
    return _first_sentences(cleaned, max_sentences=max_sentences)
