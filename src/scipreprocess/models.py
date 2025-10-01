"""Data models for the preprocessing pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ParsedDocument:
    """Represents a parsed document with extracted text and metadata.

    Attributes:
        source_path: Path to the source document.
        is_scanned: Whether the document appears to be scanned.
        text_pages: List of text content per page.
        images: List of page images (numpy arrays) if available.
        metadata: Additional metadata about the document.
    """

    source_path: str
    is_scanned: bool
    text_pages: list[str]
    images: list[Any]
    metadata: dict[str, Any]
