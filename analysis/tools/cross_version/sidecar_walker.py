"""Append-only audit sidecar walker for Phase 8 (XVER-03).

Walks all `oaa/**/*.audit.yaml` files, looks up the proto in the
4-version class_mapping.yaml, and appends a new `cross_version` evidence
entry describing the 16.4 outcome. Semantics:

- **Append-only**: NEVER rewrite or delete existing evidence entries.
  Existing `cross_version` entries for (15.9, 16.1, 16.2) stay as
  historical record. The new 4-version entry is added as a separate
  entry.
- **Idempotent**: running the walker twice produces byte-identical
  sidecars. Content-hash dedupe explicitly EXCLUDES the `date` field
  so re-runs on different days still dedupe.
- **Non-blocking**: malformed sidecars are logged to
  `analysis/reports/cross-version/skipped-sidecars.md` and the walk
  continues. No auto-repair; never silently rewrite human-curated
  evidence.
- **Orphan sidecars** (no class_mapping.yaml entry) are skipped and
  logged.

The locked YAML output format for new 4-version entries is in
`.planning/phases/08-16-4-cross-version-validation/08-CONTEXT.md`
§ "Output format for new 4-version cross_version entry".
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from jsonschema import ValidationError

from analysis.tools.cross_version.compare import ComparisonResult
from analysis.tools.proto_schema_validator.models import IssueKind, ProtoMapping
from analysis.tools.seed_import.generate import validate_audit, write_audit_yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
OAA_ROOT = _REPO_ROOT / "oaa"
SKIPPED_LOG = _REPO_ROOT / "analysis" / "reports" / "cross-version" / "skipped-sidecars.md"

SOURCE_STR = "cross-version checker (15.9, 16.1, 16.2, 16.4)"
METHOD_STR = "structural_comparison"


@dataclass
class WalkResult:
    """Summary of a sidecar walker run."""

    updated: int = 0
    new_entries: int = 0
    dedup_skips: int = 0
    skipped: list[tuple[Path, str]] = field(default_factory=list)


def content_hash(entry: dict[str, Any]) -> str:
    """Stable 16-char hash of a cross_version evidence entry.

    CRITICAL: excludes the `date` field so re-runs on different days
    produce identical hashes (PITFALL #6 in 08-RESEARCH.md).
    """
    payload = {
        "type": entry.get("type"),
        "method": entry.get("method"),
        "source": entry.get("source"),
        "description": entry.get("description"),
        "status": entry.get("status"),
        "drift_issues": entry.get("drift_issues"),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _extract_pair_for_issue(result: ComparisonResult) -> str:
    """Best-effort pair label for a drift issue. We prefer the 16.4 pairs.

    DriftIssue doesn't carry the pair itself — we infer "the comparison that
    produced it" from the issue's class names. For 16.4-era drift the
    FIELD_REMOVED / FIELD_TYPE_CHANGED issues typically come from a pair
    that includes 16.4. This helper tries to identify which pair an issue
    belongs to based on which of `result.pairs_compared` involves 16.4.
    """
    # If there's a 16.4 pair in the comparison, attribute drift to it.
    # Otherwise fall back to the last pair compared (most recent).
    for pair in result.pairs_compared:
        if "16.4" in pair:
            return f"{pair[0]}_vs_{pair[1]}"
    if result.pairs_compared:
        a, b = result.pairs_compared[-1]
        return f"{a}_vs_{b}"
    return "unknown_vs_unknown"


def _issue_field_value(issue: Any) -> int | str:
    """Return the field identifier for a DriftIssue as int or string."""
    if getattr(issue, "field_number", None) is not None:
        return int(issue.field_number)
    detail = getattr(issue, "detail", "") or ""
    return detail or "unknown"


def build_4version_entry(
    mapping: ProtoMapping,
    result: ComparisonResult | None,
    run_date: str,
) -> dict[str, Any]:
    """Build the locked 4-version YAML evidence entry for a sidecar.

    The output dict matches one of 4 shapes controlled by the class mapping
    + comparison result:

    - ``unmappable_16_4``: no 16.4 class in class_mapping.yaml
    - ``unmappable_marker``: class is mapped but comparator produced no pairs
      (typically a 0-field marker class)
    - ``drift_detected``: one or more FIELD_REMOVED / FIELD_TYPE_CHANGED issues
    - ``consistent``: all pairs clean
    """
    has_164 = bool(mapping.apk_classes.get("16.4"))
    if not has_164:
        return {
            "type": "cross_version",
            "method": METHOD_STR,
            "source": SOURCE_STR,
            "date": run_date,
            "description": (
                "Unmappable in 16.4 (matcher found no candidate meeting "
                "structural fingerprint + field count match, or candidate "
                "was ambiguous)."
            ),
            "status": "unmappable_16_4",
        }

    if result is None or not result.pairs_compared:
        # Class is mapped but comparator skipped it (0-field marker class).
        return {
            "type": "cross_version",
            "method": METHOD_STR,
            "source": SOURCE_STR,
            "date": run_date,
            "description": (
                "Zero-field marker class — structural comparison is "
                "trivially empty. Not eligible for Bronze → Silver "
                "promotion under the strict rule."
            ),
            "status": "unmappable_marker",
        }

    # Has pairs_compared. Check for drift.
    drift = [
        i
        for i in result.issues
        if i.kind in (IssueKind.FIELD_REMOVED, IssueKind.FIELD_TYPE_CHANGED)
    ]
    if drift:
        pair_label = _extract_pair_for_issue(result)
        return {
            "type": "cross_version",
            "method": METHOD_STR,
            "source": SOURCE_STR,
            "date": run_date,
            "description": (
                "Structural drift detected in 16.4 cross-version comparison. "
                "Flagged for human review — prior-version evidence preserved, "
                "tier NOT auto-downgraded."
            ),
            "status": "drift_detected",
            "drift_issues": [
                {
                    "pair": pair_label,
                    "kind": i.kind.value,
                    "field": _issue_field_value(i),
                    "severity": i.severity.value,
                }
                for i in drift
            ],
        }

    # All pairs clean — consistent entry.
    return {
        "type": "cross_version",
        "method": METHOD_STR,
        "source": SOURCE_STR,
        "date": run_date,
        "description": (
            "Structural match confirmed across versions 15.9, 16.1, 16.2, "
            "16.4. Field numbers, types, and modifiers are consistent "
            f"across all {len(result.pairs_compared)} pairwise comparisons."
        ),
        "status": "consistent",
    }


def walk_sidecars(
    mappings: list[ProtoMapping],
    comparison_results: list[ComparisonResult],
    run_date: str | None = None,
    oaa_root: Path = OAA_ROOT,
    skipped_log: Path = SKIPPED_LOG,
) -> WalkResult:
    """Walk every sidecar under oaa_root and append a 4-version entry.

    Semantics: append-only, idempotent, non-blocking. See module docstring.
    """
    run_date = run_date or date.today().isoformat()
    by_proto_file = {m.proto_file: m for m in mappings}
    results_by_proto = {r.mapping.proto_file: r for r in comparison_results}
    wr = WalkResult()

    for path in sorted(oaa_root.rglob("*.audit.yaml")):
        try:
            text = path.read_text()
            audit = yaml.safe_load(text)
        except yaml.YAMLError as e:
            wr.skipped.append((path, f"yaml_error: {type(e).__name__}"))
            continue
        except OSError as e:
            wr.skipped.append((path, f"io_error: {type(e).__name__}"))
            continue

        if audit is None:
            wr.skipped.append((path, "empty_yaml"))
            continue

        proto_file = audit.get("proto")
        mapping = by_proto_file.get(proto_file)
        if mapping is None:
            wr.skipped.append((path, "orphan_no_mapping"))
            continue

        new_entry = build_4version_entry(
            mapping,
            results_by_proto.get(proto_file),
            run_date,
        )
        new_hash = content_hash(new_entry)

        existing = audit.get("evidence", []) or []
        existing_hashes = {
            content_hash(e) for e in existing if e.get("type") == "cross_version"
        }

        if new_hash in existing_hashes:
            wr.dedup_skips += 1
            continue

        existing.append(new_entry)
        audit["evidence"] = existing
        audit["last_updated"] = run_date

        try:
            validate_audit(audit)
        except ValidationError as e:
            wr.skipped.append((path, f"schema_validation_failed: {e.message[:80]}"))
            continue

        write_audit_yaml(audit, path)
        wr.updated += 1
        wr.new_entries += 1

    _write_skipped_log(wr.skipped, skipped_log)
    return wr


def _write_skipped_log(
    skipped: list[tuple[Path, str]],
    log_path: Path,
) -> None:
    """Write the skipped-sidecars.md report."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Skipped Sidecars — Phase 8 Plan 02 Walker",
        "",
        f"Generated: {date.today().isoformat()}",
        f"Total skipped: {len(skipped)}",
        "",
        "Reasons: `yaml_error` (parse failure), `empty_yaml` (file is empty), "
        "`orphan_no_mapping` (no entry in class_mapping.yaml), "
        "`schema_validation_failed` (audit invalid after walker append — "
        "investigate).",
        "",
        "| Path | Reason |",
        "|------|--------|",
    ]
    for path, reason in sorted(skipped, key=lambda x: str(x[0])):
        lines.append(f"| `{path}` | {reason} |")
    log_path.write_text("\n".join(lines) + "\n")
