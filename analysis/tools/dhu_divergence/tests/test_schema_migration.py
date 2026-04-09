"""Schema migration unit tests (Phase 9 Plan 01 TIER-01/02/03).

Each test builds a synthetic sidecar dict in-memory and calls jsonschema.validate
against the migrated schema. PASS means no exception raised; FAIL means a
ValidationError is raised when expected.
"""
from __future__ import annotations

import copy

import jsonschema
import pytest


BASE_VALID_PLATINUM: dict = {
    "proto": "oaa/_test/_TestProto.proto",
    "message": "TestMessage",
    "confidence": "platinum",
    "platinum_scope": "single_oem",
    "last_updated": "2026-04-09",
    "evidence": [
        {
            "type": "apk_static",
            "method": "proto_access",
            "source": "test fixture",
            "date": "2026-04-09",
            "description": "Test evidence",
        },
        {
            "type": "cross_version",
            "method": "structural_comparison",
            "source": "test fixture",
            "date": "2026-04-09",
            "description": "Test cross-version evidence",
        },
        {
            "type": "platinum_evidence",
            "source": "captures/oem-vw-mib3oi-2026-04-06/messages.jsonl",
            "date": "2026-04-09",
            "description": "Test platinum evidence",
            "capture_path": "captures/oem-vw-mib3oi-2026-04-06/",
            "vehicle_metadata": {
                "make": "Volkswagen",
                "model": "MIB3 OI",
                "year": "2024",
                "aa_version": "16.4.661034",
            },
            "msg_seq": [1],
            "ts_ms": [1000],
            "message_completeness": "full",
            "attribution_method": "sdp_service_id",
            "oem_scope": "single",
            "applicability": "fields",
            "fields": [1],
            "match_rules": ["MATCH-01"],
        },
    ],
}


def test_platinum_evidence_valid(schema: dict) -> None:
    """A fully populated platinum_evidence entry validates cleanly."""
    instance = copy.deepcopy(BASE_VALID_PLATINUM)
    jsonschema.validate(instance, schema)


def test_platinum_evidence_missing_match_rules(schema: dict) -> None:
    """platinum_evidence without match_rules is rejected (required by if/then)."""
    instance = copy.deepcopy(BASE_VALID_PLATINUM)
    del instance["evidence"][2]["match_rules"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_applicability_fields_requires_list(schema: dict) -> None:
    """applicability=fields without a fields list is rejected (conditional required)."""
    instance = copy.deepcopy(BASE_VALID_PLATINUM)
    instance["evidence"][2]["applicability"] = "fields"
    del instance["evidence"][2]["fields"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_platinum_single_oem_valid(schema: dict) -> None:
    """platinum_scope: single_oem is a valid value."""
    instance = copy.deepcopy(BASE_VALID_PLATINUM)
    instance["platinum_scope"] = "single_oem"
    jsonschema.validate(instance, schema)


def test_platinum_requires_scope(schema: dict) -> None:
    """confidence=platinum without platinum_scope is rejected (top-level allOf)."""
    instance = copy.deepcopy(BASE_VALID_PLATINUM)
    del instance["platinum_scope"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_platinum_multi_oem_valid(schema: dict) -> None:
    """platinum_scope: multi_oem is representable (v2 reserved value)."""
    instance = copy.deepcopy(BASE_VALID_PLATINUM)
    instance["platinum_scope"] = "multi_oem"
    jsonschema.validate(instance, schema)


def test_match_rules_rejects_unknown(schema: dict) -> None:
    """Unknown rule IDs are rejected (closed-enum items)."""
    instance = copy.deepcopy(BASE_VALID_PLATINUM)
    instance["evidence"][2]["match_rules"] = ["MATCH-99"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_match_rules_rejects_duplicates(schema: dict) -> None:
    """Duplicate rule IDs are rejected (uniqueItems)."""
    instance = copy.deepcopy(BASE_VALID_PLATINUM)
    instance["evidence"][2]["match_rules"] = ["MATCH-01", "MATCH-01"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_match_rules_rejects_empty(schema: dict) -> None:
    """Empty match_rules list is rejected (minItems: 1)."""
    instance = copy.deepcopy(BASE_VALID_PLATINUM)
    instance["evidence"][2]["match_rules"] = []
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)
