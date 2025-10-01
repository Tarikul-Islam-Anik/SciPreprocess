"""Tests for output validation."""

import json

import pytest
from validate_output import OutputValidator, ValidationError, validate_output


class TestOutputValidator:
    """Test suite for OutputValidator."""

    def test_valid_output(self):
        """Test validation of valid output."""
        valid_data = {
            "metadata": {"title": "Test Paper", "source_file": "test.pdf", "pages": 10},
            "abstract": "This is a test abstract with sufficient length.",
            "sections": [
                {"heading": "Introduction", "text": "Introduction text here."},
                {"heading": "Methods", "text": "Methods text here."},
            ],
            "figures": [{"type": "figure", "number": "1", "caption": "Test figure", "page": 1}],
            "tables": [{"type": "table", "number": "1", "caption": "Test table", "page": 2}],
            "equations": [{"type": "equation", "number": "1", "page": 3}],
            "references": [{"number": "1", "text": "Author et al. (2023). Paper title."}],
            "acronyms": {"NLP": "Natural Language Processing", "ML": "Machine Learning"},
        }

        validator = OutputValidator(strict=True)
        assert validator.validate(valid_data) is True
        assert len(validator.errors) == 0

    def test_missing_required_keys(self):
        """Test detection of missing required keys."""
        invalid_data = {
            "metadata": {"title": "Test", "source_file": "test.pdf"},
            # Missing other required keys
        }

        validator = OutputValidator(strict=False)
        result = validator.validate(invalid_data)

        assert result is False
        assert len(validator.errors) > 0
        assert any("Missing required top-level key" in e for e in validator.errors)

    def test_invalid_metadata(self):
        """Test validation of invalid metadata."""
        invalid_data = {
            "metadata": {
                "title": "",  # Empty title
                # Missing source_file
                "pages": -5,  # Invalid page count
            },
            "abstract": "",
            "sections": [],
            "figures": [],
            "tables": [],
            "equations": [],
            "references": [],
            "acronyms": {},
        }

        validator = OutputValidator(strict=False)
        result = validator.validate(invalid_data)

        assert result is False
        assert any("Missing required metadata field" in e for e in validator.errors)

    def test_invalid_sections(self):
        """Test validation of invalid sections."""
        invalid_data = {
            "metadata": {"title": "Test", "source_file": "test.pdf"},
            "abstract": "Test abstract",
            "sections": [
                {"heading": "Intro"},  # Missing text field
                {"text": "Some text"},  # Missing heading field
                {"heading": "", "text": ""},  # Empty fields
            ],
            "figures": [],
            "tables": [],
            "equations": [],
            "references": [],
            "acronyms": {},
        }

        validator = OutputValidator(strict=False)
        result = validator.validate(invalid_data)

        assert result is False
        assert any("missing" in e.lower() for e in validator.errors)

    def test_invalid_figures(self):
        """Test validation of invalid figures."""
        invalid_data = {
            "metadata": {"title": "Test", "source_file": "test.pdf"},
            "abstract": "Test",
            "sections": [],
            "figures": [
                {"type": "figure", "number": "1", "caption": "Test"},  # Missing page
                {"type": "figure", "number": "1", "caption": "Test", "page": -1},  # Invalid page
            ],
            "tables": [],
            "equations": [],
            "references": [],
            "acronyms": {},
        }

        validator = OutputValidator(strict=False)
        result = validator.validate(invalid_data)

        assert result is False
        assert any("figures" in e for e in validator.errors)

    def test_duplicate_warnings(self):
        """Test detection of duplicate numbers."""
        data_with_duplicates = {
            "metadata": {"title": "Test", "source_file": "test.pdf"},
            "abstract": "Test abstract",
            "sections": [
                {"heading": "Intro", "text": "Text"},
                {"heading": "Intro", "text": "Text"},  # Duplicate heading
            ],
            "figures": [
                {"type": "figure", "number": "1", "caption": "Fig 1", "page": 1},
                {"type": "figure", "number": "1", "caption": "Fig 1 again", "page": 2},
            ],
            "tables": [],
            "equations": [],
            "references": [],
            "acronyms": {},
        }

        validator = OutputValidator(strict=False)
        validator.validate(data_with_duplicates)

        # Should pass but with warnings
        assert len(validator.warnings) > 0
        assert any("Duplicate" in w for w in validator.warnings)

    def test_validate_from_file(self, tmp_path):
        """Test validation from JSON file."""
        valid_data = {
            "metadata": {"title": "Test", "source_file": "test.pdf"},
            "abstract": "Test abstract",
            "sections": [{"heading": "Intro", "text": "Text"}],
            "figures": [],
            "tables": [],
            "equations": [],
            "references": [],
            "acronyms": {},
        }

        json_file = tmp_path / "test.json"
        with open(json_file, "w") as f:
            json.dump(valid_data, f)

        validator = OutputValidator(strict=True)
        assert validator.validate(json_file) is True

    def test_strict_mode_raises_exception(self):
        """Test that strict mode raises ValidationError."""
        invalid_data = {
            "metadata": {},  # Missing required fields
            "abstract": "",
            "sections": [],
            "figures": [],
            "tables": [],
            "equations": [],
            "references": [],
            "acronyms": {},
        }

        validator = OutputValidator(strict=True)

        with pytest.raises(ValidationError):
            validator.validate(invalid_data)

    def test_convenience_function(self):
        """Test the convenience validate_output function."""
        valid_data = {
            "metadata": {"title": "Test", "source_file": "test.pdf"},
            "abstract": "Test abstract",
            "sections": [{"heading": "Intro", "text": "Text"}],
            "figures": [],
            "tables": [],
            "equations": [],
            "references": [],
            "acronyms": {},
        }

        result = validate_output(valid_data, strict=True, verbose=False)
        assert result is True

    def test_get_report(self):
        """Test report generation."""
        valid_data = {
            "metadata": {"title": "Test", "source_file": "test.pdf"},
            "abstract": "Test abstract",
            "sections": [{"heading": "Intro", "text": "Text"}],
            "figures": [],
            "tables": [],
            "equations": [],
            "references": [],
            "acronyms": {},
        }

        validator = OutputValidator(strict=False)
        validator.validate(valid_data)
        report = validator.get_report()

        assert "VALIDATION REPORT" in report
        assert "✅" in report or "❌" in report or "⚠️" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
