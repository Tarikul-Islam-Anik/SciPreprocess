# Output Validation System

This directory contains tools for validating the JSON output from the scipreprocess pipeline.

## 📋 Overview

The validation system ensures that processed documents have the correct structure and complete metadata. It checks:

- ✅ Required fields are present
- ✅ Data types are correct
- ✅ Field values are valid
- ⚠️ Duplicate entries
- ⚠️ Empty or suspicious content

## 🚀 Quick Start

### Command Line Validation

```bash
# Validate a specific JSON file
python tests/run_validation.py examples/output/test.json

# Run demo with sample data
python tests/run_validation.py
```

### Python API

```python
from tests.validate_output import validate_output, OutputValidator

# Simple validation
result = validate_output("output.json")

# Advanced validation with custom options
validator = OutputValidator(strict=False)
result = validator.validate("output.json")

# Get detailed report
print(validator.get_report())

# Access specific issues
print(f"Errors: {validator.errors}")
print(f"Warnings: {validator.warnings}")
```

## 📊 Validation Checks

### Top-Level Structure
- Required keys: `metadata`, `abstract`, `sections`, `figures`, `tables`, `equations`, `references`, `acronyms`
- Warns about unexpected keys

### Metadata
- **Required**: `title`, `source_file`
- **Optional**: `pages`
- Checks for empty values
- Validates page count is positive

### Abstract
- Must be a string
- Warns if empty or very short (< 50 chars)

### Sections
- Must be a list of dictionaries
- Each section requires:
  - `heading`: non-empty string
  - `text`: string (warns if empty)
- Detects duplicate headings (except "Abstract" and "Methods")

### Figures
- Each figure requires:
  - `type`: should be "figure"
  - `number`: unique string
  - `caption`: string
  - `page`: positive integer
- Detects duplicate figure numbers

### Tables
- Each table requires:
  - `type`: should be "table"
  - `number`: unique string
  - `caption`: string
  - `page`: positive integer
- Detects duplicate table numbers

### Equations
- Each equation requires:
  - `type`: should be "equation"
  - `number`: unique string
  - `page`: positive integer
- Detects duplicate equation numbers

### References
- Each reference requires:
  - `number`: unique string
  - `text`: non-empty string
- Detects duplicate reference numbers

### Acronyms
- Must be a dictionary
- Keys and values must be strings
- Warns if expansion is empty

## 🎯 Validation Modes

### Strict Mode (Default)
```python
validator = OutputValidator(strict=True)
try:
    validator.validate(data)
except ValidationError as e:
    print(f"Validation failed: {e}")
```
- Raises `ValidationError` on any error
- Best for CI/CD pipelines
- Ensures data quality

### Lenient Mode
```python
validator = OutputValidator(strict=False)
result = validator.validate(data)
if not result:
    print(f"Found {len(validator.errors)} errors")
```
- Returns boolean result
- Collects all errors and warnings
- Best for development and debugging

## 📝 Example Output

### Valid Data
```
============================================================
VALIDATION REPORT
============================================================
✅ All checks passed!
============================================================
```

### Invalid Data
```
============================================================
VALIDATION REPORT
============================================================

❌ ERRORS (3):
  • Missing required metadata field: 'source_file'
  • sections[0] missing 'text' field
  • figures[0].page must be an integer

⚠️  WARNINGS (2):
  • metadata.title is empty
  • Duplicate figure number: 1
============================================================
```

## 🧪 Running Tests

```bash
# Run all validation tests
pytest tests/test_validation.py -v

# Run specific test
pytest tests/test_validation.py::TestOutputValidator::test_valid_output -v
```

## 🔧 Integration with Pipeline

### During Processing
```python
from scipreprocess import preprocess_file
from tests.validate_output import validate_output

# Process document
doc_json, clean_text = preprocess_file("paper.pdf")

# Validate output
is_valid = validate_output(doc_json, strict=False)
if is_valid:
    # Save to file
    with open("output.json", "w") as f:
        json.dump(doc_json, f)
```

### Post-Processing Validation
```python
import json
from tests.validate_output import validate_output

# Load processed output
with open("output.json", "r") as f:
    data = json.load(f)

# Validate
if validate_output(data):
    print("✅ Output is valid")
else:
    print("❌ Output has issues")
```

## 📚 Files

- **`validate_output.py`**: Main validation module with `OutputValidator` class
- **`test_validation.py`**: Comprehensive test suite (pytest)
- **`run_validation.py`**: Standalone CLI validation tool
- **`VALIDATION_README.md`**: This documentation

## 🎓 Best Practices

1. **Always validate** output before using it in downstream tasks
2. **Use strict mode** in production/CI/CD
3. **Use lenient mode** during development to see all issues at once
4. **Check warnings** - they might indicate data quality issues
5. **Add custom validators** for domain-specific requirements

## 🛠️ Extending the Validator

To add custom validation rules:

```python
from tests.validate_output import OutputValidator

class CustomValidator(OutputValidator):
    def validate(self, data):
        # Call parent validation
        super().validate(data)
        
        # Add custom checks
        self._validate_custom_field(data)
        
        return len(self.errors) == 0
    
    def _validate_custom_field(self, data):
        if 'custom_field' in data:
            # Your validation logic
            if not data['custom_field']:
                self.errors.append("custom_field is empty")
```

## 📞 Support

For issues or questions:
1. Check this README
2. Run `python run_validation.py` for demo
3. Check test cases in `test_validation.py` for examples

