"""Parametric integration test: all silver-tier .audit.yaml sidecars pass schema validation.

Gap 2 (TOOL-02): Finds all silver-tier sidecars under oaa/ and validates each against
docs/verification/audit-schema.json. Also verifies they contain cross_version evidence entries.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = REPO_ROOT / "docs" / "verification" / "audit-schema.json"
OAA_ROOT = REPO_ROOT / "oaa"


def _load_schema() -> dict:
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _all_sidecars() -> list[Path]:
    return sorted(OAA_ROOT.rglob("*.audit.yaml"))


def _silver_sidecars() -> list[Path]:
    result = []
    for p in _all_sidecars():
        data = yaml.safe_load(p.read_text())
        if data and data.get("confidence") == "silver":
            result.append(p)
    return result


# Parametrize over all silver sidecars so each file gets its own test entry
_SILVER_SIDECARS = _silver_sidecars()


def test_silver_sidecars_exist():
    """At least one silver-tier sidecar must exist after Phase 3 promotion run."""
    assert len(_SILVER_SIDECARS) > 0, (
        "No silver-tier audit sidecars found under oaa/. "
        "Phase 3 promotion must have run."
    )


def test_silver_sidecar_count_matches_phase3_expectation():
    """Phase 3 SUMMARY documents 143 sidecars promoted. Verify we're in that range."""
    count = len(_SILVER_SIDECARS)
    assert count >= 100, (
        f"Expected 100+ silver-tier sidecars (Phase 3 promoted 143), found {count}"
    )


@pytest.mark.parametrize("sidecar_path", _SILVER_SIDECARS, ids=lambda p: p.relative_to(OAA_ROOT).as_posix())
def test_silver_sidecar_validates_against_schema(sidecar_path: Path):
    """Each silver-tier sidecar must validate against audit-schema.json."""
    schema = _load_schema()
    data = yaml.safe_load(sidecar_path.read_text())
    assert data is not None, f"{sidecar_path}: YAML parsed to None"

    # Will raise jsonschema.ValidationError if invalid
    jsonschema.validate(instance=data, schema=schema)


@pytest.mark.parametrize("sidecar_path", _SILVER_SIDECARS, ids=lambda p: p.relative_to(OAA_ROOT).as_posix())
def test_silver_sidecar_has_cross_version_evidence(sidecar_path: Path):
    """Every silver-tier sidecar must have at least one cross_version evidence entry."""
    data = yaml.safe_load(sidecar_path.read_text())
    evidence = data.get("evidence", [])
    cross_version_entries = [e for e in evidence if e.get("type") == "cross_version"]
    assert len(cross_version_entries) >= 1, (
        f"{sidecar_path.name}: silver-tier sidecar has no cross_version evidence. "
        f"Evidence types present: {[e.get('type') for e in evidence]}"
    )


@pytest.mark.parametrize("sidecar_path", _SILVER_SIDECARS, ids=lambda p: p.relative_to(OAA_ROOT).as_posix())
def test_silver_sidecar_cross_version_entry_has_required_fields(sidecar_path: Path):
    """cross_version evidence entries must have method, source, date, description."""
    data = yaml.safe_load(sidecar_path.read_text())
    evidence = data.get("evidence", [])
    for entry in evidence:
        if entry.get("type") != "cross_version":
            continue
        assert "method" in entry, (
            f"{sidecar_path.name}: cross_version entry missing 'method' field"
        )
        assert "source" in entry, (
            f"{sidecar_path.name}: cross_version entry missing 'source' field"
        )
        assert "date" in entry, (
            f"{sidecar_path.name}: cross_version entry missing 'date' field"
        )
        assert "description" in entry, (
            f"{sidecar_path.name}: cross_version entry missing 'description' field"
        )
