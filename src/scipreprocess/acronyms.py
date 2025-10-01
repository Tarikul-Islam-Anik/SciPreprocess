"""Acronym detection and expansion utilities."""

from __future__ import annotations

import re
from typing import Any

# Regex pattern for acronym definitions: "Long Form (SF)"
ACRONYM_DEF = re.compile(r"\b([A-Za-z][A-Za-z\- ]{2,}?)\s*\(([A-Z]{2,})\)")


def detect_acronyms(text: str, nlp_model: Any | None = None) -> dict[str, str]:
    """Detect acronyms and their definitions in text.

    Uses spaCy with scispacy abbreviation detector if available,
    falls back to regex-based detection.

    Args:
        text: Input text to analyze.
        nlp_model: Optional spaCy model with abbreviation detector.

    Returns:
        Dictionary mapping acronyms to their full forms.
    """
    mapping: dict[str, str] = {}

    # Try spaCy abbreviation detector
    if nlp_model is not None and hasattr(nlp_model, "pipe_names"):
        if "abbreviation_detector" in nlp_model.pipe_names or any(
            "AbbreviationDetector" in p for p in nlp_model.pipe_names
        ):
            try:
                doc = nlp_model(text)
                abbrs = getattr(doc._, "abbreviations", [])

                for span in abbrs:
                    long_form = span._.long_form.text if hasattr(span._, "long_form") else ""
                    short_form = span.text

                    if long_form and short_form and short_form.isupper():
                        mapping[short_form] = long_form
            except Exception:
                pass

    # Regex-based fallback
    for m in ACRONYM_DEF.finditer(text):
        long_form, short = m.group(1).strip(), m.group(2).strip()
        if short.isupper() and long_form:
            mapping.setdefault(short, long_form)

    return mapping


def expand_acronyms(text: str, mapping: dict[str, str]) -> str:
    """Expand acronyms in text using a mapping.

    Args:
        text: Input text with acronyms.
        mapping: Dictionary mapping acronyms to full forms.

    Returns:
        Text with acronyms expanded.
    """
    if not mapping:
        return text

    # Build pattern matching all acronyms (longest first to avoid partial matches)
    pattern = re.compile(
        r"\b("
        + "|".join(re.escape(k) for k in sorted(mapping.keys(), key=len, reverse=True))
        + r")\b"
    )

    def repl(m):
        key = m.group(1)
        return mapping.get(key, key)

    return pattern.sub(repl, text)
