"""Audit YAML generation and validation logic."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from analysis.tools.proto_schema_validator.models import ProtoMapping

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCHEMA_PATH = _REPO_ROOT / "docs" / "verification" / "audit-schema.json"

# Confidence label -> method tag mapping
_METHOD_TAGS: dict[str, str] = {
    "proto_comment": "string_const",
    "triage_investigation": "bfs_trace",
    "collision_resolved": "enum_match",
    "apk_protos_json": "proto_access",
    "jadx_message_dispatch": "call_graph",
    "apk_protos_json_collision_12": "enum_match",
}


def make_evidence_entry(mapping: ProtoMapping, method_tag: str) -> dict[str, Any]:
    """Create an evidence_entry dict conforming to the audit schema.

    All seed mappings come from APK static analysis, so type is always apk_static.
    """
    # Build source string from APK class mappings
    versions = []
    for ver, cls in sorted(mapping.apk_classes.items()):
        if cls is not None:
            versions.append(f"v{ver}:{cls}")
    source = f"class_mapping.yaml ({', '.join(versions)})" if versions else "class_mapping.yaml"

    return {
        "type": "apk_static",
        "method": method_tag,
        "source": source,
        "date": date.today().isoformat(),
        "description": (
            f"Mapped {mapping.proto_message} to obfuscated APK class(es) "
            f"via {method_tag} analysis."
        ),
    }


def compute_tier(evidence: list[dict[str, Any]]) -> str:
    """Compute confidence tier from evidence list.

    - empty -> unverified
    - 1+ entries -> bronze
    - 2+ distinct types -> silver
    - any oem_capture -> gold
    """
    if not evidence:
        return "unverified"

    types = {e["type"] for e in evidence}

    if "oem_capture" in types:
        return "gold"
    if len(types) >= 2:
        return "silver"
    return "bronze"


def generate_audit_yaml(
    proto_path: str,
    message_name: str,
    confidence: str,
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate an audit YAML document conforming to the schema.

    Args:
        proto_path: Relative path to .proto file from repo root (e.g. oaa/sensor/Foo.proto)
        message_name: Primary message name
        confidence: Confidence tier string
        evidence: List of evidence_entry dicts

    Returns:
        Audit data dict ready for YAML serialization.
    """
    audit: dict[str, Any] = {
        "proto": proto_path,
        "message": message_name,
        "confidence": confidence,
        "last_updated": date.today().isoformat(),
        "evidence": evidence,
    }
    return audit


def validate_audit(
    audit_data: dict[str, Any],
    schema_path: Path | None = None,
) -> bool:
    """Validate audit data against the JSON schema.

    Returns True if valid. Raises jsonschema.ValidationError if invalid.
    """
    schema_path = schema_path or _SCHEMA_PATH
    with open(schema_path) as f:
        schema = json.load(f)

    jsonschema.validate(audit_data, schema)
    return True


def write_audit_yaml(audit_data: dict[str, Any], output_path: Path) -> None:
    """Write audit data as YAML to the given path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(
            audit_data,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )


def sidecar_path(proto_path: str) -> Path:
    """Compute sidecar path: oaa/sensor/Foo.proto -> oaa/sensor/Foo.audit.yaml"""
    p = Path(proto_path)
    return p.with_suffix("").with_suffix(".audit.yaml")
