"""Basic usage examples for the scipreprocess pipeline."""

import json
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scipreprocess import PipelineConfig, preprocess_documents, preprocess_file
from scipreprocess.pipeline import PreprocessingPipeline


def example_single_file():
    """Example: Process a single document."""
    print("=" * 60)
    print("Example 1: Processing a single document")
    print("=" * 60)

    # Define paths
    input_file = "examples/test_files/test.pdf"
    output_file = "examples/output/test.json"

    # Process a single file
    doc_json, clean_text = preprocess_file(input_file)

    # Save the doc_json to a json file
    with open(output_file, "w") as f:
        json.dump(doc_json, f, indent=2)

    print(f"\n✓ Saved output to: {output_file}")

    # Print results
    print(f"\nTitle: {doc_json['metadata']['title']}")
    print(f"Source: {doc_json['metadata']['source_file']}")
    print(f"Pages: {doc_json['metadata'].get('pages', 'N/A')}")
    print(f"\nAbstract:\n{doc_json['abstract'][:200]}...")
    print(f"\nSections: {[s['heading'] for s in doc_json['sections']]}")
    print(f"\nFigures: {len(doc_json.get('figures', []))}")
    print(f"Tables: {len(doc_json.get('tables', []))}")
    print(f"Equations: {len(doc_json.get('equations', []))}")
    print(f"References: {len(doc_json.get('references', []))}")
    print(f"\nAcronyms: {doc_json['acronyms']}")
    print(f"\nClean text length: {len(clean_text)} characters")


def example_multiple_files():
    """Example: Process multiple documents with TF-IDF."""
    print("\n" + "=" * 60)
    print("Example 2: Processing multiple documents")
    print("=" * 60)

    # Process multiple files from test_files directory
    files = [
        "examples/test_files/paper1.pdf",
        "examples/test_files/paper2.docx",
        "examples/test_files/paper3.tex",
    ]
    results = preprocess_documents(files)

    # Access results
    print(f"\nProcessed {len(results['documents'])} documents")

    for i, doc in enumerate(results["documents"]):
        if "error" in doc:
            print(f"\n{i+1}. ERROR: {doc['metadata']['title']}")
            print(f"   {doc['error']}")
        else:
            print(f"\n{i+1}. {doc['metadata']['title']}")
            print(f"   Sections: {len(doc['sections'])}")
            print(f"   Acronyms: {len(doc['acronyms'])}")

    # TF-IDF features
    if results["tfidf"]["X"] is not None:
        print(f"\nTF-IDF matrix shape: {results['tfidf']['X'].shape}")
        print(f"Vocabulary size: {len(results['tfidf']['vectorizer'].vocabulary_)}")

    # Chunks
    total_chunks = sum(len(chunks) for chunks in results["chunks"])
    print(f"\nTotal chunks: {total_chunks}")


def example_custom_config():
    """Example: Use custom configuration."""
    print("\n" + "=" * 60)
    print("Example 3: Custom configuration")
    print("=" * 60)

    # Create custom configuration
    config = PipelineConfig(
        use_ocr=True,  # Enable OCR for scanned documents
        use_spacy=True,  # Use spaCy for NLP
        use_semantic_embeddings=True,  # Generate embeddings
        spacy_model="en_core_sci_sm",  # Use scientific spaCy model
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        chunk_target_sentences=(5, 10),  # Larger chunks
    )

    # Create pipeline with custom config
    pipeline = PreprocessingPipeline(config)

    # Process documents from test_files directory
    results = pipeline.preprocess_documents(
        ["examples/test_files/paper1.pdf", "examples/test_files/paper2.pdf"]
    )

    print(f"\nProcessed {len(results['documents'])} documents with custom config")

    if results["embeddings"] is not None:
        print(f"Embeddings shape: {results['embeddings'].shape}")
        print(f"Embedding dimension: {results['embeddings'].shape[1]}")

    if results["index"] is not None:
        print(f"FAISS index created with {results['index'].ntotal} vectors")


def example_just_parsing():
    """Example: Use individual components."""
    print("\n" + "=" * 60)
    print("Example 4: Using individual components")
    print("=" * 60)

    from scipreprocess.acronyms import detect_acronyms, expand_acronyms
    from scipreprocess.parsers import ingest
    from scipreprocess.preprocessing import clean_text

    # Just parse a document
    input_file = "examples/test_files/test.pdf"
    parsed = ingest(input_file)
    print(f"\nParsed: {parsed.source_path}")
    print(f"Scanned: {parsed.is_scanned}")
    print(f"Pages: {len(parsed.text_pages)}")

    # Clean the text
    full_text = "\n".join(parsed.text_pages)
    cleaned = clean_text(full_text)
    print(f"\nCleaned text length: {len(cleaned)} characters")

    # Detect acronyms
    acronyms = detect_acronyms(cleaned)
    print(f"\nFound acronyms: {acronyms}")

    # Expand acronyms
    expanded = expand_acronyms(cleaned, acronyms)
    print(f"Expanded text length: {len(expanded)} characters")


def example_validate_output():
    """Example: Validate output JSON."""
    print("\n" + "=" * 60)
    print("Example 5: Validating output JSON")
    print("=" * 60)

    # Import validation module from tests
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))

    try:
        from validate_output import OutputValidator

        # Validate the test.json output
        output_file = "examples/output/test.json"

        if not Path(output_file).exists():
            print(f"\n⚠️  Output file not found: {output_file}")
            print("Run example_single_file() first to generate output.")
            return

        print(f"\nValidating: {output_file}")
        print("-" * 60)

        # Validate with strict mode off to see all issues
        validator = OutputValidator(strict=False)
        result = validator.validate(output_file)

        # Print detailed report
        print(validator.get_report())

        # Show summary
        if result:
            print("\n✅ Validation successful! Output JSON is well-formed.")
        else:
            print(f"\n❌ Validation failed with {len(validator.errors)} error(s).")

        # Example: Validate an invalid structure
        print("\n" + "-" * 60)
        print("Testing with invalid data:")
        print("-" * 60)

        invalid_data = {
            "metadata": {"title": "", "source_file": ""},  # Empty fields
            "abstract": "",
            "sections": [],
            "figures": [{"type": "figure", "number": "1", "caption": "Test"}],  # Missing page
            "tables": [],
            "equations": [],
            "references": [],
            "acronyms": {},
        }

        validator2 = OutputValidator(strict=False)
        validator2.validate(invalid_data)
        print(validator2.get_report())

    except ImportError as e:
        print(f"\n❌ Could not import validation module: {e}")
        print("Make sure validate_output.py exists in the tests/ directory.")


def main():
    """Run all examples."""
    print("SciPreprocess - Usage Examples")
    print("=" * 60)

    # Uncomment the examples you want to run
    example_single_file()
    # example_multiple_files()
    # example_custom_config()
    # example_just_parsing()
    example_validate_output()

    print("\n" + "=" * 60)
    # print("Note: Uncomment examples in main() to run them")
    # print("=" * 60)


if __name__ == "__main__":
    main()
