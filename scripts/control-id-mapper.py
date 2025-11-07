#!/usr/bin/env python3
"""
Control ID Mapper for NIST 800-53 Rev 5 Migration
AI Agent Governance Framework v2.1

Purpose: Convert legacy control IDs to NIST 800-53 Rev 5 compliant format
Usage:
  # Convert single ID
  python3 control-id-mapper.py convert --id SEC-001

  # Convert file
  python3 control-id-mapper.py convert-file --input file.json --output file_migrated.json

  # Validate file for legacy IDs
  python3 control-id-mapper.py validate --file terraform/main.tf

  # Show mapping table
  python3 control-id-mapper.py list-mappings
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Comprehensive Legacy to NIST Mapping
LEGACY_TO_NIST = {
    # Access Control
    'SEC-003': 'AC-6',
    'AC-003': 'AC-6',
    'AC-004': 'AC-4',
    'MI-006': 'AC-6',
    'MI-020': 'AC-6-AI-1',
    'MI-007': 'AC-6-AI-2',
    'APP-001': 'AC-6-AI-2',

    # Audit and Accountability
    'COMP-001': 'AU-2',
    'AU-002': 'AU-2',
    'MI-019': 'AU-2',
    'G-07': 'AU-2',
    'AU-003': 'AU-3',
    'AU-006': 'AU-6',
    'AU-009': 'AU-9',
    'AU-012': 'AU-12',

    # Configuration Management
    'COMP-002': 'CM-3',
    'CM-002': 'CM-3',
    'MI-010': 'CM-7',
    'MI-016': 'CM-3-AI-1',
    'MI-022': 'CM-3-AI-1',

    # Identification and Authentication
    'SEC-001': 'IA-5',
    'IA-002': 'IA-5',
    'MI-003': 'IA-5',
    'IA-005': 'IA-5',

    # System and Communications Protection
    'SEC-002': 'SC-4',
    'COMP-003': 'SC-7(21)',
    'SC-028': 'SC-28',
    'MI-001': 'SC-4-AI-1',
    'MI-014': 'SC-4-AI-2',
    'MI-011': 'SC-4-AI-3',

    # System and Information Integrity
    'MI-002': 'SI-10',
    'MI-017': 'SI-10-AI-1',
    'MI-013': 'SI-7-AI-1',
    'MI-015': 'SI-7-AI-2',

    # Risk Assessment
    'MI-012': 'RA-5-AI-1',

    # Continuous Monitoring
    'MI-004': 'CA-7',
    'MI-009': 'CA-7-AI-1',
    'MI-024': 'CA-7-AI-2',

    # System and Services Acquisition
    'MI-021': 'SA-15-AI-1',

    # Governance (Custom)
    'G-001': 'AC-6-AI-1',
    'G-02': 'AC-6-AI-2',
    'G-05': 'CM-3',
    'G-101': 'AC-6-AI-1',
    'G-102': 'AC-6-AI-1',
    'G-103': 'AC-6-AI-1',
    'G-202': 'CM-3(2)',

    # Additional Mitigations
    'MI-005': 'AC-7',
    'MI-008': 'SC-7(21)',
    'MI-023': 'CA-7-AI-1',
}

# Reverse mapping for backwards compatibility
NIST_TO_LEGACY = {v: k for k, v in LEGACY_TO_NIST.items()}

# CCI Mappings
NIST_TO_CCI = {
    'AC-6': 'CCI-002220',
    'AC-6(1)': 'CCI-002233',
    'AC-6(2)': 'CCI-002234',
    'AC-6(9)': 'CCI-002235',
    'AC-6-AI-1': 'CCI-AI-005',
    'AC-6-AI-2': 'CCI-AI-006',
    'AU-2': 'CCI-000130',
    'AU-3': 'CCI-000131',
    'AU-3(1)': 'CCI-000133',
    'AU-3-AI-1': 'CCI-AI-008',
    'AU-6': 'CCI-000134',
    'AU-8': 'CCI-000159',
    'AU-9': 'CCI-000162',
    'AU-9(2)': 'CCI-001350',
    'AU-9(3)': 'CCI-001351',
    'AU-11': 'CCI-001849',
    'AU-12': 'CCI-000169',
    'CM-3': 'CCI-000066',
    'CM-3(2)': 'CCI-001813',
    'CM-3-AI-1': 'CCI-AI-007',
    'CM-4': 'CCI-001812',
    'CM-7': 'CCI-000381',
    'IA-5': 'CCI-000195',
    'IA-5(1)': 'CCI-000196',
    'IA-5(2)': 'CCI-004063',
    'IA-5(7)': 'CCI-004062',
    'SC-4': 'CCI-001414',
    'SC-4-AI-1': 'CCI-AI-003',
    'SC-4-AI-2': 'CCI-AI-004',
    'SC-7': 'CCI-000382',
    'SC-7(21)': 'CCI-003748',
    'SC-28': 'CCI-001199',
    'SC-28(1)': 'CCI-002475',
    'SI-10': 'CCI-002754',
    'SI-10-AI-1': 'CCI-AI-016',
    'SI-7-AI-1': 'CCI-AI-009',
    'SI-7-AI-2': 'CCI-AI-010',
    'RA-5-AI-1': 'CCI-AI-011',
    'CA-7': 'CCI-000366',
    'CA-7-AI-1': 'CCI-AI-012',
    'CA-7-AI-2': 'CCI-AI-017',
    'SA-15-AI-1': 'CCI-AI-013',
}

# Control family names
CONTROL_FAMILIES = {
    'AC': 'Access Control',
    'AU': 'Audit and Accountability',
    'CM': 'Configuration Management',
    'IA': 'Identification and Authentication',
    'SC': 'System and Communications Protection',
    'SI': 'System and Information Integrity',
    'RA': 'Risk Assessment',
    'CA': 'Continuous Monitoring',
    'SA': 'System and Services Acquisition',
    'IR': 'Incident Response',
    'PL': 'Planning',
}


class ControlIDMapper:
    """Convert between legacy and NIST control IDs"""

    def __init__(self):
        self.legacy_to_nist = LEGACY_TO_NIST
        self.nist_to_legacy = NIST_TO_LEGACY
        self.nist_to_cci = NIST_TO_CCI

    def convert_to_nist(self, legacy_id: str) -> Optional[str]:
        """
        Convert legacy ID to NIST format

        Args:
            legacy_id: Legacy control ID (e.g., SEC-001)

        Returns:
            NIST control ID (e.g., IA-5) or None if not mapped
        """
        return self.legacy_to_nist.get(legacy_id)

    def convert_to_legacy(self, nist_id: str) -> Optional[str]:
        """
        Convert NIST ID back to legacy format (for backwards compat)

        Args:
            nist_id: NIST control ID (e.g., IA-5)

        Returns:
            Legacy control ID (e.g., SEC-001) or None if not mapped
        """
        return self.nist_to_legacy.get(nist_id)

    def get_cci(self, nist_id: str) -> Optional[str]:
        """
        Get CCI for NIST control

        Args:
            nist_id: NIST control ID

        Returns:
            CCI identifier or None
        """
        return self.nist_to_cci.get(nist_id)

    def get_control_family(self, nist_id: str) -> Optional[str]:
        """
        Get control family name

        Args:
            nist_id: NIST control ID (e.g., AC-6)

        Returns:
            Family name (e.g., 'Access Control')
        """
        family = nist_id.split('-')[0]
        return CONTROL_FAMILIES.get(family)

    def is_ai_extension(self, nist_id: str) -> bool:
        """Check if control is an AI extension"""
        return '-AI-' in nist_id

    def find_legacy_ids_in_text(self, text: str) -> List[Tuple[str, str]]:
        """
        Find all legacy control IDs in text

        Args:
            text: Text to search

        Returns:
            List of (legacy_id, nist_id) tuples
        """
        matches = []
        for legacy_id, nist_id in self.legacy_to_nist.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(legacy_id) + r'\b'
            if re.search(pattern, text):
                matches.append((legacy_id, nist_id))
        return matches

    def convert_file(self, input_path: str, output_path: str,
                    file_type: str = 'auto') -> int:
        """
        Convert all legacy IDs in a file

        Args:
            input_path: Input file path
            output_path: Output file path
            file_type: File type (json, markdown, auto)

        Returns:
            Number of replacements made
        """
        with open(input_path, 'r') as f:
            content = f.read()

        # Detect file type
        if file_type == 'auto':
            if input_path.endswith('.json'):
                file_type = 'json'
            elif input_path.endswith('.md'):
                file_type = 'markdown'
            else:
                file_type = 'text'

        replacement_count = 0
        for legacy_id, nist_id in self.legacy_to_nist.items():
            # Use word boundaries for accurate replacement
            pattern = r'\b' + re.escape(legacy_id) + r'\b'
            old_content = content
            content = re.sub(pattern, nist_id, content)
            if content != old_content:
                count = len(re.findall(pattern, old_content))
                replacement_count += count
                print(f"  Replaced {count}x: {legacy_id} → {nist_id}")

        with open(output_path, 'w') as f:
            f.write(content)

        return replacement_count

    def validate_file(self, file_path: str) -> List[Tuple[int, str, str]]:
        """
        Find legacy IDs in file

        Args:
            file_path: File to validate

        Returns:
            List of (line_number, legacy_id, nist_id) tuples
        """
        issues = []
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                for legacy_id, nist_id in self.legacy_to_nist.items():
                    pattern = r'\b' + re.escape(legacy_id) + r'\b'
                    if re.search(pattern, line):
                        issues.append((line_num, legacy_id, nist_id))
        return issues

    def generate_mapping_table(self, format: str = 'markdown') -> str:
        """
        Generate mapping table

        Args:
            format: Output format (markdown, csv)

        Returns:
            Formatted table string
        """
        if format == 'markdown':
            table = "| Legacy ID | NIST ID | CCI | Family | AI Extension |\n"
            table += "|-----------|---------|-----|--------|-------------|\n"

            for legacy_id, nist_id in sorted(self.legacy_to_nist.items()):
                cci = self.get_cci(nist_id) or '-'
                family = self.get_control_family(nist_id) or '-'
                is_ai = '✓' if self.is_ai_extension(nist_id) else ''

                table += f"| {legacy_id} | {nist_id} | {cci} | {family} | {is_ai} |\n"

            return table

        elif format == 'csv':
            lines = ["Legacy ID,NIST ID,CCI,Family,AI Extension"]
            for legacy_id, nist_id in sorted(self.legacy_to_nist.items()):
                cci = self.get_cci(nist_id) or ''
                family = self.get_control_family(nist_id) or ''
                is_ai = 'Yes' if self.is_ai_extension(nist_id) else 'No'

                lines.append(f"{legacy_id},{nist_id},{cci},{family},{is_ai}")

            return '\n'.join(lines)

        return "Unsupported format"


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Control ID Mapper for NIST 800-53 Rev 5 Migration'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Convert single ID
    convert_parser = subparsers.add_parser('convert', help='Convert single control ID')
    convert_parser.add_argument('--id', required=True, help='Legacy control ID')

    # Convert file
    file_parser = subparsers.add_parser('convert-file', help='Convert IDs in file')
    file_parser.add_argument('--input', required=True, help='Input file path')
    file_parser.add_argument('--output', required=True, help='Output file path')
    file_parser.add_argument('--type', default='auto',
                            choices=['auto', 'json', 'markdown', 'text'],
                            help='File type')

    # Validate file
    validate_parser = subparsers.add_parser('validate', help='Find legacy IDs in file')
    validate_parser.add_argument('--file', required=True, help='File to validate')

    # List mappings
    list_parser = subparsers.add_parser('list-mappings', help='Show mapping table')
    list_parser.add_argument('--format', default='markdown',
                            choices=['markdown', 'csv'],
                            help='Output format')

    # Get CCI
    cci_parser = subparsers.add_parser('get-cci', help='Get CCI for control')
    cci_parser.add_argument('--id', required=True, help='NIST control ID')

    args = parser.parse_args()

    mapper = ControlIDMapper()

    if args.command == 'convert':
        nist_id = mapper.convert_to_nist(args.id)
        if nist_id:
            cci = mapper.get_cci(nist_id)
            family = mapper.get_control_family(nist_id)
            is_ai = mapper.is_ai_extension(nist_id)

            print(f"Legacy ID: {args.id}")
            print(f"NIST ID:   {nist_id}")
            print(f"CCI:       {cci or 'N/A'}")
            print(f"Family:    {family or 'N/A'}")
            print(f"AI Ext:    {'Yes' if is_ai else 'No'}")
        else:
            print(f"❌ No mapping found for {args.id}")
            sys.exit(1)

    elif args.command == 'convert-file':
        print(f"Converting {args.input} → {args.output}")
        count = mapper.convert_file(args.input, args.output, args.type)
        print(f"✅ Completed {count} replacements")

    elif args.command == 'validate':
        issues = mapper.validate_file(args.file)
        if issues:
            print(f"⚠️  Found {len(issues)} legacy control IDs in {args.file}:\n")
            for line_num, legacy_id, nist_id in issues:
                print(f"  Line {line_num}: {legacy_id} → {nist_id}")
            print(f"\nRun: python3 {sys.argv[0]} convert-file --input {args.file} --output {args.file}.migrated")
            sys.exit(1)
        else:
            print(f"✅ No legacy control IDs found in {args.file}")

    elif args.command == 'list-mappings':
        table = mapper.generate_mapping_table(args.format)
        print(table)

    elif args.command == 'get-cci':
        cci = mapper.get_cci(args.id)
        if cci:
            family = mapper.get_control_family(args.id)
            print(f"Control: {args.id}")
            print(f"CCI:     {cci}")
            print(f"Family:  {family}")
        else:
            print(f"❌ No CCI found for {args.id}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
