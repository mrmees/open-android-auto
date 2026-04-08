"""Tests for the 16.4 delta report generator.

XVER-02 — validates the 8 locked sections, JSON schema, spurious-enum
suppression, and baseline reproduction sha256 hashes.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
REPORT_DIR = REPO_ROOT / "analysis" / "reports" / "cross-version"


def test_section_structure() -> None:
    """16-4-delta-report.md contains all 8 locked sections in order."""
    md = (REPORT_DIR / "16-4-delta-report.md").read_text()
    required_sections = [
        "## 1. Summary",
        "## 2. New in 16.4",
        "## 3. Removed in 16.4",
        "## 4. Schema Changes",
        "## 5. Promoted Bronze → Silver",
        "## 6. Drifted Silver/Gold",
        "## 7. Unmappable Protos",
        "## 8. Baseline Reproduction",
    ]
    last_idx = -1
    for section in required_sections:
        idx = md.find(section)
        assert idx > last_idx, f"Missing or out-of-order section: {section}"
        last_idx = idx


def test_json_schema() -> None:
    """16-4-delta-report.json exposes the contract keys Phase 9 will consume."""
    data = json.loads((REPORT_DIR / "16-4-delta-report.json").read_text())
    for key in [
        "summary",
        "new_in_16_4",
        "removed_in_16_4",
        "schema_changes",
        "promoted_bronze_to_silver",
        "drifted_silver_gold",
        "unmappable",
        "baseline_reproduction",
        "known_indexer_artifacts",
    ]:
        assert key in data, f"Missing top-level key: {key}"


def test_spurious_enum_suppression() -> None:
    """The 4 known spurious enum drifts are suppressed from schema_changes and moved
    to known_indexer_artifacts.
    """
    data = json.loads((REPORT_DIR / "16-4-delta-report.json").read_text())
    spurious = {"DriverPosition", "HapticFeedbackType", "SensorErrorStatus", "CarLocalMediaPlayback"}
    schema_change_names = {e["proto_message"] for e in data.get("schema_changes", [])}
    assert spurious.isdisjoint(schema_change_names), (
        f"Spurious drifts leaked into schema_changes: {spurious & schema_change_names}"
    )
    artifact_names = {e["proto_message"] for e in data["known_indexer_artifacts"]}
    assert spurious.issubset(artifact_names), (
        f"known_indexer_artifacts is missing: {spurious - artifact_names}"
    )


def test_baseline_hashes() -> None:
    data = json.loads((REPORT_DIR / "16-4-delta-report.json").read_text())
    hashes = data["baseline_reproduction"]["db_sha256"]
    assert set(hashes.keys()) == {"15.9", "16.1", "16.2", "16.4"}
    for v, h in hashes.items():
        assert len(h) == 64, f"Invalid sha256 for {v}: {h!r} (length {len(h)})"
