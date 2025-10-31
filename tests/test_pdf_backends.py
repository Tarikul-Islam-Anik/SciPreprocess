from __future__ import annotations

import pathlib

import pytest

from scipreprocess.config import PipelineConfig
from scipreprocess.parsers import extract_text_from_pdf
from scipreprocess.pipeline import PreprocessingPipeline


@pytest.fixture()
def sample_pdf(tmp_path: pathlib.Path) -> pathlib.Path:
    fitz = pytest.importorskip("fitz", reason="PyMuPDF required for PDF backend tests")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (72, 72),
        (
            "Figure 1 Example caption\n"
            "Table 1 Example caption\n"
            "Equation (1) shows something important.\n"
            "References\n"
            "[1] Example reference entry about science.\n"
        ),
    )
    path = tmp_path / "backend.pdf"
    doc.save(path)
    doc.close()
    return path


def test_rust_backend_matches_python(sample_pdf: pathlib.Path):
    pdf_ingest = pytest.importorskip(
        "rust_extensions.pdf_ingest", reason="Rust backend not built"
    )
    if not pdf_ingest.is_available():
        pytest.skip("Rust backend Python bindings available but extension missing")

    local = extract_text_from_pdf(str(sample_pdf), backend="local")
    rust = extract_text_from_pdf(str(sample_pdf), backend="rust")

    assert local.text_pages == rust.text_pages
    assert local.metadata["figures"] == rust.metadata["figures"]
    assert local.metadata["tables"] == rust.metadata["tables"]
    assert local.metadata["equations"] == rust.metadata["equations"]
    assert local.metadata["references"] == rust.metadata["references"]

    pipe_local = PreprocessingPipeline(
        PipelineConfig(use_spacy=False, parser_backend="local")
    )
    pipe_rust = PreprocessingPipeline(
        PipelineConfig(use_spacy=False, parser_backend="rust")
    )

    local_json, _ = pipe_local.preprocess_file(str(sample_pdf))
    rust_json, _ = pipe_rust.preprocess_file(str(sample_pdf))

    assert local_json == rust_json
