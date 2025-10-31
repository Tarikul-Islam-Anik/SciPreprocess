"""Bindings for the optional Rust-based PDF ingestion backend."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Dict

try:  # pragma: no cover - exercised via integration tests
    _native = import_module("pdf_ingest_rs")
except Exception:  # pragma: no cover - gracefully handle missing builds
    _native = None


def is_available() -> bool:
    """Return ``True`` when the compiled Rust extension can be imported."""

    return _native is not None


def extract_text_from_pdf(
    pdf_path: str, use_ocr: bool = False, use_layout: bool = False
) -> Dict[str, Any]:
    """Mirror :func:`scipreprocess.parsers.extract_text_from_pdf` in Rust."""

    if _native is None:  # pragma: no cover - import guarded by availability checks
        raise RuntimeError(
            "pdf_ingest_rs extension is not available. Build the Rust module first."
        )

    payload = _native.extract_text_from_pdf(pdf_path, use_ocr, use_layout)
    if not isinstance(payload, dict):  # pragma: no cover - defensive programming
        raise RuntimeError("Unexpected payload returned from pdf_ingest_rs")

    return payload


__all__ = ["extract_text_from_pdf", "is_available"]
