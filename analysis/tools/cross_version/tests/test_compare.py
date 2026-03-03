"""Tests for the cross-version comparison engine."""
from __future__ import annotations

from pathlib import Path

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
