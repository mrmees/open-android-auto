"""CLI entry point for proto schema validation.

Usage:
    python -m analysis.tools.proto_schema_validator.run \\
        --db analysis/android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db \\
        --output analysis/reports/validation-report.md

    python -m analysis.tools.proto_schema_validator.run --layers 1 \\
        --db analysis/android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analysis.tools.proto_schema_validator.mapping import (
    get_or_build_bundle,
    load_mapping,
)
from analysis.tools.proto_schema_validator.report import generate_report, write_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Proto schema validation tool")
    parser.add_argument(
        "--db",
        type=Path,
        required=True,
        help="Path to primary APK index SQLite database",
    )
    parser.add_argument(
        "--db-alt",
        type=Path,
        default=None,
        help="Path to alternate-version APK index DB (for Layer 3)",
    )
    parser.add_argument(
        "--capture",
        type=Path,
        default=None,
        help="Path to wire capture JSONL file (for Layer 2)",
    )
    parser.add_argument(
        "--mapping",
        type=Path,
        default=None,
        help="Path to class_mapping.yaml (default: auto-detect)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for markdown report (default: stdout)",
    )
    parser.add_argument(
        "--layers",
        type=str,
        default="1,2,3",
        help="Comma-separated layer numbers to run (default: 1,2,3)",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="16.1",
        help="APK version to validate against (default: 16.1)",
    )

    args = parser.parse_args(argv)
    layers = {int(x.strip()) for x in args.layers.split(",")}

    # Load mappings
    mappings = load_mapping(args.mapping)
    print(f"Loaded {len(mappings)} mappings", file=sys.stderr)

    # Count how many have APK class for the target version
    has_apk = [m for m in mappings if m.apk_classes.get(args.version)]
    print(f"  {len(has_apk)} have APK class for v{args.version}", file=sys.stderr)

    # Build descriptor bundle
    print("Building descriptor bundle...", file=sys.stderr)
    bundle = get_or_build_bundle()
    print("  Done.", file=sys.stderr)

    schema_issues = None
    wire_issues = None
    wire_stats = None
    drift_issues = None
    drift_stats = None

    # Layer 1: Schema vs APK DB
    if 1 in layers:
        print("Running Layer 1: Schema vs APK DB...", file=sys.stderr)
        from analysis.tools.proto_schema_validator.layer1_schema import run_layer1
        schema_issues = run_layer1(bundle.pool, mappings, args.db, args.version)
        errs = sum(1 for i in schema_issues if i.severity.value == "error")
        warns = sum(1 for i in schema_issues if i.severity.value == "warning")
        print(f"  {errs} errors, {warns} warnings", file=sys.stderr)

    # Layer 2: Wire capture
    if 2 in layers and args.capture:
        print("Running Layer 2: Wire capture validation...", file=sys.stderr)
        from analysis.tools.proto_schema_validator.layer2_wire import run_layer2
        wire_issues, wire_stats = run_layer2(bundle, args.capture)
        errs = sum(1 for i in wire_issues if i.severity.value == "error")
        warns = sum(1 for i in wire_issues if i.severity.value == "warning")
        print(f"  {errs} errors, {warns} warnings", file=sys.stderr)
    elif 2 in layers and not args.capture:
        print("  Skipping Layer 2 (no --capture provided)", file=sys.stderr)

    # Layer 3: Cross-version drift
    if 3 in layers and args.db_alt:
        print("Running Layer 3: Cross-version drift...", file=sys.stderr)
        from analysis.tools.proto_schema_validator.layer3_crossversion import run_layer3
        drift_issues, drift_stats = run_layer3(
            mappings, args.db, args.db_alt, args.version
        )
        print(f"  {len(drift_issues)} findings", file=sys.stderr)
    elif 3 in layers and not args.db_alt:
        print("  Skipping Layer 3 (no --db-alt provided)", file=sys.stderr)

    # Validated count = mappings that had an APK class AND a valid FQN
    validated_count = sum(
        1 for m in mappings
        if m.apk_classes.get(args.version) and m.proto_fqn
    )

    report = generate_report(
        schema_issues=schema_issues,
        wire_issues=wire_issues,
        drift_issues=drift_issues,
        mapping_count=len(mappings),
        validated_count=validated_count,
        wire_stats=wire_stats,
        drift_stats=drift_stats,
    )

    if args.output:
        write_report(report, args.output)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
