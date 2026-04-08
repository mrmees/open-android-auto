"""Unit tests for the Phase 8 sidecar_walker module (XVER-03).

Covers the six must-pass contracts:
- content_hash excludes the `date` field (idempotency invariant)
- append-only (never rewrites existing evidence entries)
- idempotent (running twice produces no diff)
- non-blocking (malformed sidecars don't halt the walk)
- orphan logging (sidecars with no mapping are logged)
- schema compliant (generated entries validate against the migrated schema)
"""
from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from analysis.tools.cross_version.compare import ComparisonResult
from analysis.tools.cross_version.sidecar_walker import (
    METHOD_STR,
    SOURCE_STR,
    WalkResult,
    build_4version_entry,
    content_hash,
    walk_sidecars,
)
from analysis.tools.proto_schema_validator.models import (
    DriftIssue,
    IssueKind,
    ProtoMapping,
    Severity,
)

FIXTURES = Path(__file__).parent / "fixtures"

ALL_PAIRS = [
    ("15.9", "16.1"),
    ("15.9", "16.2"),
    ("15.9", "16.4"),
    ("16.1", "16.2"),
    ("16.1", "16.4"),
    ("16.2", "16.4"),
]


def _make_mapping(proto_file: str, include_164: bool = True) -> ProtoMapping:
    return ProtoMapping(
        proto_message="ExampleMessage",
        proto_file=proto_file,
        apk_classes={
            "15.9": "abc",
            "16.1": "abd",
            "16.2": "abe",
            "16.4": "abf" if include_164 else None,
        },
    )


def _make_result(
    mapping: ProtoMapping,
    pairs: list[tuple[str, str]],
    issues: list[DriftIssue] | None = None,
) -> ComparisonResult:
    return ComparisonResult(
        mapping=mapping,
        pairs_compared=list(pairs),
        issues=list(issues or []),
    )


def _prepare_tmp_oaa(tmp_path: Path, fixture_name: str, dest_name: str) -> Path:
    """Copy a fixture sidecar into a temporary oaa/ tree under the given name."""
    dest = tmp_path / "oaa" / dest_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURES / fixture_name, dest)
    return dest


# ---------------------------------------------------------------------------
# 1. content_hash excludes date
# ---------------------------------------------------------------------------


def test_content_hash_no_date():
    """Same content, different dates → identical hashes."""
    e1 = {
        "type": "cross_version",
        "method": METHOD_STR,
        "source": SOURCE_STR,
        "date": "2026-04-08",
        "description": "test description",
        "status": "consistent",
    }
    e2 = {
        "type": "cross_version",
        "method": METHOD_STR,
        "source": SOURCE_STR,
        "date": "2027-01-01",
        "description": "test description",
        "status": "consistent",
    }
    assert content_hash(e1) == content_hash(e2)


def test_content_hash_differs_on_description():
    """Different descriptions → different hashes (sanity check)."""
    e1 = {
        "type": "cross_version",
        "method": METHOD_STR,
        "source": SOURCE_STR,
        "date": "2026-04-08",
        "description": "one",
        "status": "consistent",
    }
    e2 = dict(e1)
    e2["description"] = "two"
    assert content_hash(e1) != content_hash(e2)


def test_content_hash_differs_on_status():
    """Different status fields → different hashes."""
    e1 = {
        "type": "cross_version",
        "method": METHOD_STR,
        "source": SOURCE_STR,
        "date": "2026-04-08",
        "description": "same",
        "status": "consistent",
    }
    e2 = dict(e1)
    e2["status"] = "unmappable_16_4"
    assert content_hash(e1) != content_hash(e2)


# ---------------------------------------------------------------------------
# 2. build_4version_entry shape
# ---------------------------------------------------------------------------


def test_build_entry_consistent():
    m = _make_mapping("oaa/t/T.proto")
    r = _make_result(m, ALL_PAIRS)
    entry = build_4version_entry(m, r, "2026-04-08")
    assert entry["status"] == "consistent"
    assert entry["source"] == SOURCE_STR
    assert entry["method"] == METHOD_STR
    assert entry["type"] == "cross_version"
    assert "drift_issues" not in entry


def test_build_entry_unmappable_16_4():
    m = _make_mapping("oaa/t/T.proto", include_164=False)
    entry = build_4version_entry(m, None, "2026-04-08")
    assert entry["status"] == "unmappable_16_4"


def test_build_entry_unmappable_marker():
    m = _make_mapping("oaa/t/T.proto")
    # Mapped but no pairs_compared → marker class
    r = _make_result(m, [])
    entry = build_4version_entry(m, r, "2026-04-08")
    assert entry["status"] == "unmappable_marker"


def test_build_entry_drift_detected():
    m = _make_mapping("oaa/t/T.proto")
    issue = DriftIssue(
        apk_class_v1="abe",
        apk_class_v2="abf",
        kind=IssueKind.FIELD_REMOVED,
        severity=Severity.ERROR,
        field_number=7,
    )
    r = _make_result(m, ALL_PAIRS, [issue])
    entry = build_4version_entry(m, r, "2026-04-08")
    assert entry["status"] == "drift_detected"
    assert "drift_issues" in entry
    assert len(entry["drift_issues"]) == 1
    di = entry["drift_issues"][0]
    assert di["kind"] == "field_removed"
    assert di["field"] == 7
    assert di["severity"] == "error"
    assert "16.4" in di["pair"]


# ---------------------------------------------------------------------------
# 3. Walker semantics: append-only, idempotent, non-blocking, orphan, schema
# ---------------------------------------------------------------------------


def test_append_only(tmp_path: Path):
    """Walker adds a new entry but does NOT modify existing ones."""
    dest = _prepare_tmp_oaa(
        tmp_path, "sidecar_clean.audit.yaml", "test_fixture/ExampleMessage.audit.yaml"
    )
    mappings = [_make_mapping("oaa/test_fixture/ExampleMessage.proto")]
    results = [_make_result(mappings[0], ALL_PAIRS)]
    wr = walk_sidecars(
        mappings,
        results,
        oaa_root=tmp_path / "oaa",
        skipped_log=tmp_path / "skipped.md",
    )
    assert wr.updated == 1
    audit = yaml.safe_load(dest.read_text())
    # Original 2 entries (apk_static + 3-version cross_version) + 1 new 4-version entry
    assert len(audit["evidence"]) == 3
    # Original entries are untouched
    assert audit["evidence"][0]["type"] == "apk_static"
    assert audit["evidence"][0]["source"] == "seed_import"
    assert audit["evidence"][1]["type"] == "cross_version"
    assert "(15.9, 16.1, 16.2)" in audit["evidence"][1]["source"]
    # New entry is the 4-version one
    assert audit["evidence"][2]["type"] == "cross_version"
    assert audit["evidence"][2]["source"] == SOURCE_STR
    assert audit["evidence"][2]["status"] == "consistent"


def test_idempotent(tmp_path: Path):
    """Second walker run produces the same cross_version entry count."""
    dest = _prepare_tmp_oaa(
        tmp_path, "sidecar_clean.audit.yaml", "test_fixture/ExampleMessage.audit.yaml"
    )
    mappings = [_make_mapping("oaa/test_fixture/ExampleMessage.proto")]
    results = [_make_result(mappings[0], ALL_PAIRS)]

    walk_sidecars(
        mappings,
        results,
        oaa_root=tmp_path / "oaa",
        skipped_log=tmp_path / "skipped.md",
    )
    first_audit = yaml.safe_load(dest.read_text())

    # Second run on a different day should dedupe
    wr2 = walk_sidecars(
        mappings,
        results,
        run_date="2027-01-01",
        oaa_root=tmp_path / "oaa",
        skipped_log=tmp_path / "skipped.md",
    )
    second_audit = yaml.safe_load(dest.read_text())

    first_xv = [e for e in first_audit["evidence"] if e["type"] == "cross_version"]
    second_xv = [e for e in second_audit["evidence"] if e["type"] == "cross_version"]
    assert len(first_xv) == len(second_xv)
    assert wr2.updated == 0
    assert wr2.dedup_skips == 1


def test_non_blocking(tmp_path: Path):
    """A malformed sidecar does NOT halt the walk."""
    _prepare_tmp_oaa(
        tmp_path,
        "sidecar_malformed.audit.yaml",
        "test_fixture/Broken.audit.yaml",
    )
    _prepare_tmp_oaa(
        tmp_path,
        "sidecar_clean.audit.yaml",
        "test_fixture/ExampleMessage.audit.yaml",
    )
    mappings = [_make_mapping("oaa/test_fixture/ExampleMessage.proto")]
    results = [_make_result(mappings[0], ALL_PAIRS)]
    wr = walk_sidecars(
        mappings,
        results,
        oaa_root=tmp_path / "oaa",
        skipped_log=tmp_path / "skipped.md",
    )
    # Walk continued past the malformed file
    assert wr.updated >= 1
    assert any("yaml_error" in reason for _, reason in wr.skipped)
    assert (tmp_path / "skipped.md").exists()


def test_orphan_logging(tmp_path: Path):
    """A sidecar whose proto_file is not in class_mapping.yaml is logged as orphan."""
    _prepare_tmp_oaa(
        tmp_path,
        "sidecar_orphan.audit.yaml",
        "test_fixture/Orphan.audit.yaml",
    )
    # Mapping refers to a different proto file — orphan sidecar has no match
    mappings = [_make_mapping("oaa/test_fixture/SomethingElse.proto")]
    wr = walk_sidecars(
        mappings,
        [],
        oaa_root=tmp_path / "oaa",
        skipped_log=tmp_path / "skipped.md",
    )
    assert any("orphan_no_mapping" in reason for _, reason in wr.skipped)
    skipped_md = (tmp_path / "skipped.md").read_text()
    assert "orphan_no_mapping" in skipped_md


def test_schema_compliant(tmp_path: Path):
    """Walker-generated entries pass schema validation (no skip due to validation)."""
    _prepare_tmp_oaa(
        tmp_path,
        "sidecar_clean.audit.yaml",
        "test_fixture/ExampleMessage.audit.yaml",
    )
    mappings = [_make_mapping("oaa/test_fixture/ExampleMessage.proto")]
    results = [_make_result(mappings[0], ALL_PAIRS)]
    wr = walk_sidecars(
        mappings,
        results,
        oaa_root=tmp_path / "oaa",
        skipped_log=tmp_path / "skipped.md",
    )
    assert wr.updated >= 1
    # No schema_validation_failed entries in skipped
    assert all(
        "schema_validation_failed" not in reason for _, reason in wr.skipped
    )


def test_drift_entry_schema_compliant(tmp_path: Path):
    """A drift_detected entry with drift_issues list validates against schema."""
    _prepare_tmp_oaa(
        tmp_path,
        "sidecar_clean.audit.yaml",
        "test_fixture/ExampleMessage.audit.yaml",
    )
    mappings = [_make_mapping("oaa/test_fixture/ExampleMessage.proto")]
    issue = DriftIssue(
        apk_class_v1="abe",
        apk_class_v2="abf",
        kind=IssueKind.FIELD_TYPE_CHANGED,
        severity=Severity.WARNING,
        field_number=3,
    )
    results = [_make_result(mappings[0], ALL_PAIRS, [issue])]
    wr = walk_sidecars(
        mappings,
        results,
        oaa_root=tmp_path / "oaa",
        skipped_log=tmp_path / "skipped.md",
    )
    assert wr.updated == 1
    audit = yaml.safe_load(
        (tmp_path / "oaa" / "test_fixture" / "ExampleMessage.audit.yaml").read_text()
    )
    new_entry = audit["evidence"][-1]
    assert new_entry["status"] == "drift_detected"
    assert new_entry["drift_issues"][0]["kind"] == "field_type_changed"
    assert new_entry["drift_issues"][0]["field"] == 3


def test_walkresult_dataclass():
    """WalkResult is a proper dataclass with the expected fields."""
    wr = WalkResult()
    assert wr.updated == 0
    assert wr.new_entries == 0
    assert wr.dedup_skips == 0
    assert wr.skipped == []
