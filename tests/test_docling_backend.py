from __future__ import annotations

import pathlib

import pytest

from scipreprocess.config import PipelineConfig
from scipreprocess.pipeline import PreprocessingPipeline


@pytest.mark.parametrize("backend", ["auto", "docling", "local"])
def test_backend_provenance(tmp_path: pathlib.Path, backend: str):
    # create tiny txt input to exercise pipeline without external deps
    p = tmp_path / "a.txt"
    p.write_text("Hello world\n", encoding="utf-8")

    cfg = PipelineConfig(parser_backend=backend)
    pipe = PreprocessingPipeline(cfg)
    out = pipe.preprocess_documents([str(p)])

    assert "documents" in out and out["documents"], "must produce at least one document"
    doc = out["documents"][0]
    prov = doc.get("provenance", {})
    assert prov.get("pipeline") == "local"
    assert prov.get("backend") in {"local", "docling"}


def test_cli_hardening_empty(tmp_path: pathlib.Path, capsys):
    import sys

    from scipreprocess.cli import main

    sys.argv = ["scipreprocess", "--backend", "auto", "nonexistent.file"]
    rc = main()
    assert rc == 2
    captured = capsys.readouterr()
    assert "no valid inputs" in captured.err


def test_toc_sections_are_filtered(tmp_path: pathlib.Path):
    # Create a text that includes a TOC-like section and other index sections
    content = (
        "Title\n"
        "Table of Contents\n"
        "1 Introduction 1\n2 Methods 3\n3 Results 5\n"
        "Introduction\nThis is the intro.\n"
        "List of Figures\n1 System Overview 2\n"
        "Methods\nMethod details here.\n"
        "Glossary\nTerm: Definition\n"
        "Results\nFindings here.\n"
    )
    p = tmp_path / "with_toc.txt"
    p.write_text(content, encoding="utf-8")

    cfg = PipelineConfig(parser_backend="local")
    pipe = PreprocessingPipeline(cfg)
    out = pipe.preprocess_documents([str(p)])
    doc = out["documents"][0]

    # Ensure sections do not contain TOC/index sections
    headings = [s.get("heading", "").lower() for s in doc.get("sections", [])]
    banned = {
        "table of contents",
        "contents",
        "toc",
        "list of figures",
        "list of tables",
        "list of algorithms",
        "list of abbreviations",
        "list of symbols",
        "glossary",
    }
    assert not any(h in banned for h in headings)

    # If parsed, toc_structured may exist either from index extraction or metadata
    # Not strictly required, but ensure pipeline remains stable
    assert "sections" in doc and isinstance(doc["sections"], list)
