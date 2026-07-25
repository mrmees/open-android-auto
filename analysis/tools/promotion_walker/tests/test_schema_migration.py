from __future__ import annotations
import json
import subprocess
import sys
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


def test_all_in_scope_sidecars_validate_except_documented_holdouts(schema: dict, repo_root: Path) -> None:
    """Validate the live in-scope inventory without freezing a stale file count."""
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
    assert total > 0, "expected at least one in-scope sidecar"
    assert not errors, \
        "Option B migration did not unblock all expected sidecars:\n" \
        + "\n".join(errors)


def test_cross_version_promotion_suite_remains_green(repo_root: Path) -> None:
    """The current cross-version promotion suite remains green after migration."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "analysis/tools/cross_version/tests/test_promoted_sidecars.py",
         "--tb=no", "-q"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    out = result.stdout + result.stderr
    assert result.returncode == 0, f"cross-version promotion suite failed:\n{out}"
