"""Basic tests for the preprocessing pipeline."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

import scipreprocess.pipeline as pipeline

from scipreprocess.acronyms import detect_acronyms, expand_acronyms
from scipreprocess.config import PipelineConfig
from scipreprocess.models import ParsedDocument
from scipreprocess.pipeline import PreprocessingPipeline
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


def test_pipeline_figures_summary():
    """Ensure figure summaries are generated and bounded."""

    pipeline = PreprocessingPipeline(PipelineConfig(use_spacy=False))
    parsed = ParsedDocument(
        source_path="dummy.pdf",
        is_scanned=False,
        text_pages=[""],
        images=[],
        metadata={
            "figures": [
                {
                    "type": "figure",
                    "number": "1",
                    "caption": (
                        "Figure 1 illustrates the proposed architecture with three major modules. "
                        "The framework improves classification accuracy by combining contextual cues."
                    ),
                }
            ]
        },
    )

    doc_json = pipeline._assemble_document_json(parsed, "", [], {})
    figures = doc_json["figures"]
    assert figures, "Figures should be preserved in the JSON payload"
    summary = figures[0].get("summary", "")
    assert summary, "Summaries must not be empty"
    assert len(summary.split()) <= 60, "Summaries should be length constrained"


def test_pipeline_preserves_structured_index(monkeypatch):
    """Structured TOC/index entries should surface in the final payload."""

    config = PipelineConfig(use_spacy=False)
    pipe = PreprocessingPipeline(config)

    synthetic_toc = [
        {"id": "1", "parent_id": None, "name": "Introduction", "page": "1"},
        {"id": "1.1", "parent_id": "1", "name": "Background", "page": "2"},
    ]

    parsed = ParsedDocument(
        source_path="dummy.pdf",
        is_scanned=False,
        text_pages=[
            (
                "Table of Contents\n"
                "1 Introduction 1\n"
                "1.1 Background 2\n\n"
                "List of Figures\n"
                "1 System Overview 5\n\n"
                "Introduction\n"
                "Main body text."
            )
        ],
        images=[],
        metadata={"toc": synthetic_toc},
    )

    sections = [
        {
            "heading": "Table of Contents",
            "text": "1 Introduction 1\n1.1 Background 2\n",
        },
        {"heading": "List of Figures", "text": "1 System Overview 5\n"},
        {"heading": "Introduction", "text": "Main body text."},
    ]

    monkeypatch.setattr(
        pipeline,
        "ingest",
        lambda file_path, use_ocr, use_layout: parsed,
    )
    monkeypatch.setattr(
        pipeline,
        "split_into_sections_with_toc",
        lambda full_text, toc: sections,
    )
    monkeypatch.setattr(pipeline, "split_into_sections", lambda full_text: sections)

    doc_json, _ = pipe.preprocess_file("dummy.pdf")

    metadata = doc_json["metadata"]
    assert metadata.get("toc") == synthetic_toc

    index_block = metadata.get("index", {})
    assert index_block, "Index metadata should be populated"
    toc_structured = index_block.get("toc_structured", [])
    assert toc_structured and toc_structured[0]["name"] == "Introduction"

    figures_list = index_block.get("list_of_figures", [])
    assert figures_list and figures_list[0]["title"] == "System Overview"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
