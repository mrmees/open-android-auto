"""Tests for the cross-version comparison engine."""
from __future__ import annotations

from pathlib import Path

import pytest

from analysis.tools.proto_schema_validator.models import IssueKind, ProtoMapping
from analysis.tools.cross_version.compare import run_comparison


def test_field_added(mock_db_v1: Path, mock_db_v2: Path):
    """v2 has field 6 that v1 lacks -- expect FIELD_ADDED, not suspicious."""
    mappings = [
        ProtoMapping(
            proto_message="SensorData",
            proto_file="oaa/sensor/SensorData.proto",
            apk_classes={"v1": "vnx", "v2": "voa"},
        ),
    ]
    results = run_comparison(
        db_paths={"v1": mock_db_v1, "v2": mock_db_v2},
        mappings=mappings,
    )
    assert len(results) >= 1
    # Find the SensorData result
    r = results[0]
    added = [i for i in r.issues if i.kind == IssueKind.FIELD_ADDED]
    assert len(added) >= 1, "Expected at least one FIELD_ADDED issue"
    assert added[0].field_number == 6


def test_field_removed(mock_db_v1: Path, mock_db_v2: Path):
    """v2 missing field 5 from v1 -- expect FIELD_REMOVED flagged as suspicious."""
    mappings = [
        ProtoMapping(
            proto_message="SensorData",
            proto_file="oaa/sensor/SensorData.proto",
            apk_classes={"v1": "vnx", "v2": "voa"},
        ),
    ]
    results = run_comparison(
        db_paths={"v1": mock_db_v1, "v2": mock_db_v2},
        mappings=mappings,
    )
    r = results[0]
    removed = [i for i in r.issues if i.kind == IssueKind.FIELD_REMOVED]
    assert len(removed) >= 1, "Expected at least one FIELD_REMOVED issue"
    assert removed[0].field_number == 5
    assert r.has_suspicious, "FIELD_REMOVED should be flagged as suspicious"


def test_type_changed(mock_db_v1: Path, mock_db_v2: Path):
    """Field 3 changed type from enum to int32 -- expect FIELD_TYPE_CHANGED."""
    mappings = [
        ProtoMapping(
            proto_message="SensorData",
            proto_file="oaa/sensor/SensorData.proto",
            apk_classes={"v1": "vnx", "v2": "voa"},
        ),
    ]
    results = run_comparison(
        db_paths={"v1": mock_db_v1, "v2": mock_db_v2},
        mappings=mappings,
    )
    r = results[0]
    changed = [i for i in r.issues if i.kind == IssueKind.FIELD_TYPE_CHANGED]
    assert len(changed) >= 1, "Expected at least one FIELD_TYPE_CHANGED issue"
    assert changed[0].field_number == 3
    assert r.has_suspicious, "FIELD_TYPE_CHANGED should be flagged as suspicious"


def test_consistent_match(mock_db_v1: Path, mock_db_v2: Path):
    """Identical field sets across versions -- expect no issues, marked consistent."""
    mappings = [
        ProtoMapping(
            proto_message="SimpleMessage",
            proto_file="oaa/common/SimpleMessage.proto",
            apk_classes={"v1": "wab", "v2": "wbc"},
        ),
    ]
    results = run_comparison(
        db_paths={"v1": mock_db_v1, "v2": mock_db_v2},
        mappings=mappings,
    )
    assert len(results) == 1
    r = results[0]
    assert len(r.issues) == 0, f"Expected no issues, got {r.issues}"
    assert r.is_consistent, "Identical fields should be marked consistent"


def test_four_version_pairs(
    mock_db_v1: Path,
    mock_db_v2: Path,
    mock_db_v3: Path,
    mock_db_v4: Path,
    sample_mappings_4v,
):
    """4 versions → C(4,2) = 6 pairwise comparisons per mapping with all classes populated.

    Note: this test already passes against the existing version-agnostic run_comparison().
    It locks the 6-pair expansion contract so Task 2's CLI wiring can't silently drop it.
    """
    db_paths = {
        "15.9": mock_db_v1,
        "16.1": mock_db_v2,
        "16.2": mock_db_v3,
        "16.4": mock_db_v4,
    }
    # sample_mappings_4v uses '15.9' / '16.1' / '16.2' / '16.4' keys;
    # but mock_db_v1 / mock_db_v2 were designed around 'v1' / 'v2' key names
    # with classes vnx / voa (v1) and wab / wbc (v2). Re-key them.
    # sample_mappings has: SensorData {'15.9': 'vnx', '16.1': 'vnx', '16.2': 'voa'}
    #                      SimpleMessage {'15.9': 'wab', '16.1': 'wab', '16.2': 'wbc'}
    # sample_mappings_4v added '16.2'='vob' and '16.4'='wqs' — but that overwrites 16.2.
    # Since mock_db_v1 has vnx/wab and mock_db_v2 has voa/wbc, the 15.9 and 16.1 slots
    # should match the v1 content (vnx/wab), 16.2 should match v3 (vob/wbd) since that's
    # what db_paths['16.2'] points to, and 16.4 should match v4 (wqs/wwb).
    # sample_mappings_4v already sets '16.2' = 'vob' / 'wbd' and '16.4' = 'wqs' / 'wwb'.
    # We need to ensure 15.9 and 16.1 point into mock_db_v1's classes.
    for m in sample_mappings_4v:
        if m.proto_message == "SensorData":
            m.apk_classes["15.9"] = "vnx"
            m.apk_classes["16.1"] = "vnx"
        elif m.proto_message == "SimpleMessage":
            m.apk_classes["15.9"] = "wab"
            m.apk_classes["16.1"] = "wab"

    results = run_comparison(db_paths, sample_mappings_4v)
    # At least one mapping should have all 6 pairs compared successfully
    six_pair_results = [r for r in results if len(r.pairs_compared) == 6]
    assert len(six_pair_results) >= 1, (
        f"Expected ≥1 mapping with 6 pairs; got pairs_compared counts: "
        f"{[len(r.pairs_compared) for r in results]}"
    )
