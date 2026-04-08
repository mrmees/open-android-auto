"""Tests for the audit sidecar promotion logic.

Covers both the original 3-version `promote_sidecars` helper and the new
Phase 8 (XVER-04) strict `is_eligible_for_silver` / `classify_sidecar_outcome`
rule.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from analysis.tools.cross_version.compare import ComparisonResult
from analysis.tools.cross_version.promote import (
    REQUIRED_PAIRS,
    classify_sidecar_outcome,
    is_eligible_for_silver,
    promote_sidecars,
)
from analysis.tools.proto_schema_validator.models import (
    DriftIssue,
    IssueKind,
    ProtoMapping,
    Severity,
)


def _make_consistent_result(proto_file: str, message: str) -> ComparisonResult:
    """Helper: create a consistent ComparisonResult for promotion testing."""
    return ComparisonResult(
        mapping=ProtoMapping(
            proto_message=message,
            proto_file=proto_file,
            apk_classes={"15.9": "vnx", "16.1": "vnx", "16.2": "voa"},
        ),
        pairs_compared=[("15.9", "16.1"), ("16.1", "16.2"), ("15.9", "16.2")],
        issues=[],
    )


def test_promotion(tmp_sidecar: Path):
    """Consistent comparison promotes bronze to silver with cross_version evidence."""
    result = _make_consistent_result(
        "oaa/sensor/SensorData.proto", "SensorData"
    )
    count = promote_sidecars(
        [result],
        repo_root=tmp_sidecar.parent.parent.parent,  # tmp_path
    )
    assert count == 1, f"Expected 1 promoted sidecar, got {count}"

    with open(tmp_sidecar) as f:
        audit = yaml.safe_load(f)

    assert audit["confidence"] == "silver"
    evidence_types = [e["type"] for e in audit["evidence"]]
    assert "cross_version" in evidence_types
    assert "apk_static" in evidence_types


def test_schema_valid(tmp_sidecar: Path):
    """Promoted sidecar still validates against audit-schema.json."""
    import jsonschema

    result = _make_consistent_result(
        "oaa/sensor/SensorData.proto", "SensorData"
    )
    promote_sidecars(
        [result],
        repo_root=tmp_sidecar.parent.parent.parent,
    )

    schema_path = Path(__file__).resolve().parents[4] / "docs" / "verification" / "audit-schema.json"
    with open(schema_path) as f:
        schema = json.load(f)
    with open(tmp_sidecar) as f:
        audit = yaml.safe_load(f)

    jsonschema.validate(audit, schema)


def test_skip_existing(tmp_sidecar: Path):
    """If sidecar already has cross_version evidence, promotion should skip it."""
    # First promotion
    result = _make_consistent_result(
        "oaa/sensor/SensorData.proto", "SensorData"
    )
    count1 = promote_sidecars(
        [result],
        repo_root=tmp_sidecar.parent.parent.parent,
    )
    assert count1 == 1

    # Second promotion -- should skip
    count2 = promote_sidecars(
        [result],
        repo_root=tmp_sidecar.parent.parent.parent,
    )
    assert count2 == 0, "Should skip already-promoted sidecar"

    # Verify no duplicate evidence
    with open(tmp_sidecar) as f:
        audit = yaml.safe_load(f)
    cross_version_count = sum(
        1 for e in audit["evidence"] if e["type"] == "cross_version"
    )
    assert cross_version_count == 1, "Should not have duplicate cross_version evidence"


# ---------------------------------------------------------------------------
# Phase 8 (XVER-04) strict promotion rule tests
# ---------------------------------------------------------------------------


def _mk_mapping(has_164: bool = True) -> ProtoMapping:
    return ProtoMapping(
        proto_message="T",
        proto_file="oaa/t/T.proto",
        apk_classes={
            "15.9": "a",
            "16.1": "b",
            "16.2": "c",
            "16.4": "d" if has_164 else None,
        },
    )


def _mk_result(
    mapping: ProtoMapping,
    pairs,
    issues: list[DriftIssue] | None = None,
) -> ComparisonResult:
    return ComparisonResult(
        mapping=mapping,
        pairs_compared=list(pairs),
        issues=list(issues or []),
    )


def test_all_six_clean():
    """All 6 pairs clean + non-null 16.4 → eligible."""
    m = _mk_mapping()
    r = _mk_result(m, REQUIRED_PAIRS)
    assert is_eligible_for_silver(m, r) is True


def test_all_six_clean_fails_on_missing_pair():
    m = _mk_mapping()
    pairs = [p for p in REQUIRED_PAIRS if tuple(sorted(p)) != ("15.9", "16.4")]
    r = _mk_result(m, pairs)
    assert is_eligible_for_silver(m, r) is False


def test_all_six_clean_fails_on_field_removed():
    m = _mk_mapping()
    issue = DriftIssue(
        apk_class_v1="c",
        apk_class_v2="d",
        kind=IssueKind.FIELD_REMOVED,
        severity=Severity.ERROR,
        field_number=5,
    )
    r = _mk_result(m, REQUIRED_PAIRS, [issue])
    assert is_eligible_for_silver(m, r) is False


def test_all_six_clean_fails_on_field_type_changed():
    m = _mk_mapping()
    issue = DriftIssue(
        apk_class_v1="c",
        apk_class_v2="d",
        kind=IssueKind.FIELD_TYPE_CHANGED,
        severity=Severity.WARNING,
        field_number=2,
    )
    r = _mk_result(m, REQUIRED_PAIRS, [issue])
    assert is_eligible_for_silver(m, r) is False


def test_all_six_clean_fails_on_null_164():
    m = _mk_mapping(has_164=False)
    r = _mk_result(m, REQUIRED_PAIRS)
    assert is_eligible_for_silver(m, r) is False


def test_all_six_clean_fails_on_field_count_mismatch():
    m = _mk_mapping()
    r = _mk_result(m, REQUIRED_PAIRS)
    # One version has a different field count → ineligible
    counts = {"15.9": 5, "16.1": 5, "16.2": 5, "16.4": 6}
    assert is_eligible_for_silver(m, r, counts) is False


def test_all_six_clean_passes_on_identical_field_counts():
    m = _mk_mapping()
    r = _mk_result(m, REQUIRED_PAIRS)
    counts = {"15.9": 5, "16.1": 5, "16.2": 5, "16.4": 5}
    assert is_eligible_for_silver(m, r, counts) is True


def test_zero_field_marker_stays_bronze():
    """A 0-field marker (no pairs_compared) stays Bronze with the marker outcome."""
    m = _mk_mapping()
    r = _mk_result(m, [])  # no pairs_compared
    assert classify_sidecar_outcome(m, r, "bronze") == "stayed_bronze_marker"


def test_drifted_not_downgraded():
    """Silver/Gold protos with drift are flagged, NOT downgraded."""
    m = _mk_mapping()
    issue = DriftIssue(
        apk_class_v1="c",
        apk_class_v2="d",
        kind=IssueKind.FIELD_REMOVED,
        severity=Severity.ERROR,
        field_number=5,
    )
    r = _mk_result(m, REQUIRED_PAIRS, [issue])
    assert classify_sidecar_outcome(m, r, "silver") == "drifted_silver_gold"
    assert classify_sidecar_outcome(m, r, "gold") == "drifted_silver_gold"


def test_drifted_bronze_stays_bronze_drift():
    m = _mk_mapping()
    issue = DriftIssue(
        apk_class_v1="c",
        apk_class_v2="d",
        kind=IssueKind.FIELD_TYPE_CHANGED,
        severity=Severity.WARNING,
        field_number=2,
    )
    r = _mk_result(m, REQUIRED_PAIRS, [issue])
    assert classify_sidecar_outcome(m, r, "bronze") == "stayed_bronze_drift"


def test_promoted_outcome_for_bronze_clean_all_six():
    m = _mk_mapping()
    r = _mk_result(m, REQUIRED_PAIRS)
    assert classify_sidecar_outcome(m, r, "bronze") == "promoted"


def test_bronze_no_164_outcome():
    m = _mk_mapping(has_164=False)
    r = _mk_result(m, REQUIRED_PAIRS)
    assert classify_sidecar_outcome(m, r, "bronze") == "stayed_bronze_no_164"


def test_live_promotion_snapshot():
    """Empirical snapshot: how many ACTUAL Bronze sidecars promote under the strict rule.

    Expected headline under the strict rule: 0 promotions (all 10 Bronze
    sidecars map to 0-field marker classes per 08-RESEARCH.md "Bronze
    Promotion Reality Check"). Cap at ≤3 as a sanity guard so a future
    matcher improvement that finds a genuinely consistent Bronze we didn't
    anticipate doesn't silently slip past.

    This test reads the actual confidence tier from each sidecar on disk
    rather than assuming every mapping is Bronze — that's the only way
    the strict rule's headline metric makes sense.
    """
    from analysis.tools.cross_version.compare import run_comparison
    from analysis.tools.cross_version.run import _find_db
    from analysis.tools.proto_schema_validator.mapping import load_mapping
    from analysis.tools.seed_import.generate import sidecar_path

    repo_root = Path(__file__).resolve().parents[4]
    db_paths = {
        "15.9": _find_db("15.9"),
        "16.1": _find_db("16.1"),
        "16.2": _find_db("16.2"),
        "16.4": _find_db("16.4"),
    }
    if not all(db_paths.values()):
        pytest.skip("One or more APK index DBs unavailable")

    mappings = load_mapping()
    results = run_comparison(db_paths, mappings)
    results_by_proto = {r.mapping.proto_file: r for r in results}

    promoted_count = 0
    bronze_sidecars_seen = 0
    for m in mappings:
        sp = repo_root / sidecar_path(m.proto_file)
        if not sp.exists():
            continue
        audit = yaml.safe_load(sp.read_text())
        if not audit:
            continue
        current_tier = audit.get("confidence", "unverified")
        if current_tier != "bronze":
            continue
        bronze_sidecars_seen += 1
        result = results_by_proto.get(m.proto_file)
        outcome = classify_sidecar_outcome(m, result, current_tier)
        if outcome == "promoted":
            promoted_count += 1

    assert bronze_sidecars_seen > 0, (
        "Expected at least one Bronze sidecar in oaa/ — snapshot baseline "
        "expected ~10 per 08-01-SUMMARY.md."
    )
    assert promoted_count <= 3, (
        f"Unexpected promotion count: {promoted_count} (of {bronze_sidecars_seen} "
        f"Bronze sidecars). Snapshot expected 0 per 08-RESEARCH.md 'Bronze "
        f"Promotion Reality Check'. If intentional, regenerate snapshot and "
        f"document in 08-02-SUMMARY.md."
    )
