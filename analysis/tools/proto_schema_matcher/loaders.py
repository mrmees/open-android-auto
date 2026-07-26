from __future__ import annotations

import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from google.protobuf import descriptor_pb2

from analysis.tools.apk_indexer.extract import extract_signals
from analysis.tools.proto_stream_validator.descriptors import build_descriptor_bundle

from .models import EnumNode, FieldShape, MessageNode


_TYPE_NAMES = {
    1: "double",
    2: "float",
    3: "int64",
    4: "uint64",
    5: "int32",
    6: "fixed64",
    7: "fixed32",
    8: "bool",
    9: "string",
    10: "group",
    11: "message",
    12: "bytes",
    13: "uint32",
    14: "enum",
    15: "sfixed32",
    16: "sfixed64",
    17: "sint32",
    18: "sint64",
}


def _walk_messages(prefix: str, messages):
    for message in messages:
        full_name = f"{prefix}.{message.name}" if prefix else message.name
        yield full_name, message
        yield from _walk_messages(full_name, message.nested_type)


def _load_canonical_descriptor_set(repo_root: Path):
    with TemporaryDirectory(prefix="proto_schema_matcher_") as tmp:
        bundle = build_descriptor_bundle(repo_root, Path(tmp))
        file_set = descriptor_pb2.FileDescriptorSet()
        file_set.ParseFromString(bundle.descriptor_set_path.read_bytes())
    return file_set


def _retracted_proto_files(repo_root: Path) -> set[str]:
    retracted = set()
    for proto_path in (repo_root / "oaa").rglob("*.proto"):
        proto_text = proto_path.read_text(errors="ignore")
        audit_path = proto_path.with_suffix(".audit.yaml")
        audit_text = audit_path.read_text(errors="ignore") if audit_path.exists() else ""
        if re.search(r"^//\s*confidence:\s*retracted\b", proto_text, re.MULTILINE) or re.search(
            r"^confidence:\s*retracted\b", audit_text, re.MULTILINE
        ):
            retracted.add(proto_path.relative_to(repo_root).as_posix())
    return retracted


def load_canonical_schema(
    repo_root: Path,
) -> tuple[dict[str, MessageNode], dict[str, EnumNode]]:
    """Compile and normalize messages and enum numeric domains under ``oaa/``."""
    file_set = _load_canonical_descriptor_set(repo_root)
    retracted_files = _retracted_proto_files(repo_root)

    map_entries: set[str] = set()
    for file_proto in file_set.file:
        if file_proto.name in retracted_files:
            continue
        prefix = f".{file_proto.package}" if file_proto.package else ""
        for full_name, message in _walk_messages(prefix, file_proto.message_type):
            if message.options.map_entry:
                map_entries.add(full_name)

    graph: dict[str, MessageNode] = {}
    enum_graph: dict[str, EnumNode] = {}
    for file_proto in file_set.file:
        if file_proto.name in retracted_files:
            continue
        syntax = file_proto.syntax or "proto2"
        prefix = file_proto.package
        for full_name, message in _walk_messages(prefix, file_proto.message_type):
            if message.options.map_entry:
                continue

            fields: list[FieldShape] = []
            for proto_field in sorted(message.field, key=lambda item: item.number):
                is_map = (
                    proto_field.type == descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
                    and proto_field.type_name in map_entries
                )
                scalar = proto_field.type not in {
                    descriptor_pb2.FieldDescriptorProto.TYPE_STRING,
                    descriptor_pb2.FieldDescriptorProto.TYPE_GROUP,
                    descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE,
                    descriptor_pb2.FieldDescriptorProto.TYPE_BYTES,
                }
                repeated = (
                    proto_field.label == descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
                    and not is_map
                )
                if proto_field.options.HasField("packed"):
                    packed = proto_field.options.packed
                else:
                    packed = syntax == "proto3" and repeated and scalar

                fields.append(
                    FieldShape(
                        number=proto_field.number,
                        base_type="map" if is_map else _TYPE_NAMES[proto_field.type],
                        repeated=repeated,
                        packed=packed,
                        oneof=proto_field.HasField("oneof_index"),
                        map=is_map,
                        required=(
                            proto_field.label
                            == descriptor_pb2.FieldDescriptorProto.LABEL_REQUIRED
                        ),
                        target=proto_field.type_name.lstrip(".") or None,
                    )
                )

            graph[full_name] = MessageNode(
                name=full_name,
                syntax=syntax,
                fields=tuple(fields),
                source=file_proto.name,
            )
            for enum in message.enum_type:
                enum_name = f"{full_name}.{enum.name}"
                enum_graph[enum_name] = EnumNode(
                    name=enum_name,
                    values=tuple(value.number for value in enum.value),
                    source=file_proto.name,
                )
        for enum in file_proto.enum_type:
            enum_name = f"{prefix}.{enum.name}" if prefix else enum.name
            enum_graph[enum_name] = EnumNode(
                name=enum_name,
                values=tuple(value.number for value in enum.value),
                source=file_proto.name,
            )
    return graph, enum_graph


def load_canonical_graph(repo_root: Path) -> dict[str, MessageNode]:
    """Compile and normalize every non-map-entry message under ``oaa/``."""
    return load_canonical_schema(repo_root)[0]


def _data_from_json(path: Path) -> dict[str, list[dict[str, object]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"proto_classes": data, "proto_enum_classes": []}
    if isinstance(data, dict) and isinstance(data.get("proto_classes"), list):
        return {
            "proto_classes": data["proto_classes"],
            "proto_enum_classes": data.get("proto_enum_classes", []),
        }
    raise ValueError(f"expected proto class list or signals object in {path}")


_VERIFIER_INSTANCE_RE = re.compile(
    r"\b(?:public\s+)?static\s+final\s+\w+\s+(\w+)\s*=\s*new\s+(\w+)\((\d+)\)"
)
_CASE_BLOCK_RE = re.compile(
    r"case\s+(\d+)\s*:(.*?)(?=\bcase\s+\d+\s*:|\bdefault\s*:|\Z)",
    re.DOTALL,
)


def _load_verifier_enum_targets(
    jadx_root: Path,
    enum_class_names: set[str],
) -> dict[str, str]:
    """Resolve multiplexed lite enum verifiers such as ``xjj.c -> xlu``."""
    sources = jadx_root / "sources"
    targets: dict[str, str] = {}
    for path in sources.rglob("*.java"):
        text = path.read_text(errors="ignore")
        instances = {
            int(discriminator): f"{verifier_class}.{member}"
            for member, verifier_class, discriminator in _VERIFIER_INSTANCE_RE.findall(
                text
            )
            if verifier_class == path.stem
        }
        if not instances:
            continue
        for case_number, block in _CASE_BLOCK_RE.findall(text):
            referenced_enums = {
                match.group(1)
                for match in re.finditer(r"\b([a-z][a-z0-9]*)\.\w+\(", block)
                if match.group(1) in enum_class_names
            }
            key = instances.get(int(case_number))
            if key and len(referenced_enums) == 1:
                targets[key] = next(iter(referenced_enums))
    return targets


def load_apk_schema(
    *,
    jadx_root: Path | None = None,
    proto_classes_json: Path | None = None,
) -> tuple[dict[str, MessageNode], dict[str, EnumNode]]:
    """Load normalized APK message and enum nodes from JADX or index JSON."""
    if (jadx_root is None) == (proto_classes_json is None):
        raise ValueError("provide exactly one of jadx_root or proto_classes_json")

    if jadx_root is not None:
        data = extract_signals(jadx_root, scope="all")
    else:
        assert proto_classes_json is not None
        data = _data_from_json(proto_classes_json)

    rows = data["proto_classes"]
    enum_graph: dict[str, EnumNode] = {}
    for row in data.get("proto_enum_classes", []):
        raw_values = row.get("values", "[]")
        values = json.loads(raw_values) if isinstance(raw_values, str) else raw_values
        name = str(row["class_name"])
        enum_graph[name] = EnumNode(
            name=name,
            values=tuple(int(value["int_value"]) for value in values),
            source=str(row.get("file") or ""),
        )
    verifier_targets = (
        _load_verifier_enum_targets(jadx_root, set(enum_graph))
        if jadx_root is not None
        else {}
    )

    graph: dict[str, MessageNode] = {}
    for row in rows:
        syntax = str(row.get("proto_syntax") or "")
        if not syntax:
            continue
        decoded = row.get("decoded_fields", "[]")
        decoded_fields = json.loads(decoded) if isinstance(decoded, str) else decoded
        raw_references = row.get("field_references", "[]")
        field_references = (
            json.loads(raw_references)
            if isinstance(raw_references, str)
            else raw_references
        )
        targets_by_number = {}
        for item in field_references:
            target = str(item["target_class"])
            if item.get("base_type") == "enum":
                target = verifier_targets.get(str(item.get("token") or ""), target)
            targets_by_number[int(item["field_number"])] = target
        fields = tuple(
            FieldShape(
                number=int(item["field_number"]),
                base_type=str(item["base_type"]),
                repeated=bool(item["is_repeated"]),
                packed=bool(item["is_packed"]),
                oneof=bool(item["is_oneof"]),
                map=bool(item["is_map"]),
                required=bool(item["required"]),
                target=targets_by_number.get(int(item["field_number"])),
            )
            for item in decoded_fields
        )
        name = str(row["class_name"])
        graph[name] = MessageNode(
            name=name,
            syntax=syntax,
            fields=fields,
            source=str(row.get("file") or ""),
        )
    return graph, enum_graph


def load_apk_graph(
    *,
    jadx_root: Path | None = None,
    proto_classes_json: Path | None = None,
) -> dict[str, MessageNode]:
    """Load normalized APK message nodes from JADX source or index JSON."""
    return load_apk_schema(
        jadx_root=jadx_root,
        proto_classes_json=proto_classes_json,
    )[0]
