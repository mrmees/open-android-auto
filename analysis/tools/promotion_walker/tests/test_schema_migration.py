from __future__ import annotations
import json
import subprocess
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, ValidationError


IN_SCOPE_DIRS = ("oaa/av", "oaa/media", "oaa/video", "oaa/audio")

# 3 sidecars that are expected to STAY invalid after Option B (different debt classes)
EXPECTED_INVALID_AFTER_MIGRATION = {
    # top-level `notes` field -- NOT whitelisted by Option B, deferred housekeeping
    "oaa/media/MediaPlaybackStatusEventMessage.audit.yaml",
    # confidence: superseded -- enum addition deferred to later housekeeping phase
    "oaa/media/CarLocalMediaPlaybackEnum.audit.yaml",
    # apk_static evidence entry missing required description field
    "oaa/video/VideoFocusIndicationMessage.audit.yaml",
}


def test_schema_adds_pending_platinum_evidence(schema: dict) -> None:
    """Phase 10 Wave 1: schema must add pending_platinum_evidence top-level array."""
    props = schema["properties"]
    assert "pending_platinum_evidence" in props, \
        "pending_platinum_evidence top-level property missing"
    ppe = props["pending_platinum_evidence"]
    assert ppe["type"] == "array"
    assert ppe["items"] == {"$ref": "#/$defs/evidence_entry"}, \
        "pending_platinum_evidence items must $ref the existing evidence_entry definition"


def test_schema_adds_corrections_whitelist(schema: dict) -> None:
    """Phase 10 Wave 1: schema must add corrections top-level array (Option B)."""
    props = schema["properties"]
    assert "corrections" in props, \
        "corrections top-level property missing (Option B)"
    corr = props["corrections"]
    assert corr["type"] == "array"
    assert corr["items"] == {"type": "string"}


def test_schema_adds_corrections_to_evidence_entry(schema: dict) -> None:
    """Phase 10 Wave 1: evidence_entry must also accept corrections (Rule 1 auto-fix).

    The 4 real oaa/media/ Gold sidecars carry corrections INSIDE evidence entries
    (on their apk_deep_trace entries), not at the top level. The schema must
    whitelist corrections in both locations.
    """
    ev_props = schema["$defs"]["evidence_entry"]["properties"]
    assert "corrections" in ev_props, \
        "corrections missing from evidence_entry properties (needed for real sidecars)"
    corr = ev_props["corrections"]
    assert corr["type"] == "array"
    assert corr["items"] == {"type": "string"}


def test_schema_root_still_closed(schema: dict) -> None:
    """additionalProperties: false must be preserved on the root object."""
    assert schema.get("additionalProperties") is False


def test_confidence_enum_unchanged(schema: dict) -> None:
    """Phase 10 does NOT touch the confidence enum -- superseded is deferred."""
    conf = schema["$defs"]["confidence_tier"]["enum"]
    assert sorted(conf) == sorted([
        "unverified", "bronze", "silver", "gold", "platinum", "retracted"
    ])


def test_fixture_schema_invalid_corrections_validates(schema: dict, repo_root: Path) -> None:
    """The fixture mirroring the 5 oaa/media/ Gold sidecars must validate under Option B."""
    fx = repo_root / "analysis/tools/promotion_walker/tests/fixtures/sidecar_schema_invalid_corrections.audit.yaml"
    sidecar = yaml.safe_load(fx.read_text())
    Draft202012Validator(schema).validate(sidecar)  # raises on failure


def test_all_36_in_scope_sidecars_validate(schema: dict, repo_root: Path) -> None:
    """After Option B, 33 of 36 in-scope sidecars validate; 3 known-holdouts are expected."""
    validator = Draft202012Validator(schema)
    errors = []
    total = 0
    for d in IN_SCOPE_DIRS:
        for path in sorted((repo_root / d).glob("*.audit.yaml")):
            total += 1
            rel = str(path.relative_to(repo_root))
            if rel in EXPECTED_INVALID_AFTER_MIGRATION:
                continue  # known holdout; deferred housekeeping
            try:
                validator.validate(yaml.safe_load(path.read_text()))
            except ValidationError as e:
                errors.append(f"{rel}: {e.message[:120]}")
    assert total == 36, f"expected 36 in-scope sidecars, found {total}"
    assert not errors, \
        "Option B migration did not unblock all expected sidecars:\n" \
        + "\n".join(errors)


def test_phase_8_baseline_preserved(repo_root: Path) -> None:
    """Phase 8 test_promoted_sidecars.py must remain at 334 passed / 1 failed after migration."""
    result = subprocess.run(
        ["python3", "-m", "pytest",
         "analysis/tools/cross_version/tests/test_promoted_sidecars.py",
         "--tb=no", "-q"],
        cwd=repo_root,
        env={"PYTHONPATH": str(repo_root), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    # pytest exit code 1 is expected (1 pre-existing failure), 0 would mean fewer tests
    out = result.stdout + result.stderr
    assert "334 passed" in out, f"Phase 8 baseline broken: output was:\n{out}"
    assert "1 failed" in out, f"Phase 8 baseline broken (expected 1 pre-existing failure):\n{out}"
