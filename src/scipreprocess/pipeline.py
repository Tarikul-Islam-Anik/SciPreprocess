"""Main preprocessing pipeline orchestration."""

from __future__ import annotations

import pathlib
from typing import Any

from .acronyms import detect_acronyms, expand_acronyms
from .config import PipelineConfig
from .features import maybe_build_embeddings, tfidf_features
from .local_extract import extract_header_blocks, extract_index_sections
from .models import ParsedDocument
from .parsers import ingest
from .preprocessing import clean_text, ocr_image_to_text
from .sectioning import (
    semantic_chunk_sections,
    split_into_sections,
    split_into_sections_with_toc,
)
from .utils import ensure_nltk_resources, load_spacy_model, print_availability_status


class PreprocessingPipeline:
    """Main preprocessing pipeline for scientific documents."""

    def __init__(self, config: PipelineConfig | None = None):
        """Initialize the pipeline with configuration.

        Args:
            config: Pipeline configuration. Uses defaults if not provided.
        """
        self.config = config or PipelineConfig()

        # Initialize NLP resources
        ensure_nltk_resources()

        self.nlp_model = None
        if self.config.use_spacy:
            self.nlp_model = load_spacy_model(self.config.spacy_model)

        # Print dependency status
        print_availability_status(self.nlp_model)

    def _ensure_text_for_scanned(self, parsed: ParsedDocument) -> ParsedDocument:
        """Apply OCR to scanned pages if needed.

        Args:
            parsed: Parsed document potentially with scanned pages.

        Returns:
            ParsedDocument with OCR text if needed.
        """
        if not parsed.is_scanned or not self.config.use_ocr:
            return parsed

        text_pages: list[str] = []

        for idx, page_text in enumerate(parsed.text_pages):
            if page_text.strip():
                text_pages.append(page_text)
                continue

            # Apply OCR to empty pages
            img = parsed.images[idx] if idx < len(parsed.images) else None
            page_txt = ocr_image_to_text(img)
            text_pages.append(page_txt)

        return ParsedDocument(
            source_path=parsed.source_path,
            is_scanned=True,
            text_pages=text_pages,
            images=parsed.images,
            metadata=parsed.metadata,
        )

    def _assemble_document_json(
        self,
        parsed: ParsedDocument,
        full_text: str,
        sections: list[dict[str, Any]],
        acronyms: dict[str, str],
    ) -> dict[str, Any]:
        """Assemble final document JSON structure.

        Args:
            parsed: Original parsed document.
            full_text: Full cleaned text.
            sections: Detected sections.
            acronyms: Detected acronyms.

        Returns:
            Dictionary with document metadata and content.
        """
        # Extract title from metadata or first section
        title = parsed.metadata.get("title")
        if not title and sections:
            title = sections[0]["text"][:120]
        if not title:
            title = pathlib.Path(parsed.source_path).stem

        # Extract abstract
        abstract = next((s["text"] for s in sections if s["heading"].lower() == "abstract"), "")

        return {
            "metadata": {
                "title": title,
                "source_file": parsed.source_path,
                "pages": parsed.metadata.get("pages", None),
                # Surface extracted authors if available
                "authors": parsed.metadata.get("authors", []),
            },
            "abstract": abstract,
            "sections": sections,
            "figures": parsed.metadata.get("figures", []),
            "tables": parsed.metadata.get("tables", []),
            "equations": parsed.metadata.get("equations", []),
            "references": parsed.metadata.get("references", []),
            "acronyms": acronyms,
            # Minimal provenance for tests
            "provenance": {
                "pipeline": "local",
                "backend": (
                    self.config.parser_backend
                    if self.config.parser_backend in {"local", "docling"}
                    else "local"
                ),
            },
        }

    def preprocess_file(self, file_path: str, lower: bool = False) -> tuple[dict[str, Any], str]:
        """Preprocess a single scientific document.

        Args:
            file_path: Path to the document file.
            lower: Whether to convert text to lowercase.

        Returns:
            Tuple of (document JSON, full cleaned text).
        """
        # Ingest document
        parsed = ingest(file_path, self.config.use_ocr, self.config.use_layout)

        # Apply OCR if needed
        parsed = self._ensure_text_for_scanned(parsed)

        # Combine all pages
        full_text = "\n".join(parsed.text_pages)

        # Split into sections BEFORE cleaning (to preserve line structure)
        toc = parsed.metadata.get("toc", [])
        if toc:
            sections = split_into_sections_with_toc(full_text, toc)
        else:
            sections = split_into_sections(full_text)

        # Remove TOC/index-like sections while preserving metadata if needed
        index_info, consumed = extract_index_sections(sections, parsed.text_pages)
        if consumed:
            sections = [s for i, s in enumerate(sections) if i not in consumed]

        # Clean text in each section and detect acronyms
        cleaned_sections = []
        acr_map = {}
        for sec in sections:
            cleaned_text = clean_text(sec["text"], lower=lower)
            # Detect acronyms in this section
            sec_acr = detect_acronyms(cleaned_text, self.nlp_model)
            acr_map.update(sec_acr)
            # Expand acronyms
            expanded_text = expand_acronyms(cleaned_text, acr_map)
            cleaned_sections.append({"heading": sec["heading"], "text": expanded_text})

        sections = cleaned_sections
        # Get expanded full text for return value
        expanded = " ".join(sec["text"] for sec in sections)

        # Heuristically extract header info (title/authors) and merge into metadata
        header = extract_header_blocks(parsed.text_pages)
        if header:
            merged_md = dict(parsed.metadata)
            # Only override title if not already set by parser
            if header.get("title") and not merged_md.get("title"):
                merged_md["title"] = header["title"]
            if header.get("authors"):
                merged_md["authors"] = header["authors"]
            parsed = ParsedDocument(
                source_path=parsed.source_path,
                is_scanned=parsed.is_scanned,
                text_pages=parsed.text_pages,
                images=parsed.images,
                metadata=merged_md,
            )

        # Assemble final JSON
        doc_json = self._assemble_document_json(parsed, expanded, sections, acr_map)

        # Return JSON and combined section text
        section_text = " ".join(sec["text"] for sec in sections)

        return doc_json, section_text

    def preprocess_documents(self, file_paths: list[str], lower: bool = False) -> dict[str, Any]:
        """Preprocess multiple scientific documents.

        Args:
            file_paths: List of paths to document files.
            lower: Whether to convert text to lowercase.

        Returns:
            Dictionary containing:
                - documents: List of document JSONs
                - tfidf: TF-IDF features and vectorizer
                - chunks: List of chunked sections per document
                - embeddings: Semantic embeddings (if enabled)
                - index: FAISS index (if enabled)
        """
        docs_json: list[dict[str, Any]] = []
        corpus: list[str] = []

        # Process each document
        for fp in file_paths:
            try:
                doc_json, doc_text = self.preprocess_file(fp, lower=lower)
                docs_json.append(doc_json)
                corpus.append(doc_text)
            except Exception as e:
                # Store error for failed documents
                docs_json.append(
                    {
                        "metadata": {"title": pathlib.Path(fp).stem, "source_file": fp},
                        "error": str(e),
                    }
                )

        # Extract TF-IDF features
        tfidf_matrix, vectorizer = tfidf_features(corpus)

        # Chunk sections
        all_chunks: list[list[dict[str, Any]]] = []
        for j in docs_json:
            secs = j.get("sections", [])
            chunks = semantic_chunk_sections(secs, *self.config.chunk_target_sentences)
            all_chunks.append(chunks)

        # Build embeddings if enabled
        embeddings, index = None, None
        if self.config.use_semantic_embeddings:
            flat_chunks = [c for chunk_list in all_chunks for c in chunk_list]
            embeddings, index = maybe_build_embeddings(flat_chunks, self.config.embedding_model)

        return {
            "documents": docs_json,
            "tfidf": {"X": tfidf_matrix, "vectorizer": vectorizer},
            "chunks": all_chunks,
            "embeddings": embeddings,
            "index": index,
        }


# Convenience functions for backward compatibility
_default_pipeline = None


def _get_default_pipeline() -> PreprocessingPipeline:
    """Get or create the default pipeline instance."""
    global _default_pipeline
    if _default_pipeline is None:
        _default_pipeline = PreprocessingPipeline()
    return _default_pipeline


def preprocess_file(file_path: str, lower: bool = False) -> tuple[dict[str, Any], str]:
    """Preprocess a single file using the default pipeline.

    Args:
        file_path: Path to the document file.
        lower: Whether to convert text to lowercase.

    Returns:
        Tuple of (document JSON, full cleaned text).
    """
    return _get_default_pipeline().preprocess_file(file_path, lower)


def preprocess_documents(file_paths: list[str], lower: bool = False) -> dict[str, Any]:
    """Preprocess multiple documents using the default pipeline.

    Args:
        file_paths: List of paths to document files.
        lower: Whether to convert text to lowercase.

    Returns:
        Dictionary with processed documents and features.
    """
    return _get_default_pipeline().preprocess_documents(file_paths, lower)
