"""Validation utilities for scipreprocess output JSON structure."""

import json
from pathlib import Path
from typing import Any


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


class OutputValidator:
    """Validator for scipreprocess output JSON."""

    def __init__(self, strict: bool = True):
        """Initialize validator.

        Args:
            strict: If True, raise exceptions on validation failures.
                   If False, collect and return validation warnings.
        """
        self.strict = strict
        self.warnings: list[str] = []
        self.errors: list[str] = []

    def validate(self, data: dict[str, Any] | str | Path) -> bool:
        """Validate output JSON structure and content.

        Args:
            data: Dictionary, JSON string, or path to JSON file.

        Returns:
            True if validation passes, False otherwise.

        Raises:
            ValidationError: If strict mode is enabled and validation fails.
        """
        # Load data if it's a file path or string
        if isinstance(data, (str, Path)):
            data = self._load_json(data)

        self.warnings = []
        self.errors = []

        try:
            # Validate top-level structure
            self._validate_top_level(data)

            # Validate metadata
            self._validate_metadata(data.get("metadata", {}))

            # Validate abstract
            self._validate_abstract(data.get("abstract", ""))

            # Validate sections
            self._validate_sections(data.get("sections", []))

            # Validate figures
            self._validate_figures(data.get("figures", []))

            # Validate tables
            self._validate_tables(data.get("tables", []))

            # Validate equations
            self._validate_equations(data.get("equations", []))

            # Validate references
            self._validate_references(data.get("references", []))

            # Validate acronyms
            self._validate_acronyms(data.get("acronyms", {}))

            # Report results
            if self.errors:
                error_msg = f"Validation failed with {len(self.errors)} error(s):\n" + "\n".join(
                    f"  - {e}" for e in self.errors
                )
                if self.strict:
                    raise ValidationError(error_msg)
                return False

            if self.warnings and not self.strict:
                print(f"Validation passed with {len(self.warnings)} warning(s):")
                for w in self.warnings:
                    print(f"  ⚠ {w}")

            return True

        except ValidationError:
            raise
        except Exception as e:
            error_msg = f"Unexpected validation error: {e}"
            if self.strict:
                raise ValidationError(error_msg)
            self.errors.append(error_msg)
            return False

    def _load_json(self, path: str | Path) -> dict[str, Any]:
        """Load JSON from file or parse JSON string."""
        path = Path(path) if not isinstance(path, Path) else path

        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        else:
            # Try parsing as JSON string
            try:
                return json.loads(str(path))
            except json.JSONDecodeError:
                raise ValidationError(f"Invalid JSON file or string: {path}")

    def _validate_top_level(self, data: dict[str, Any]):
        """Validate top-level structure."""
        required_keys = [
            "metadata",
            "abstract",
            "sections",
            "figures",
            "tables",
            "equations",
            "references",
            "acronyms",
        ]

        for key in required_keys:
            if key not in data:
                self.errors.append(f"Missing required top-level key: '{key}'")

        # Check for unexpected keys
        expected_keys = set(required_keys)
        actual_keys = set(data.keys())
        unexpected = actual_keys - expected_keys

        if unexpected:
            self.warnings.append(f"Unexpected top-level keys: {unexpected}")

    def _validate_metadata(self, metadata: dict[str, Any]):
        """Validate metadata structure."""
        if not isinstance(metadata, dict):
            self.errors.append(f"metadata must be a dict, got {type(metadata).__name__}")
            return

        # Required fields
        required = ["title", "source_file"]
        for key in required:
            if key not in metadata:
                self.errors.append(f"Missing required metadata field: '{key}'")
            elif not isinstance(metadata[key], str):
                self.errors.append(f"metadata.{key} must be a string")
            elif not metadata[key].strip():
                self.warnings.append(f"metadata.{key} is empty")

        # Optional fields with type checking
        if "pages" in metadata:
            if not isinstance(metadata["pages"], (int, type(None))):
                self.errors.append("metadata.pages must be an integer or null")
            elif isinstance(metadata["pages"], int) and metadata["pages"] <= 0:
                self.warnings.append(f"metadata.pages should be positive, got {metadata['pages']}")

    def _validate_abstract(self, abstract: str):
        """Validate abstract."""
        if not isinstance(abstract, str):
            self.errors.append(f"abstract must be a string, got {type(abstract).__name__}")
            return

        if not abstract.strip():
            self.warnings.append("abstract is empty")
        elif len(abstract) < 50:
            self.warnings.append(f"abstract seems very short ({len(abstract)} chars)")

    def _validate_sections(self, sections: list[dict[str, Any]]):
        """Validate sections structure."""
        if not isinstance(sections, list):
            self.errors.append(f"sections must be a list, got {type(sections).__name__}")
            return

        if not sections:
            self.warnings.append("sections list is empty")
            return

        seen_headings = set()
        for i, section in enumerate(sections):
            if not isinstance(section, dict):
                self.errors.append(f"sections[{i}] must be a dict")
                continue

            # Check required fields
            if "heading" not in section:
                self.errors.append(f"sections[{i}] missing 'heading' field")
            elif not isinstance(section["heading"], str):
                self.errors.append(f"sections[{i}].heading must be a string")
            elif not section["heading"].strip():
                self.errors.append(f"sections[{i}].heading is empty")
            else:
                heading = section["heading"]
                if heading in seen_headings and heading.lower() not in ["abstract", "methods"]:
                    self.warnings.append(f"Duplicate section heading: '{heading}'")
                seen_headings.add(heading)

            if "text" not in section:
                self.errors.append(f"sections[{i}] missing 'text' field")
            elif not isinstance(section["text"], str):
                self.errors.append(f"sections[{i}].text must be a string")
            elif not section["text"].strip():
                self.warnings.append(
                    f"sections[{i}] ('{section.get('heading', '?')}') has empty text"
                )

    def _validate_figures(self, figures: list[dict[str, Any]]):
        """Validate figures structure."""
        if not isinstance(figures, list):
            self.errors.append(f"figures must be a list, got {type(figures).__name__}")
            return

        seen_numbers = set()
        for i, figure in enumerate(figures):
            if not isinstance(figure, dict):
                self.errors.append(f"figures[{i}] must be a dict")
                continue

            # Check required fields
            required = ["type", "number", "caption", "page"]
            for key in required:
                if key not in figure:
                    self.errors.append(f"figures[{i}] missing '{key}' field")

            # Validate types
            if "type" in figure and figure["type"] != "figure":
                self.warnings.append(
                    f"figures[{i}].type should be 'figure', got '{figure['type']}'"
                )

            if "number" in figure:
                if not isinstance(figure["number"], str):
                    self.errors.append(f"figures[{i}].number must be a string")
                else:
                    if figure["number"] in seen_numbers:
                        self.warnings.append(f"Duplicate figure number: {figure['number']}")
                    seen_numbers.add(figure["number"])

            if "caption" in figure and not isinstance(figure["caption"], str):
                self.errors.append(f"figures[{i}].caption must be a string")

            if "page" in figure:
                if not isinstance(figure["page"], int):
                    self.errors.append(f"figures[{i}].page must be an integer")
                elif figure["page"] <= 0:
                    self.errors.append(f"figures[{i}].page must be positive")

    def _validate_tables(self, tables: list[dict[str, Any]]):
        """Validate tables structure."""
        if not isinstance(tables, list):
            self.errors.append(f"tables must be a list, got {type(tables).__name__}")
            return

        seen_numbers = set()
        for i, table in enumerate(tables):
            if not isinstance(table, dict):
                self.errors.append(f"tables[{i}] must be a dict")
                continue

            # Check required fields
            required = ["type", "number", "caption", "page"]
            for key in required:
                if key not in table:
                    self.errors.append(f"tables[{i}] missing '{key}' field")

            # Validate types
            if "type" in table and table["type"] != "table":
                self.warnings.append(f"tables[{i}].type should be 'table', got '{table['type']}'")

            if "number" in table:
                if not isinstance(table["number"], str):
                    self.errors.append(f"tables[{i}].number must be a string")
                else:
                    if table["number"] in seen_numbers:
                        self.warnings.append(f"Duplicate table number: {table['number']}")
                    seen_numbers.add(table["number"])

            if "caption" in table and not isinstance(table["caption"], str):
                self.errors.append(f"tables[{i}].caption must be a string")

            if "page" in table:
                if not isinstance(table["page"], int):
                    self.errors.append(f"tables[{i}].page must be an integer")
                elif table["page"] <= 0:
                    self.errors.append(f"tables[{i}].page must be positive")

    def _validate_equations(self, equations: list[dict[str, Any]]):
        """Validate equations structure."""
        if not isinstance(equations, list):
            self.errors.append(f"equations must be a list, got {type(equations).__name__}")
            return

        seen_numbers = set()
        for i, equation in enumerate(equations):
            if not isinstance(equation, dict):
                self.errors.append(f"equations[{i}] must be a dict")
                continue

            # Check required fields
            required = ["type", "number", "page"]
            for key in required:
                if key not in equation:
                    self.errors.append(f"equations[{i}] missing '{key}' field")

            # Validate types
            if "type" in equation and equation["type"] != "equation":
                self.warnings.append(
                    f"equations[{i}].type should be 'equation', got '{equation['type']}'"
                )

            if "number" in equation:
                if not isinstance(equation["number"], str):
                    self.errors.append(f"equations[{i}].number must be a string")
                else:
                    if equation["number"] in seen_numbers:
                        self.warnings.append(f"Duplicate equation number: {equation['number']}")
                    seen_numbers.add(equation["number"])

            if "page" in equation:
                if not isinstance(equation["page"], int):
                    self.errors.append(f"equations[{i}].page must be an integer")
                elif equation["page"] <= 0:
                    self.errors.append(f"equations[{i}].page must be positive")

    def _validate_references(self, references: list[dict[str, str]]):
        """Validate references structure."""
        if not isinstance(references, list):
            self.errors.append(f"references must be a list, got {type(references).__name__}")
            return

        seen_numbers = set()
        for i, reference in enumerate(references):
            if not isinstance(reference, dict):
                self.errors.append(f"references[{i}] must be a dict")
                continue

            # Check required fields
            if "number" not in reference:
                self.errors.append(f"references[{i}] missing 'number' field")
            elif not isinstance(reference["number"], str):
                self.errors.append(f"references[{i}].number must be a string")
            else:
                if reference["number"] in seen_numbers:
                    self.warnings.append(f"Duplicate reference number: {reference['number']}")
                seen_numbers.add(reference["number"])

            if "text" not in reference:
                self.errors.append(f"references[{i}] missing 'text' field")
            elif not isinstance(reference["text"], str):
                self.errors.append(f"references[{i}].text must be a string")
            elif not reference["text"].strip():
                self.warnings.append(f"references[{i}] has empty text")

    def _validate_acronyms(self, acronyms: dict[str, str]):
        """Validate acronyms structure."""
        if not isinstance(acronyms, dict):
            self.errors.append(f"acronyms must be a dict, got {type(acronyms).__name__}")
            return

        for key, value in acronyms.items():
            if not isinstance(key, str):
                self.errors.append(f"acronyms key must be a string, got {type(key).__name__}")
            elif not key.strip():
                self.warnings.append("Empty string used as acronym key")

            if not isinstance(value, str):
                self.errors.append(
                    f"acronyms['{key}'] must be a string, got {type(value).__name__}"
                )
            elif not value.strip():
                self.warnings.append(f"acronyms['{key}'] has empty expansion")

    def get_report(self) -> str:
        """Get validation report."""
        lines = []
        lines.append("=" * 60)
        lines.append("VALIDATION REPORT")
        lines.append("=" * 60)

        if not self.errors and not self.warnings:
            lines.append("✅ All checks passed!")
        else:
            if self.errors:
                lines.append(f"\n❌ ERRORS ({len(self.errors)}):")
                for error in self.errors:
                    lines.append(f"  • {error}")

            if self.warnings:
                lines.append(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
                for warning in self.warnings:
                    lines.append(f"  • {warning}")

        lines.append("=" * 60)
        return "\n".join(lines)


def validate_output(
    data: dict[str, Any] | str | Path, strict: bool = True, verbose: bool = True
) -> bool:
    """Convenience function to validate output JSON.

    Args:
        data: Dictionary, JSON string, or path to JSON file.
        strict: If True, raise exceptions on validation failures.
        verbose: If True, print validation report.

    Returns:
        True if validation passes, False otherwise.

    Raises:
        ValidationError: If strict mode is enabled and validation fails.
    """
    validator = OutputValidator(strict=strict)
    result = validator.validate(data)

    if verbose:
        print(validator.get_report())

    return result


if __name__ == "__main__":
    import sys

    # Command-line validation
    if len(sys.argv) < 2:
        print("Usage: python validate_output.py <path_to_json_file>")
        sys.exit(1)

    try:
        result = validate_output(sys.argv[1], strict=False, verbose=True)
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
