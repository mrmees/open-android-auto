"""Shared data structures for proto schema validation."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueKind(Enum):
    MISSING_FIELD = "missing_field"
    EXTRA_FIELD = "extra_field"
    TYPE_MISMATCH = "type_mismatch"
    MODIFIER_MISMATCH = "modifier_mismatch"
    SYNTAX_MISMATCH = "syntax_mismatch"
    PARSE_FAILURE = "parse_failure"
    UNKNOWN_WIRE_FIELD = "unknown_wire_field"
    FIELD_NEVER_SEEN = "field_never_seen"
    FIELD_ADDED = "field_added"
    FIELD_REMOVED = "field_removed"
    FIELD_TYPE_CHANGED = "field_type_changed"
    STRUCTURAL_MATCH = "structural_match"


@dataclass(frozen=True)
class FieldDef:
    """A single proto field definition from either our schema or the APK DB."""
    field_number: int
    base_type: str
    is_repeated: bool = False
    is_packed: bool = False
    is_oneof: bool = False
    is_map: bool = False
    optional: bool = False
    required: bool = False
    oneof_index: int | None = None
    enum_closed: bool = False
    name: str = ""


@dataclass
class ProtoMapping:
    """Maps one of our proto messages to APK obfuscated class(es)."""
    proto_message: str
    proto_file: str
    proto_fqn: str = ""
    apk_classes: dict[str, str | None] = field(default_factory=dict)
    confidence: str = ""


@dataclass(frozen=True)
class SchemaIssue:
    """Layer 1: discrepancy between our schema and APK DB."""
    proto_message: str
    kind: IssueKind
    severity: Severity
    field_number: int | None = None
    detail: str = ""


@dataclass(frozen=True)
class WireIssue:
    """Layer 2: discrepancy found in wire capture data."""
    proto_message: str
    kind: IssueKind
    severity: Severity
    field_number: int | None = None
    frame_index: int | None = None
    detail: str = ""


@dataclass(frozen=True)
class DriftIssue:
    """Layer 3: structural change between APK versions."""
    apk_class_v1: str
    apk_class_v2: str | None
    kind: IssueKind
    severity: Severity
    field_number: int | None = None
    detail: str = ""


# Wire type compatibility groups — mismatches within a group are warnings,
# across groups are errors.
WIRE_TYPE_GROUPS: dict[str, int] = {
    # Varint (wire type 0)
    "int32": 0, "int64": 0, "uint32": 0, "uint64": 0,
    "sint32": 0, "sint64": 0, "bool": 0, "enum": 0,
    # 64-bit (wire type 1)
    "fixed64": 1, "sfixed64": 1, "double": 1,
    # Length-delimited (wire type 2)
    "string": 2, "bytes": 2, "message": 2,
    # 32-bit (wire type 5)
    "fixed32": 5, "sfixed32": 5, "float": 5,
    # Group (wire type 3/4) — legacy, unlikely
    "group": 3,
}
