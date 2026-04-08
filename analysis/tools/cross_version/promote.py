"""Audit sidecar promotion logic.

Adds cross_version evidence to eligible sidecars and promotes bronze to silver.

Phase 8 (XVER-04) extends this with the strict "all 6 pairs clean" rule
used in the 4-version (15.9, 16.1, 16.2, 16.4) pipeline. The strict rule
lives alongside the original `promote_sidecars` helper for backwards
compatibility with the 3-version tests.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from analysis.tools.cross_version.compare import ComparisonResult
from analysis.tools.proto_schema_validator.models import IssueKind, ProtoMapping
from analysis.tools.seed_import.generate import (
    compute_tier,
    sidecar_path,
    validate_audit,
    write_audit_yaml,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]

# The 6 pairwise comparisons required for a Bronze → Silver promotion under
# the Phase 8 (XVER-04) strict rule. Stored as a frozenset of sorted tuples
# so order of (v1, v2) in a ComparisonResult doesn't matter.
REQUIRED_PAIRS: frozenset[tuple[str, str]] = frozenset(
    {
        ("15.9", "16.1"),
        ("15.9", "16.2"),
        ("15.9", "16.4"),
        ("16.1", "16.2"),
        ("16.1", "16.4"),
        ("16.2", "16.4"),
    }
)

_REQUIRED_VERSIONS: frozenset[str] = frozenset({"15.9", "16.1", "16.2", "16.4"})


def promote_sidecars(
    results: list[ComparisonResult],
    repo_root: Path | None = None,
) -> int:
    """Promote eligible audit sidecars from bronze to silver.

    For each consistent ComparisonResult, add cross_version evidence
    to the audit sidecar and recompute the confidence tier.

    Args:
        results: Comparison results from run_comparison.
        repo_root: Repository root path (default: auto-detected).

    Returns:
        Number of sidecars promoted.
    """
    root = repo_root or _REPO_ROOT
    promoted = 0

    for r in results:
        if not r.is_consistent:
            continue
        if not r.pairs_compared:
            continue

        sp = root / sidecar_path(r.mapping.proto_file)
        if not sp.exists():
            continue

        with open(sp) as f:
            audit = yaml.safe_load(f)

        if audit is None:
            continue

        # Skip if already has cross_version evidence
        evidence = audit.get("evidence", [])
        if any(e.get("type") == "cross_version" for e in evidence):
            continue

        # Add cross_version evidence
        versions = r.versions_matched
        evidence.append({
            "type": "cross_version",
            "method": "structural_comparison",
            "source": f"cross-version checker ({', '.join(versions)})",
            "date": date.today().isoformat(),
            "description": (
                f"Structural match confirmed across versions "
                f"{', '.join(versions)}. Field numbers, types, "
                f"and modifiers are consistent."
            ),
        })
        audit["evidence"] = evidence

        # Recompute tier
        audit["confidence"] = compute_tier(evidence)
        audit["last_updated"] = date.today().isoformat()

        # Validate and write
        validate_audit(audit)
        write_audit_yaml(audit, sp)
        promoted += 1

    return promoted


# ---------------------------------------------------------------------------
# Phase 8 (XVER-04) strict "all 6 pairs clean" promotion rule
# ---------------------------------------------------------------------------


def is_eligible_for_silver(
    mapping: ProtoMapping,
    result: ComparisonResult,
    field_counts_by_version: dict[str, int] | None = None,
) -> bool:
    """Strict "all 6 pairs clean" eligibility check (XVER-04).

    Returns True iff ALL of:
      1. `mapping.apk_classes` entries for 15.9, 16.1, 16.2, 16.4 are non-null.
      2. All 6 pairwise comparisons are present in `result.pairs_compared`.
      3. Zero FIELD_REMOVED issues across all pairs.
      4. Zero FIELD_TYPE_CHANGED issues across all pairs.
      5. Field count identical across all 4 versions (caller may pass
         `field_counts_by_version`; if omitted the caller accepts whatever
         the comparator already enforces).

    0-field marker classes never enter `result.pairs_compared` — they fail
    condition 2 and correctly return False.
    """
    apk = mapping.apk_classes
    if not all(apk.get(v) for v in _REQUIRED_VERSIONS):
        return False

    pairs_set = {tuple(sorted(p)) for p in result.pairs_compared}
    required_set = {tuple(sorted(p)) for p in REQUIRED_PAIRS}
    if not required_set.issubset(pairs_set):
        return False

    for issue in result.issues:
        if issue.kind in (IssueKind.FIELD_REMOVED, IssueKind.FIELD_TYPE_CHANGED):
            return False

    if field_counts_by_version is not None:
        counts = {field_counts_by_version.get(v) for v in _REQUIRED_VERSIONS}
        counts.discard(None)
        if len(counts) != 1:
            return False

    return True


def classify_sidecar_outcome(
    mapping: ProtoMapping,
    result: ComparisonResult | None,
    current_tier: str,
    field_counts_by_version: dict[str, int] | None = None,
) -> str:
    """Classify a sidecar's Phase 8 walker outcome.

    Returns one of:
      - ``promoted``                — Bronze proto met the strict rule
      - ``stayed_bronze_no_164``    — no 16.4 class in the mapping
      - ``stayed_bronze_marker``    — 0-field marker, no pairs compared
      - ``stayed_bronze_drift``     — Bronze with FIELD_REMOVED / FIELD_TYPE_CHANGED
      - ``drifted_silver_gold``     — Silver/Gold with drift (flagged, NOT downgraded)
      - ``already_silver_clean``    — Silver/Gold with no drift
      - ``stayed_bronze_not_eligible``— Bronze with clean pairs but missing some
    """
    has_164 = bool(mapping.apk_classes.get("16.4"))
    if not has_164:
        if current_tier == "bronze":
            return "stayed_bronze_no_164"
        return "already_silver_clean"

    if result is None or not result.pairs_compared:
        if current_tier == "bronze":
            return "stayed_bronze_marker"
        return "already_silver_clean"

    has_drift = any(
        i.kind in (IssueKind.FIELD_REMOVED, IssueKind.FIELD_TYPE_CHANGED)
        for i in result.issues
    )
    if has_drift:
        if current_tier in ("silver", "gold"):
            return "drifted_silver_gold"
        return "stayed_bronze_drift"

    # No drift, has pairs. Bronze candidates get the strict check.
    if current_tier == "bronze":
        if is_eligible_for_silver(mapping, result, field_counts_by_version):
            return "promoted"
        return "stayed_bronze_not_eligible"
    return "already_silver_clean"


def promote_eligible(
    mappings: list[ProtoMapping],
    results: list[ComparisonResult],
    *,
    dry_run: bool = False,
    run_date: str | None = None,
) -> list[tuple[str, str]]:
    """Orchestrate the Phase 8 promotion walk.

    Classifies every mapping's outcome, runs the sidecar walker to append
    the locked YAML evidence entries (unless ``dry_run=True``), and bumps
    the confidence tier on sidecars that were classified as ``promoted``.

    Returns a list of ``(proto_message, outcome)`` tuples in mapping order.
    """
    # Late import avoids a circular dependency — sidecar_walker imports
    # nothing from promote.py but both live under cross_version/.
    from analysis.tools.cross_version.sidecar_walker import walk_sidecars

    results_by_proto = {r.mapping.proto_file: r for r in results}
    outcomes: list[tuple[str, str]] = []

    # First pass: read each sidecar's current tier and classify outcome.
    for m in mappings:
        side_path = _REPO_ROOT / sidecar_path(m.proto_file)
        current_tier = "unverified"
        if side_path.exists():
            try:
                audit = yaml.safe_load(side_path.read_text())
                if audit:
                    current_tier = audit.get("confidence", "unverified")
            except Exception:
                outcomes.append((m.proto_message, "sidecar_read_error"))
                continue
        else:
            outcomes.append((m.proto_message, "no_sidecar"))
            continue

        result = results_by_proto.get(m.proto_file)
        outcome = classify_sidecar_outcome(m, result, current_tier)
        outcomes.append((m.proto_message, outcome))

    if dry_run:
        return outcomes

    # Second pass: walker writes the locked YAML entries (append-only).
    walk_sidecars(mappings, results, run_date=run_date)

    # Third pass: bump confidence tier on sidecars classified as promoted.
    for m, (_, outcome) in zip(mappings, outcomes, strict=False):
        if outcome != "promoted":
            continue
        side_path = _REPO_ROOT / sidecar_path(m.proto_file)
        if not side_path.exists():
            continue
        try:
            audit = yaml.safe_load(side_path.read_text())
        except yaml.YAMLError:
            continue
        if not audit:
            continue
        audit["confidence"] = "silver"
        audit["last_updated"] = run_date or date.today().isoformat()
        try:
            validate_audit(audit)
        except Exception:
            # Validation shouldn't fail here — if it does, leave tier alone
            # rather than breaking the walker's append-only contract.
            continue
        write_audit_yaml(audit, side_path)

    return outcomes
