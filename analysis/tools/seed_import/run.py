"""CLI entry point for one-shot seed import into .audit.yaml sidecars."""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

from analysis.tools.proto_schema_validator.mapping import load_mapping
from analysis.tools.proto_schema_validator.models import ProtoMapping
from analysis.tools.seed_import.generate import (
    _METHOD_TAGS,
    compute_tier,
    generate_audit_yaml,
    make_evidence_entry,
    sidecar_path,
    validate_audit,
    write_audit_yaml,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]

# --- Exclusion patterns (reused from proto_triage/signals.py) ---

_INTERNAL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"analytics", re.IGNORECASE),
    re.compile(r"feedback", re.IGNORECASE),
    re.compile(r"survey", re.IGNORECASE),
    re.compile(r"crash", re.IGNORECASE),
    re.compile(r"telemetry", re.IGNORECASE),
    re.compile(r"firebase", re.IGNORECASE),
    re.compile(r"InstallReferrer", re.IGNORECASE),
    re.compile(r"bugreport", re.IGNORECASE),
    re.compile(r"clearcut", re.IGNORECASE),
    re.compile(r"ConnectivityEvent", re.IGNORECASE),
    re.compile(r"performance\.primes", re.IGNORECASE),
    re.compile(r"CarSetupService", re.IGNORECASE),
    re.compile(r"HatsService", re.IGNORECASE),
    re.compile(r"dapper", re.IGNORECASE),
    re.compile(r"FailureInjection", re.IGNORECASE),
    re.compile(r"AudioDiagnostics", re.IGNORECASE),
    re.compile(r"suggestion", re.IGNORECASE),
    re.compile(r"AssistantConnection", re.IGNORECASE),
]

_TELEMETRY_ROOT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ConnectivityEvent", re.IGNORECASE),
    re.compile(r"clearcut", re.IGNORECASE),
    re.compile(r"performance\.primes", re.IGNORECASE),
    re.compile(r"[Tt]elemetry"),
    re.compile(r"CarSetupService", re.IGNORECASE),
    re.compile(r"HatsService", re.IGNORECASE),
    re.compile(r"dapper", re.IGNORECASE),
    re.compile(r"FailureInjection", re.IGNORECASE),
    re.compile(r"AudioDiagnostics", re.IGNORECASE),
]

# Utility classes excluded by triage
_UTILITY_EXCLUSIONS: set[str] = {"zyd"}  # PingConfiguration — generic Duration


def _is_excluded(mapping: ProtoMapping) -> bool:
    """Check if a mapping should be excluded (telemetry/noise/utility)."""
    check_strings = [mapping.proto_message, mapping.proto_fqn]

    for s in check_strings:
        for pat in _INTERNAL_PATTERNS:
            if pat.search(s):
                return True
        for pat in _TELEMETRY_ROOT_PATTERNS:
            if pat.search(s):
                return True

    # Check APK classes against exclusions
    for cls in mapping.apk_classes.values():
        if cls is not None and cls in _UTILITY_EXCLUSIONS:
            return True

    return False


def _pick_primary_message(proto_file: str, mappings: list[ProtoMapping]) -> str:
    """Pick the primary message for a proto file.

    Heuristic: prefer the message whose name matches the proto filename.
    For oaa/sensor/FooData.proto, look for 'Foo' or a message ending in the
    base name. Falls back to the first mapping.
    """
    # Extract base name: oaa/sensor/SensorData.proto -> SensorData
    stem = Path(proto_file).stem
    # Strip common suffixes to find core name
    for suffix in ("Message", "Data", "Enum"):
        if stem.endswith(suffix):
            core = stem[: -len(suffix)]
            break
    else:
        core = stem

    # Exact match on stem
    for m in mappings:
        if m.proto_message == stem:
            return m.proto_message

    # Match on core name
    for m in mappings:
        if m.proto_message == core:
            return m.proto_message

    # Match message that starts with core
    for m in mappings:
        if m.proto_message.startswith(core):
            return m.proto_message

    # Fallback: first message
    return mappings[0].proto_message


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="One-shot import of class_mapping.yaml into .audit.yaml sidecars."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be done without writing files.",
    )
    parser.add_argument(
        "--mapping", type=Path, default=None,
        help="Path to class_mapping.yaml (default: auto-detect).",
    )
    args = parser.parse_args(argv)

    mappings = load_mapping(args.mapping)

    # Counters
    total = len(mappings)
    excluded = 0
    skipped_no_proto = 0
    written = 0
    validation_errors = 0
    by_confidence: dict[str, int] = {}
    total_messages_imported = 0

    # Group non-excluded mappings by proto_file
    by_file: dict[str, list[ProtoMapping]] = defaultdict(list)

    for m in mappings:
        if _is_excluded(m):
            excluded += 1
            continue

        proto_full = _REPO_ROOT / m.proto_file
        if not proto_full.exists():
            skipped_no_proto += 1
            if args.dry_run:
                print(f"  SKIP (no proto): {m.proto_file} [{m.proto_message}]")
            continue

        by_file[m.proto_file].append(m)

    # Process each proto file (one sidecar per file)
    for proto_file, file_mappings in sorted(by_file.items()):
        primary = _pick_primary_message(proto_file, file_mappings)

        # Collect evidence from all mappings for this file
        evidence = []
        for m in file_mappings:
            method_tag = _METHOD_TAGS.get(m.confidence, m.confidence)
            entry = make_evidence_entry(m, method_tag)
            # Avoid duplicate evidence entries (same message + method)
            if entry not in evidence:
                evidence.append(entry)

        tier = compute_tier(evidence)

        audit = generate_audit_yaml(
            proto_path=proto_file,
            message_name=primary,
            confidence=tier,
            evidence=evidence,
        )

        # Validate against schema
        try:
            validate_audit(audit)
        except Exception as e:
            print(f"  VALIDATION ERROR: {proto_file}: {e}", file=sys.stderr)
            validation_errors += 1
            continue

        # Write sidecar
        out = _REPO_ROOT / sidecar_path(proto_file)
        if args.dry_run:
            msg_names = [m.proto_message for m in file_mappings]
            print(f"  WRITE: {out.relative_to(_REPO_ROOT)}  ({len(file_mappings)} msgs: {', '.join(msg_names)})")
        else:
            write_audit_yaml(audit, out)

        written += 1
        total_messages_imported += len(file_mappings)
        by_confidence[tier] = by_confidence.get(tier, 0) + 1

    # Summary report
    print()
    print("=" * 60)
    print("Seed Import Report")
    print("=" * 60)
    print(f"Total mappings:      {total}")
    print(f"Excluded (noise):    {excluded}")
    print(f"Skipped (no proto):  {skipped_no_proto}")
    print(f"Audit files written: {written}")
    print(f"Messages imported:   {total_messages_imported}")
    if validation_errors:
        print(f"Validation errors:   {validation_errors}")
    print()
    print("By confidence tier:")
    for tier, count in sorted(by_confidence.items()):
        print(f"  {tier}: {count}")
    print("=" * 60)

    if validation_errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
