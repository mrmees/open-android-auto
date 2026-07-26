#!/usr/bin/env python3
"""Add confidence annotation comments to .proto files from .audit.yaml sidecars.

Usage:
    python -m analysis.tools.seed_import.annotate oaa/sensor oaa/common

Reads .audit.yaml sidecar files and inserts confidence comments:
- Above each `message` or `enum` declaration: // confidence: {tier} [{evidence_types}]
- At end of each field line: // confidence: {tier} [{evidence_types}]

The audit YAML is the source of truth; proto comments are a convenience mirror.
"""

import argparse
import re
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


def render_annotated_content(
    content: str,
    audit: dict | None,
) -> tuple[str, dict[str, int]]:
    """Return generated proto text and declaration/field counts without I/O."""
    stats = {'messages': 0, 'fields': 0, 'enums': 0}

    tier = audit.get('confidence', 'unverified') if audit else 'unverified'
    evidence = audit.get('evidence', []) if audit else []
    field_overrides = audit.get('fields', {}) if audit else {}

    confidence_comment = format_confidence(tier, evidence)

    lines = content.splitlines(keepends=True)

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
            line_ending = '\r\n' if line.endswith('\r\n') else '\n'
            new_lines.append(f'{indent}{confidence_comment}{line_ending}')
            new_lines.append(line)
            if line.lstrip().startswith('message '):
                stats['messages'] += 1
            else:
                stats['enums'] += 1
        elif is_field_line(line):
            # Strip any existing confidence comment
            line_ending = '\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else ''
            line_body = line[:-len(line_ending)] if line_ending else line
            clean = strip_existing_confidence(line_body)
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
                new_lines.append(f'{code_part} {existing_comment}  {fc}{line_ending}')
            else:
                new_lines.append(f'{code_part}  {fc}{line_ending}')
            stats['fields'] += 1
        else:
            new_lines.append(line)

        i += 1

    return ''.join(new_lines), stats


def annotate_proto(
    proto_path: Path,
    audit: dict | None,
    *,
    check: bool = False,
) -> dict[str, int | bool]:
    """Write generated content, or report drift without writing in check mode."""
    with proto_path.open(encoding='utf-8', newline='') as proto_file:
        content = proto_file.read()
    rendered, stats = render_annotated_content(content, audit)
    changed = rendered != content

    if changed and not check:
        with proto_path.open('w', encoding='utf-8', newline='') as proto_file:
            proto_file.write(rendered)

    return {**stats, 'changed': changed}


def annotate_directory(dir_path: Path, *, check: bool = False) -> dict[str, int]:
    """Process direct child protos and include a changed-file count."""
    totals = {
        'files': 0,
        'messages': 0,
        'fields': 0,
        'enums': 0,
        'with_audit': 0,
        'without_audit': 0,
        'changed': 0,
    }

    proto_files = sorted(dir_path.glob('*.proto'))
    for proto_path in proto_files:
        audit = load_audit_yaml(proto_path)
        if audit:
            totals['with_audit'] += 1
        else:
            totals['without_audit'] += 1

        stats = annotate_proto(proto_path, audit, check=check)
        totals['files'] += 1
        totals['messages'] += int(stats['messages'])
        totals['fields'] += int(stats['fields'])
        totals['enums'] += int(stats['enums'])
        totals['changed'] += int(stats['changed'])
        if check and stats['changed']:
            print(f'DRIFT: {proto_path}')

    return totals


def main(argv: list[str] | None = None) -> int:
    """Return 1 when --check finds drift, otherwise 0."""
    parser = argparse.ArgumentParser(
        description='Add confidence annotations to direct-child proto files.'
    )
    parser.add_argument('--check', action='store_true', help='report drift without writing')
    parser.add_argument('directories', nargs='+', help='directories containing proto files')
    args = parser.parse_args(argv)

    grand_totals = {
        'files': 0,
        'messages': 0,
        'fields': 0,
        'enums': 0,
        'with_audit': 0,
        'without_audit': 0,
        'changed': 0,
    }

    for dir_arg in args.directories:
        dir_path = Path(dir_arg)
        if not dir_path.is_dir():
            print(f"Warning: {dir_arg} is not a directory, skipping")
            continue

        action = 'Checking' if args.check else 'Annotating'
        print(f"\n--- {action} {dir_path} ---")
        totals = annotate_directory(dir_path, check=args.check)

        for key in grand_totals:
            grand_totals[key] += totals[key]

        print(f"  Files: {totals['files']}")
        print(f"  Messages annotated: {totals['messages']}")
        print(f"  Enums annotated: {totals['enums']}")
        print(f"  Fields annotated: {totals['fields']}")
        print(f"  With audit YAML: {totals['with_audit']}")
        print(f"  Without audit (unverified): {totals['without_audit']}")
        print(f"  Changed: {totals['changed']}")

    print(f"\n=== TOTALS ===")
    print(f"  Files: {grand_totals['files']}")
    print(f"  Messages annotated: {grand_totals['messages']}")
    print(f"  Enums annotated: {grand_totals['enums']}")
    print(f"  Fields annotated: {grand_totals['fields']}")
    print(f"  With audit YAML: {grand_totals['with_audit']}")
    print(f"  Without audit (unverified): {grand_totals['without_audit']}")
    print(f"  Changed: {grand_totals['changed']}")

    return 1 if args.check and grand_totals['changed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
