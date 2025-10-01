#!/usr/bin/env python3
"""Standalone script to validate scipreprocess output JSON files."""

import sys
from pathlib import Path

# Add tests directory to path
sys.path.insert(0, str(Path(__file__).parent))

from validate_output import OutputValidator, validate_output


def create_sample_output():
    """Create a sample valid output for testing."""
    return {
        "metadata": {
            "title": "Sample Scientific Paper on Machine Learning",
            "source_file": "examples/test_files/sample.pdf",
            "pages": 12,
        },
        "abstract": (
            "This paper presents a novel approach to machine learning that combines "
            "deep learning with symbolic reasoning. We demonstrate significant "
            "improvements over baseline methods on multiple benchmark datasets."
        ),
        "sections": [
            {"heading": "Introduction", "text": "Machine learning has revolutionized..."},
            {"heading": "Related Work", "text": "Previous research in this area..."},
            {"heading": "Methods", "text": "Our approach consists of three main components..."},
            {"heading": "Results", "text": "We evaluated our method on five datasets..."},
            {"heading": "Discussion", "text": "The results demonstrate that..."},
            {"heading": "Conclusion", "text": "In this work, we presented..."},
            {"heading": "References", "text": "Complete references section..."},
        ],
        "figures": [
            {
                "type": "figure",
                "number": "1",
                "caption": "Figure 1: Architecture overview of our proposed system.",
                "page": 3,
            },
            {
                "type": "figure",
                "number": "2",
                "caption": "Figure 2: Comparison of accuracy across different methods.",
                "page": 7,
            },
        ],
        "tables": [
            {
                "type": "table",
                "number": "1",
                "caption": "Table 1: Dataset statistics and characteristics.",
                "page": 5,
            },
            {
                "type": "table",
                "number": "2",
                "caption": "Table 2: Performance comparison on benchmark datasets.",
                "page": 8,
            },
        ],
        "equations": [
            {"type": "equation", "number": "1", "page": 4},
            {"type": "equation", "number": "2", "page": 6},
        ],
        "references": [
            {
                "number": "1",
                "text": "Smith, J. et al. (2022). Deep Learning Methods. Journal of AI Research, 45(2), 123-145.",
            },
            {
                "number": "2",
                "text": "Johnson, A. and Brown, B. (2021). Symbolic Reasoning in ML. Proceedings of ICML.",
            },
            {
                "number": "3",
                "text": "Williams, C. (2023). Neural Networks: A Comprehensive Guide. MIT Press.",
            },
        ],
        "acronyms": {
            "ML": "Machine Learning",
            "DL": "Deep Learning",
            "NLP": "Natural Language Processing",
            "CNN": "Convolutional Neural Network",
            "RNN": "Recurrent Neural Network",
        },
    }


def main():
    """Main entry point for validation script."""
    print("=" * 70)
    print("SciPreprocess Output Validator")
    print("=" * 70)

    if len(sys.argv) > 1:
        # Validate file provided as argument
        file_path = sys.argv[1]
        print(f"\nValidating file: {file_path}")
        print("-" * 70)

        if not Path(file_path).exists():
            print(f"❌ Error: File not found: {file_path}")
            sys.exit(1)

        try:
            result = validate_output(file_path, strict=False, verbose=False)

            validator = OutputValidator(strict=False)
            validator.validate(file_path)
            print(validator.get_report())

            sys.exit(0 if result else 1)

        except Exception as e:
            print(f"❌ Error during validation: {e}")
            sys.exit(1)
    else:
        # Demo mode - validate sample data
        print("\nNo file provided. Running validation demo with sample data...")
        print("-" * 70)

        # Test with valid data
        print("\n1️⃣  Testing with VALID sample data:")
        print("=" * 70)
        sample_data = create_sample_output()

        validator = OutputValidator(strict=False)
        validator.validate(sample_data)
        print(validator.get_report())

        # Test with invalid data
        print("\n2️⃣  Testing with INVALID sample data:")
        print("=" * 70)
        invalid_data = {
            "metadata": {
                "title": "",  # Empty title
                # Missing source_file
                "pages": -5,  # Invalid page count
            },
            "abstract": "",  # Empty abstract
            "sections": [
                {"heading": "Intro"},  # Missing text
                {"text": "Some text"},  # Missing heading
            ],
            "figures": [{"type": "figure", "number": "1", "caption": "Test"}],  # Missing page
            "tables": [],
            "equations": [],
            "references": [{"number": "1"}],  # Missing text
            "acronyms": {"ML": ""},  # Empty expansion
        }

        validator2 = OutputValidator(strict=False)
        validator2.validate(invalid_data)
        print(validator2.get_report())

        print("\n" + "=" * 70)
        print("Usage: python run_validation.py <path_to_json_file>")
        print("=" * 70)


if __name__ == "__main__":
    main()
