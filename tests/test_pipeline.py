"""Basic tests for the preprocessing pipeline."""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scipreprocess.acronyms import detect_acronyms, expand_acronyms
from scipreprocess.config import PipelineConfig
from scipreprocess.preprocessing import clean_text, tokenize
from scipreprocess.sectioning import split_into_sections


def test_config_defaults():
    """Test default configuration."""
    config = PipelineConfig()
    assert config.use_spacy is True
    assert config.use_ocr is False
    assert config.chunk_target_sentences == (3, 8)


def test_clean_text():
    """Test text cleaning."""
    text = "This is a test [1] with citations (Smith et al., 2020) and unicode: café"
    cleaned = clean_text(text)

    assert "[1]" not in cleaned
    assert "Smith et al." not in cleaned
    assert "cafe" in cleaned or "caf" in cleaned


def test_tokenize():
    """Test tokenization."""
    text = "This is a test sentence."
    tokens = tokenize(text)

    assert len(tokens) > 0
    assert "test" in tokens
    assert "sentence" in tokens


def test_detect_acronyms():
    """Test acronym detection."""
    text = "Natural Language Processing (NLP) is important. Machine Learning (ML) too."
    acronyms = detect_acronyms(text)

    assert "NLP" in acronyms
    assert "ML" in acronyms
    assert "Natural Language Processing" in acronyms.values()


def test_expand_acronyms():
    """Test acronym expansion."""
    text = "NLP is useful. ML is powerful."
    mapping = {"NLP": "Natural Language Processing", "ML": "Machine Learning"}
    expanded = expand_acronyms(text, mapping)

    assert "Natural Language Processing" in expanded
    assert "Machine Learning" in expanded


def test_split_into_sections():
    """Test section splitting."""
    text = """
    Abstract
    This is the abstract.

    Introduction
    This is the introduction.

    Methods
    This is the methods section.
    """

    sections = split_into_sections(text)

    assert len(sections) > 0
    headings = [s["heading"] for s in sections]
    assert "Abstract" in headings
    assert "Introduction" in headings
    assert "Methods" in headings


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
