#!/usr/bin/env python3
"""Add confidence annotation comments to .proto files from .audit.yaml sidecars.

Usage:
    python -m analysis.tools.seed_import.annotate oaa/sensor oaa/common

Reads .audit.yaml sidecar files and inserts confidence comments:
- Above each `message` or `enum` declaration: // confidence: {tier} [{evidence_types}]
- At end of each field line: // confidence: {tier} [{evidence_types}]

The audit YAML is the source of truth; proto comments are a convenience mirror.
"""

import os
import re
import sys
from pathlib import Path

import yaml


def load_audit_yaml(proto_path: Path) -> dict | None:
    """Load the audit YAML sidecar for a proto file, if it exists."""
    audit_path = proto_path.with_suffix('.audit.yaml')
    if not audit_path.exists():
        return None
    with open(audit_path) as f:
        return yaml.safe_load(f)


def format_confidence(tier: str, evidence: list[dict] | None) -> str:
    """Format a confidence annotation comment."""
    if not evidence or tier == 'unverified':
        return '// confidence: unverified'
    # Collect unique evidence types
    types = sorted(set(e.get('type', '') for e in evidence if e.get('type')))
    if types:
        return f'// confidence: {tier} [{", ".join(types)}]'
    return f'// confidence: {tier}'


def strip_existing_confidence(line: str) -> str:
    """Remove any existing confidence comment from a line."""
    # Remove trailing confidence comment (field lines)
    return re.sub(r'\s*// confidence:.*$', '', line)


def is_message_or_enum_decl(line: str) -> bool:
    """Check if line is a message or enum declaration."""
    stripped = line.strip()
    return bool(re.match(r'^(message|enum)\s+\w+', stripped))


def is_field_line(line: str) -> bool:
    """Check if line is a proto field (optional/required/repeated/map or proto3 bare type)."""
    stripped = line.strip()
    if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
        return False
    # Skip braces, package, syntax, import, option lines
    if stripped in ('{', '}', '};'):
        return False
    if stripped.startswith(('syntax', 'package', 'import ', 'option ')):
        return False
    # Proto field patterns: starts with label or type name, has field number
    # e.g. "optional bool is_night = 1;"
    # e.g. "repeated data.GPSLocation gps_location = 1;"
    # Also proto3 bare fields: "string name = 1;"
    # Enum values: "UNRESTRICTED = 0;"
    if re.search(r'=\s*\d+\s*;', stripped):
        # But skip enum values — only annotate the enum declaration itself
        if re.match(r'^[A-Z_]+\s*=\s*\d+', stripped):
            return False
        return True
    return False


def is_confidence_comment(line: str) -> bool:
    """Check if a line is a standalone confidence annotation comment."""
    return bool(re.match(r'^\s*// confidence:', line))


def annotate_proto(proto_path: Path, audit: dict | None) -> dict:
    """Annotate a single proto file. Returns stats dict."""
    stats = {'messages': 0, 'fields': 0, 'enums': 0}

    if audit:
        tier = audit.get('confidence', 'unverified')
        evidence = audit.get('evidence', [])
        # Check for field-level overrides
        field_overrides = audit.get('fields', {})
    else:
        tier = 'unverified'
        evidence = []
        field_overrides = {}

    confidence_comment = format_confidence(tier, evidence)

    with open(proto_path) as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip existing standalone confidence comments (will be re-inserted)
        if is_confidence_comment(line):
            i += 1
            continue

        if is_message_or_enum_decl(line):
            # Determine indent
            indent = re.match(r'^(\s*)', line).group(1)
            # Insert confidence comment above declaration
            new_lines.append(f'{indent}{confidence_comment}\n')
            new_lines.append(line)
            if 'message' in line:
                stats['messages'] += 1
            else:
                stats['enums'] += 1
        elif is_field_line(line):
            # Strip any existing confidence comment
            clean = strip_existing_confidence(line).rstrip('\n')
            # Check for field-level override
            field_match = re.search(r'(\w+)\s*=\s*\d+', clean)
            if field_match and field_match.group(1) in field_overrides:
                override = field_overrides[field_match.group(1)]
                fc = format_confidence(
                    override.get('confidence', tier),
                    override.get('evidence', evidence)
                )
            else:
                fc = confidence_comment

            # Find where the semicolon ends and any existing comment
            # Preserve existing non-confidence comments
            # Pattern: code_part ; existing_comment
            existing_comment = ''
            code_part = clean
            # Check for existing inline comment (not confidence)
            comment_match = re.search(r';\s*(//.*)', clean)
            if comment_match:
                existing_comment = comment_match.group(1).strip()
                code_part = clean[:comment_match.start() + 1]

            if existing_comment:
                new_lines.append(f'{code_part} {existing_comment}  {fc}\n')
            else:
                new_lines.append(f'{code_part}  {fc}\n')
            stats['fields'] += 1
        else:
            new_lines.append(line)

        i += 1

    with open(proto_path, 'w') as f:
        f.writelines(new_lines)

    return stats


def annotate_directory(dir_path: Path) -> dict:
    """Annotate all proto files in a directory."""
    totals = {'files': 0, 'messages': 0, 'fields': 0, 'enums': 0, 'with_audit': 0, 'without_audit': 0}

    proto_files = sorted(dir_path.glob('*.proto'))
    for proto_path in proto_files:
        audit = load_audit_yaml(proto_path)
        if audit:
            totals['with_audit'] += 1
        else:
            totals['without_audit'] += 1

        stats = annotate_proto(proto_path, audit)
        totals['files'] += 1
        totals['messages'] += stats['messages']
        totals['fields'] += stats['fields']
        totals['enums'] += stats['enums']

    return totals


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m analysis.tools.seed_import.annotate <dir1> [dir2] ...")
        sys.exit(1)

    grand_totals = {'files': 0, 'messages': 0, 'fields': 0, 'enums': 0, 'with_audit': 0, 'without_audit': 0}

    for dir_arg in sys.argv[1:]:
        dir_path = Path(dir_arg)
        if not dir_path.is_dir():
            print(f"Warning: {dir_arg} is not a directory, skipping")
            continue

        print(f"\n--- Annotating {dir_path} ---")
        totals = annotate_directory(dir_path)

        for key in grand_totals:
            grand_totals[key] += totals[key]

        print(f"  Files: {totals['files']}")
        print(f"  Messages annotated: {totals['messages']}")
        print(f"  Enums annotated: {totals['enums']}")
        print(f"  Fields annotated: {totals['fields']}")
        print(f"  With audit YAML: {totals['with_audit']}")
        print(f"  Without audit (unverified): {totals['without_audit']}")

    print(f"\n=== TOTALS ===")
    print(f"  Files: {grand_totals['files']}")
    print(f"  Messages annotated: {grand_totals['messages']}")
    print(f"  Enums annotated: {grand_totals['enums']}")
    print(f"  Fields annotated: {grand_totals['fields']}")
    print(f"  With audit YAML: {grand_totals['with_audit']}")
    print(f"  Without audit (unverified): {grand_totals['without_audit']}")


if __name__ == '__main__':
    main()
