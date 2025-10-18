#!/usr/bin/env python3
"""
Schema Validation Utility
AI Agent Governance Framework v2.1
Control: G-01 (Schema Compliance)

Purpose: Validate JSON data against framework schemas
Usage: python3 validate-schema.py --schema <schema-file> --data <data-file>

Features:
  - Validates against JSON Schema Draft 7
  - Detailed error reporting
  - Batch validation support
  - CI/CD integration ready
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import jsonschema
    from jsonschema import Draft7Validator, validators
except ImportError:
    print("❌ ERROR: jsonschema library not installed")
    print("Install via: pip install jsonschema")
    sys.exit(2)


class SchemaValidator:
    """JSON Schema validator with enhanced error reporting"""

    def __init__(self, schema_path: str):
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)

    def _load_schema(self) -> Dict:
        """Load and parse JSON schema"""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        with open(self.schema_path, 'r') as f:
            schema = json.load(f)

        # Validate schema itself
        Draft7Validator.check_schema(schema)
        return schema

    def validate(self, data: Dict) -> tuple[bool, List[str]]:
        """
        Validate data against schema

        Args:
            data: JSON data to validate

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        for error in self.validator.iter_errors(data):
            error_msg = self._format_error(error)
            errors.append(error_msg)

        return (len(errors) == 0, errors)

    def _format_error(self, error: jsonschema.ValidationError) -> str:
        """Format validation error with context"""
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        return f"[{path}] {error.message}"

    def validate_file(self, data_path: str) -> tuple[bool, List[str]]:
        """Validate data from file"""
        data_file = Path(data_path)

        if not data_file.exists():
            return (False, [f"Data file not found: {data_path}"])

        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return (False, [f"Invalid JSON: {str(e)}"])

        return self.validate(data)


def print_validation_result(schema_name: str, data_name: str, is_valid: bool, errors: List[str]):
    """Print formatted validation result"""
    print("=" * 60)
    print(f"Schema Validation: {schema_name}")
    print("=" * 60)
    print(f"Data file: {data_name}")
    print()

    if is_valid:
        print("✅ VALIDATION PASSED")
        print()
        print(f"The data conforms to schema: {schema_name}")
    else:
        print("❌ VALIDATION FAILED")
        print()
        print(f"Found {len(errors)} validation error(s):")
        print()
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")

    print("=" * 60)


def validate_all_examples(schema_dir: str = "policies/schemas") -> int:
    """Validate all example files against their schemas"""
    schema_path = Path(schema_dir)

    validations = [
        ("audit-trail.json", "test/example-audit-trail.json"),
        ("siem-event.json", "test/example-siem-event.json"),
        ("agent-cost-record.json", "test/example-cost-record.json"),
    ]

    failures = 0

    print()
    print("🔍 Running batch schema validation...")
    print()

    for schema_file, data_file in validations:
        schema_full_path = schema_path / schema_file
        data_full_path = Path(data_file)

        if not schema_full_path.exists():
            print(f"⚠️  Schema not found: {schema_full_path}")
            continue

        if not data_full_path.exists():
            print(f"⚠️  Example not found: {data_full_path}")
            continue

        try:
            validator = SchemaValidator(str(schema_full_path))
            is_valid, errors = validator.validate_file(str(data_full_path))

            if is_valid:
                print(f"✅ {schema_file:30s} <- {data_file}")
            else:
                print(f"❌ {schema_file:30s} <- {data_file}")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"   • {error}")
                if len(errors) > 3:
                    print(f"   ... and {len(errors) - 3} more error(s)")
                failures += 1

        except Exception as e:
            print(f"❌ {schema_file:30s} <- {data_file}")
            print(f"   ERROR: {str(e)}")
            failures += 1

    print()
    if failures == 0:
        print("✅ All validations passed!")
    else:
        print(f"❌ {failures} validation(s) failed")

    return failures


def main():
    parser = argparse.ArgumentParser(
        description="Validate JSON data against framework schemas (G-01)"
    )
    parser.add_argument(
        "--schema",
        help="Path to JSON schema file (e.g., policies/schemas/audit-trail.json)"
    )
    parser.add_argument(
        "--data",
        help="Path to JSON data file to validate"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Validate all example files against their schemas"
    )
    parser.add_argument(
        "--schema-dir",
        default="policies/schemas",
        help="Directory containing schemas (default: policies/schemas)"
    )

    args = parser.parse_args()

    # Batch validation mode
    if args.batch:
        failures = validate_all_examples(args.schema_dir)
        sys.exit(0 if failures == 0 else 1)

    # Single file validation mode
    if not args.schema or not args.data:
        parser.print_help()
        print()
        print("Examples:")
        print("  # Validate single file")
        print("  python3 validate-schema.py \\")
        print("    --schema policies/schemas/audit-trail.json \\")
        print("    --data test/example-audit-trail.json")
        print()
        print("  # Validate all examples")
        print("  python3 validate-schema.py --batch")
        sys.exit(2)

    try:
        validator = SchemaValidator(args.schema)
        is_valid, errors = validator.validate_file(args.data)

        schema_name = Path(args.schema).name
        data_name = Path(args.data).name

        print_validation_result(schema_name, data_name, is_valid, errors)

        sys.exit(0 if is_valid else 1)

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
