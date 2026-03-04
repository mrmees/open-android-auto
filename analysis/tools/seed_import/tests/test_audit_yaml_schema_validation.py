"""
VERI-01 / VERI-02 gap: validate all .audit.yaml sidecar files against audit-schema.json.

Finds every .audit.yaml under oaa/ and asserts each one passes JSON Schema
(Draft 2020-12) validation. Skips gracefully if no files exist yet.
"""

import json
import os
from pathlib import Path

import jsonschema
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = REPO_ROOT / "docs" / "verification" / "audit-schema.json"
OAA_ROOT = REPO_ROOT / "oaa"


def _load_schema():
    with open(SCHEMA_PATH) as fh:
        return json.load(fh)


def _find_audit_files():
    if not OAA_ROOT.exists():
        return []
    return sorted(OAA_ROOT.rglob("*.audit.yaml"))


AUDIT_FILES = _find_audit_files()


def test_audit_schema_file_exists():
    """The JSON Schema itself must be present — it's a required framework artifact."""
    assert SCHEMA_PATH.exists(), (
        f"audit-schema.json not found at {SCHEMA_PATH}. "
        "This file is required by VERI-02."
    )


def test_audit_schema_is_valid_json():
    """The schema must be parseable JSON."""
    schema = _load_schema()
    assert isinstance(schema, dict)
    assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", (
        "Schema must declare Draft 2020-12"
    )


def test_audit_schema_has_required_top_level_properties():
    """Schema must require proto, message, and confidence — the minimum valid audit file."""
    schema = _load_schema()
    required = schema.get("required", [])
    for field in ("proto", "message", "confidence"):
        assert field in required, (
            f"audit-schema.json must require '{field}' at top level"
        )


def test_audit_schema_allows_empty_evidence_list():
    """An Unverified audit file with evidence: [] must pass schema validation."""
    schema = _load_schema()
    minimal_unverified = {
        "proto": "oaa/sensor/NightModeData.proto",
        "message": "NightMode",
        "confidence": "unverified",
        "evidence": [],
    }
    # Should not raise
    jsonschema.validate(minimal_unverified, schema)


def test_audit_schema_validates_bronze_entry():
    """A Bronze audit file with one apk_static evidence entry must pass schema validation."""
    schema = _load_schema()
    bronze = {
        "proto": "oaa/sensor/NightModeData.proto",
        "message": "NightMode",
        "confidence": "bronze",
        "evidence": [
            {
                "type": "apk_static",
                "method": "bfs_trace",
                "source": "APK 16.1 (jadx: wbo.java field 10 -> NightMode)",
                "date": "2026-02-28",
                "description": (
                    "Field 10 of SensorEventIndication maps to NightMode message "
                    "via BFS trace through obfuscated class wbo"
                ),
            }
        ],
    }
    jsonschema.validate(bronze, schema)


def test_audit_schema_validates_silver_entry():
    """A Silver audit file with apk_static + dhu_observation must pass schema validation."""
    schema = _load_schema()
    silver = {
        "proto": "oaa/sensor/NightModeData.proto",
        "message": "NightMode",
        "confidence": "silver",
        "evidence": [
            {
                "type": "apk_static",
                "method": "bfs_trace",
                "source": "APK 16.1 (jadx: wbo.java field 10 -> NightMode)",
                "date": "2026-02-28",
                "description": "Field 10 maps to NightMode via BFS trace through wbo",
            },
            {
                "type": "dhu_observation",
                "method": "logcat_trace",
                "source": "DHU 2.1 kitchen_sink.ini, logcat tag CAR.SENSOR.LITE",
                "date": "2026-02-28",
                "description": (
                    "Injected night_mode=true via DHU CLI. "
                    "Pipeline traced: CAR.SENSOR.LITE -> updateDayNightMode"
                ),
            },
        ],
    }
    jsonschema.validate(silver, schema)


def test_audit_schema_rejects_unknown_confidence_value():
    """A confidence value not in {unverified, bronze, silver, gold} must fail validation."""
    schema = _load_schema()
    bad = {
        "proto": "oaa/sensor/NightModeData.proto",
        "message": "NightMode",
        "confidence": "platinum",
        "evidence": [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_audit_schema_rejects_unknown_evidence_type():
    """An evidence type not in the allowed set must fail validation."""
    schema = _load_schema()
    bad = {
        "proto": "oaa/sensor/NightModeData.proto",
        "message": "NightMode",
        "confidence": "bronze",
        "evidence": [
            {
                "type": "blog_post",
                "source": "some blog",
                "date": "2026-02-28",
                "description": "Found it on a blog",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_audit_schema_rejects_proto_outside_oaa_directory():
    """A proto path that does not start with oaa/ must fail schema validation."""
    schema = _load_schema()
    bad = {
        "proto": "docs/sensor/NightModeData.proto",
        "message": "NightMode",
        "confidence": "unverified",
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


@pytest.mark.skipif(
    len(AUDIT_FILES) == 0,
    reason="No .audit.yaml files found under oaa/ — skipping file validation pass",
)
@pytest.mark.parametrize("audit_path", AUDIT_FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_each_audit_yaml_file_passes_schema_validation(audit_path):
    """Every .audit.yaml file under oaa/ must validate against audit-schema.json."""
    schema = _load_schema()
    with open(audit_path) as fh:
        content = yaml.safe_load(fh)

    assert content is not None, f"{audit_path} is empty or unparseable"
    assert isinstance(content, dict), (
        f"{audit_path} must be a YAML mapping at the top level"
    )

    try:
        jsonschema.validate(content, schema)
    except jsonschema.ValidationError as exc:
        pytest.fail(
            f"{audit_path.relative_to(REPO_ROOT)} failed schema validation:\n"
            f"  Path: {list(exc.absolute_path)}\n"
            f"  Message: {exc.message}"
        )
