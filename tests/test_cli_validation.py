"""Integration tests for CLI validation hooks."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

from scipreprocess.config import PipelineConfig
from scipreprocess.pipeline import PreprocessingPipeline
from scipreprocess.validate_output import OutputValidator


def test_pipeline_output_passes_validator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ensure pipeline outputs satisfy the OutputValidator contract."""

    sample_text = """\
Abstract
This abstract is intentionally long enough to satisfy validation rules by providing ample descriptive content.

Introduction
This introduction supplies background context so the validator perceives a realistic document structure with meaningful prose.

Methods
The methods section details steps, materials, and procedures with thorough explanations and technical wording to mirror scientific writing.

Results
Results summarise observations, reinforce hypotheses, and include supporting interpretation so downstream validation has material to inspect.

References
[1] Example Reference Entry illustrating properly formatted citations.
"""

    sample_path = tmp_path / "sample.txt"
    sample_path.write_text(sample_text, encoding="utf-8")

    monkeypatch.setattr("scipreprocess.pipeline.ensure_nltk_resources", lambda: None)

    pipeline = PreprocessingPipeline(PipelineConfig(use_spacy=False))
    result = pipeline.preprocess_documents([str(sample_path)])

    documents = result.get("documents", [])
    assert documents, "Pipeline should produce at least one document payload"

    validator = OutputValidator(strict=True)
    for doc in documents:
        assert validator.validate(doc) is True

