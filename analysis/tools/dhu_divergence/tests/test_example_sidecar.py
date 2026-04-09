"""Committed example Platinum sidecar validates against the migrated schema (TIER-01).

This is TIER-01's 'schema validates, example sidecar passes' acceptance criterion.
The example is a REAL committed sidecar under oaa/, not a fixture (per Pitfall 6
in 09-RESEARCH.md).
"""
from __future__ import annotations

from pathlib import Path

import jsonschema
import yaml


def test_example_sidecar_validates(repo_root: Path, schema: dict) -> None:
    example_path = repo_root / "oaa/video/VideoFocusRequestMessage.audit.yaml"
    assert example_path.exists(), f"Expected example sidecar at {example_path}"
    data = yaml.safe_load(example_path.read_text())

    # Must be promoted to platinum
    assert data["confidence"] == "platinum", (
        f"Expected confidence: platinum, got {data.get('confidence')}"
    )
    assert data.get("platinum_scope") == "single_oem", (
        "Example sidecar must set platinum_scope: single_oem"
    )

    # Must have a platinum_evidence entry
    evidence = data.get("evidence", [])
    pe_entries = [e for e in evidence if e.get("type") == "platinum_evidence"]
    assert len(pe_entries) >= 1, (
        "Example sidecar must have at least one platinum_evidence entry"
    )

    pe = pe_entries[0]
    # Required fields per the schema conditional
    for field in [
        "capture_path",
        "vehicle_metadata",
        "msg_seq",
        "ts_ms",
        "message_completeness",
        "attribution_method",
        "oem_scope",
        "applicability",
        "match_rules",
    ]:
        assert field in pe, f"platinum_evidence missing required field: {field}"

    # Full schema validation — this is the 'passes' criterion
    jsonschema.validate(data, schema)
