"""Tests for the audit sidecar promotion logic."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from analysis.tools.cross_version.promote import promote_sidecars
from analysis.tools.cross_version.compare import ComparisonResult
from analysis.tools.proto_schema_validator.models import ProtoMapping


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
