"""Load class mappings and query APK DB / compiled descriptors."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml
from google.protobuf import descriptor_pool

from analysis.tools.proto_schema_validator.models import FieldDef, ProtoMapping
from analysis.tools.proto_stream_validator.descriptors import (
    DescriptorBundle,
    build_descriptor_bundle,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_MAPPING_FILE = Path(__file__).resolve().parent / "class_mapping.yaml"


def load_mapping(path: Path | None = None) -> list[ProtoMapping]:
    """Load class_mapping.yaml into ProtoMapping objects."""
    path = path or _MAPPING_FILE
    with open(path) as f:
        data = yaml.safe_load(f)

    mappings = []
    for entry in data.get("mappings", []):
        apk = entry.get("apk_classes", {})
        mappings.append(ProtoMapping(
            proto_message=entry["proto_message"],
            proto_file=entry["proto_file"],
            proto_fqn=entry.get("proto_fqn", ""),
            apk_classes={str(k): v for k, v in apk.items()},
            confidence=entry.get("confidence", ""),
        ))
    return mappings


def get_apk_fields(db_path: Path, class_name: str) -> list[FieldDef]:
    """Query proto_fields table for all fields of an APK class."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT field_number, base_type, is_repeated, is_packed, is_oneof, "
            "is_map, optional, required, oneof_index, enum_closed "
            "FROM proto_fields WHERE class_name = ? ORDER BY field_number",
            (class_name,),
        ).fetchall()
    finally:
        conn.close()

    return [
        FieldDef(
            field_number=r["field_number"],
            base_type=r["base_type"],
            is_repeated=bool(r["is_repeated"]),
            is_packed=bool(r["is_packed"]),
            is_oneof=bool(r["is_oneof"]),
            is_map=bool(r["is_map"]),
            optional=bool(r["optional"]),
            required=bool(r["required"]),
            oneof_index=r["oneof_index"] if r["oneof_index"] is not None else None,
            enum_closed=bool(r["enum_closed"]),
        )
        for r in rows
    ]


def get_apk_syntax(db_path: Path, class_name: str) -> str | None:
    """Query proto_classes for the syntax of an APK class."""
    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT proto_syntax FROM proto_classes WHERE class_name = ?",
            (class_name,),
        ).fetchone()
    finally:
        conn.close()
    return row[0] if row else None


def get_our_syntax(proto_file: str) -> str:
    """Parse syntax= line from a .proto file."""
    full = _REPO_ROOT / proto_file
    if not full.exists():
        return "unknown"
    for line in full.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("syntax"):
            if "proto2" in stripped:
                return "proto2"
            if "proto3" in stripped:
                return "proto3"
    return "unknown"


def _descriptor_field_to_fielddef(fd) -> FieldDef:
    """Convert a google.protobuf FieldDescriptor to our FieldDef."""
    # Field type name mapping from protobuf's TYPE_* constants
    _TYPE_NAMES = {
        1: "double", 2: "float", 3: "int64", 4: "uint64",
        5: "int32", 6: "fixed64", 7: "fixed32", 8: "bool",
        9: "string", 10: "group", 11: "message", 12: "bytes",
        13: "uint32", 14: "enum", 15: "sfixed32", 16: "sfixed64",
        17: "sint32", 18: "sint64",
    }
    base_type = _TYPE_NAMES.get(fd.type, f"unknown_{fd.type}")

    is_repeated = fd.is_repeated
    required = fd.is_required if hasattr(fd, "is_required") else False
    is_packed = fd.is_packed if hasattr(fd, "is_packed") else False

    # Check for oneof
    is_oneof = fd.containing_oneof is not None
    oneof_index = None
    if is_oneof:
        oneof_index = fd.containing_oneof.index

    # Check for map (map fields are repeated message with map_entry option)
    is_map = False
    if base_type == "message" and is_repeated and fd.message_type:
        if fd.message_type.GetOptions().map_entry:
            is_map = True

    # has_presence indicates optional-like semantics (proto3 optional, oneof, proto2)
    has_presence = fd.has_presence if hasattr(fd, "has_presence") else False
    optional = has_presence and not is_oneof and not required

    return FieldDef(
        field_number=fd.number,
        base_type=base_type,
        is_repeated=is_repeated,
        is_packed=is_packed,
        is_oneof=is_oneof,
        is_map=is_map,
        optional=optional,
        required=required,
        oneof_index=oneof_index,
        name=fd.name,
    )


def get_proto_fields_from_descriptor(
    pool: descriptor_pool.DescriptorPool, message_fqn: str
) -> list[FieldDef]:
    """Introspect a compiled descriptor pool for fields of a message."""
    desc = pool.FindMessageTypeByName(message_fqn)
    return sorted(
        [_descriptor_field_to_fielddef(fd) for fd in desc.fields],
        key=lambda f: f.field_number,
    )


_bundle_cache: dict[str, DescriptorBundle] = {}


def get_or_build_bundle() -> DescriptorBundle:
    """Build (or return cached) descriptor bundle for oaa/ protos."""
    key = str(_REPO_ROOT)
    if key not in _bundle_cache:
        tmpdir = TemporaryDirectory(prefix="proto_schema_val_")
        _bundle_cache[key] = build_descriptor_bundle(_REPO_ROOT, Path(tmpdir.name))
    return _bundle_cache[key]


def get_all_apk_classes(db_path: Path) -> dict[str, str | None]:
    """Get all class_name -> proto_syntax from proto_classes table."""
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            "SELECT class_name, proto_syntax FROM proto_classes"
        ).fetchall()
    finally:
        conn.close()
    return {r[0]: r[1] for r in rows}
