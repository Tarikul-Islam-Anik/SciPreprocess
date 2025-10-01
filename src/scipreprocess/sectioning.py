"""Section detection and text chunking utilities."""

from __future__ import annotations

import re
from typing import Any, cast

from .preprocessing import sentence_split

# Common scientific paper section headings (fallback)
SECTION_HEADINGS = [
    "Abstract",
    "Introduction",
    "Background",
    "Related Work",
    "Methods",
    "Materials and Methods",
    "Results",
    "Discussion",
    "Conclusion",
    "Conclusions",
    "Acknowledgments",
    "References",
    "Appendix",
]

# Regex to match section headings (with optional numbering)
HEADING_REGEX = re.compile(
    r"^(\d+(?:\.\d+)*\.?)?\s*({})\b".format("|".join(re.escape(h) for h in SECTION_HEADINGS)),
    re.IGNORECASE,
)


def is_section_heading(line: str) -> str | None:
    """Check if a line is a section heading.

    Args:
        line: Line of text to check.

    Returns:
        Extracted heading text if it's a heading, None otherwise.
    """
    line = line.strip()

    # Skip empty lines or very short lines
    if not line or len(line) < 3:
        return None

    # Skip lines with many punctuation marks (likely text, not heading)
    punct_count = sum(1 for c in line if c in ".,;:()\"'[]{}")
    if punct_count > 3:
        return None

    # Skip lines that look like author names or affiliations
    # (contain email-like patterns, @ symbols, multiple capital letters in sequence)
    if "@" in line or "edu" in line.lower() or "org" in line.lower():
        return None

    # Skip lines with many numbers (likely page numbers, dates, etc.)
    if sum(1 for c in line if c.isdigit()) > len(line) * 0.3:
        return None

    # Check against common headings first (highest confidence)
    match = HEADING_REGEX.match(line)
    if match:
        return match.group(2).title()

    # Check for numbered sections (e.g., "1 Introduction", "2.3 Methods")
    numbered_pattern = re.compile(r"^(\d+(?:\.\d+)*\.?)\s+([A-Z][A-Za-z\s]{2,60})$")
    match = numbered_pattern.match(line)
    if match:
        heading = match.group(2).strip()
        # Make sure it's not just a person's name
        words = heading.split()
        if len(words) >= 2 or heading.lower() in [h.lower() for h in SECTION_HEADINGS]:
            return heading

    # Check for all-caps headings (common in papers)
    if line.isupper() and 5 <= len(line) <= 60:
        # Must be actual words, not acronyms or random caps
        words = line.split()
        if len(words) >= 2 and all(len(w) >= 3 for w in words):
            return line.title()

    return None


def split_into_sections_with_toc(text: str, toc: list) -> list[dict[str, Any]]:
    """Split text into sections using table of contents information.

    Args:
        text: Input text to split into sections.
        toc: Table of contents from PDF (list of [level, title, page] entries).

    Returns:
        List of dictionaries with 'heading' and 'text' keys.
    """
    if not toc:
        return split_into_sections(text)

    sections: list[dict[str, Any]] = []

    # Extract section titles from TOC
    toc_headings = []
    for entry in toc:
        if len(entry) >= 2:
            level = entry[0]
            title = entry[1]
            # Only use top-level sections
            if level <= 2 and title.strip():
                toc_headings.append(title.strip())

    if not toc_headings:
        return split_into_sections(text)

    # Build regex pattern from TOC headings
    escaped_headings = [re.escape(h) for h in toc_headings]
    toc_pattern = re.compile(
        r"^(\d+(?:\.\d+)*\.?)?\s*(" + "|".join(escaped_headings) + r")\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

    lines = text.split("\n")
    current: dict[str, Any] = {"heading": "Body", "text": []}

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        match = toc_pattern.match(line_stripped)
        if match:
            # Save current section
            if current["text"]:
                current["text"] = " ".join(current["text"]).strip()
                sections.append(current)

            # Start new section
            heading = match.group(2).strip()
            current = {"heading": heading, "text": []}
        else:
            cast(list[str], current["text"]).append(line_stripped)

    # Save final section
    if current["text"]:
        current["text"] = " ".join(current["text"]).strip()
        sections.append(current)

    return sections if sections else split_into_sections(text)


def split_into_sections(text: str) -> list[dict[str, Any]]:
    """Split text into sections based on detected headings.

    Args:
        text: Input text to split into sections.

    Returns:
        List of dictionaries with 'heading' and 'text' keys.
    """
    lines = [line.strip() for line in text.split("\n")]
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] = {"heading": "Body", "text": []}
    in_references = False
    seen_headings = set()

    for line in lines:
        if not line:
            continue

        heading = is_section_heading(line)

        # Stop detecting new sections after References/Bibliography
        if heading and heading.lower() in ["references", "bibliography"]:
            in_references = True
            # Save current section
            if current["text"]:
                current["text"] = " ".join(current["text"]).strip()
                sections.append(current)
            current = {"heading": heading, "text": []}
        elif heading and not in_references:
            # Skip duplicate section headings (except for common ones that might legitimately appear multiple times)
            heading_lower = heading.lower()
            if heading_lower in seen_headings and heading_lower not in ["methods", "abstract"]:
                cast(list[str], current["text"]).append(line)
                continue

            seen_headings.add(heading_lower)

            # Save current section
            if current["text"]:
                current["text"] = " ".join(current["text"]).strip()
                sections.append(current)

            # Start new section
            current = {"heading": heading, "text": []}
        else:
            cast(list[str], current["text"]).append(line)

    # Save final section
    if current["text"]:
        current["text"] = " ".join(current["text"]).strip()
        sections.append(current)

    return sections if sections else [{"heading": "Body", "text": text}]


def semantic_chunk_sections(
    sections: list[dict[str, Any]], min_sent: int = 3, max_sent: int = 8
) -> list[dict[str, Any]]:
    """Chunk sections into smaller pieces based on sentence count.

    Args:
        sections: List of sections with 'heading' and 'text' keys.
        min_sent: Minimum sentences per chunk.
        max_sent: Maximum sentences per chunk.

    Returns:
        List of chunks with 'heading' and 'text' keys.
    """
    chunks: list[dict[str, Any]] = []

    for sec in sections:
        sents = sentence_split(sec["text"])
        buffer: list[str] = []

        for sent in sents:
            buffer.append(sent)

            if len(buffer) >= max_sent:
                chunks.append({"heading": sec["heading"], "text": " ".join(buffer)})
                buffer = []

        # Handle remaining sentences
        if buffer:
            if len(buffer) < min_sent and chunks:
                # Merge with previous chunk if too small
                chunks[-1]["text"] += " " + " ".join(buffer)
            else:
                chunks.append({"heading": sec["heading"], "text": " ".join(buffer)})

    return chunks
