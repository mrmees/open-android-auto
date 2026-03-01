"""DB queries and seed loading for proto triage."""
from __future__ import annotations

import json
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path

from analysis.tools.proto_schema_validator.mapping import load_mapping


@dataclass(frozen=True)
class ProtoInfo:
    """Basic info about a proto class from the APK DB."""
    class_name: str
    proto_syntax: str  # "proto2", "proto3", or ""
    field_count: int
    sub_message_refs: list[str] = field(default_factory=list)


def load_seeds(mapping_path: Path | None, version: str) -> set[str]:
    """Load known wire proto class names from class_mapping.yaml."""
    mappings = load_mapping(mapping_path)
    seeds: set[str] = set()
    for m in mappings:
        cls = m.apk_classes.get(version)
        if cls:
            seeds.add(cls)
    return seeds


def load_seed_service_map(mapping_path: Path | None, version: str) -> dict[str, str]:
    """Map class_name → service label derived from proto_file path."""
    mappings = load_mapping(mapping_path)
    result: dict[str, str] = {}
    for m in mappings:
        cls = m.apk_classes.get(version)
        if not cls:
            continue
        label = _service_from_path(m.proto_file)
        result[cls] = label
    return result


def _service_from_path(proto_file: str) -> str:
    """Derive service label from proto file path."""
    parts = proto_file.lower()
    # Map path fragments to service labels
    for fragment, label in _SERVICE_FRAGMENTS:
        if fragment in parts:
            return label
    return "Unknown"


_SERVICE_FRAGMENTS: list[tuple[str, str]] = [
    ("oaa/av/", "AV"),
    ("oaa/sensor/", "Sensor"),
    ("oaa/input/", "Input"),
    ("oaa/navigation/", "Navigation"),
    ("oaa/media/", "Media"),
    ("oaa/phone/", "Phone"),
    ("oaa/notification/", "Notification"),
    ("oaa/radio/", "Radio"),
    ("oaa/car_control/", "CarControl"),
    ("oaa/control/", "Control"),
    ("oaa/ping/", "Ping"),
    ("oaa/auth/", "Auth"),
    ("oaa/generic/", "Generic"),
    ("oaa/bluetooth/", "Bluetooth"),
    ("oaa/vendor/", "Vendor"),
    ("oaa/wifi/", "WiFi"),
    ("oaa/", "OAA"),
]


def load_proto_universe(db_path: Path) -> dict[str, ProtoInfo]:
    """Load all proto classes from the APK index DB."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT class_name, proto_syntax, field_count, sub_message_refs "
            "FROM proto_classes"
        ).fetchall()
    finally:
        conn.close()

    universe: dict[str, ProtoInfo] = {}
    for r in rows:
        refs_raw = r["sub_message_refs"] or "[]"
        try:
            refs = json.loads(refs_raw)
        except (json.JSONDecodeError, TypeError):
            refs = []
        # Filter out java.lang.Object and deduplicate
        refs = list(dict.fromkeys(
            ref for ref in refs
            if ref and ref != "java.lang.Object"
        ))
        universe[r["class_name"]] = ProtoInfo(
            class_name=r["class_name"],
            proto_syntax=r["proto_syntax"] or "",
            field_count=r["field_count"] or 0,
            sub_message_refs=refs,
        )
    return universe


def load_class_references(db_path: Path) -> list[tuple[str, str, str]]:
    """Load class_references as (file, source_package, target_class) tuples."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT file, source_package, target_class FROM class_references"
        ).fetchall()
    finally:
        conn.close()
    return [(r["file"], r["source_package"], r["target_class"]) for r in rows]


def build_sub_message_graph(
    universe: dict[str, ProtoInfo],
) -> dict[str, set[str]]:
    """Build bidirectional adjacency graph from sub_message_refs.

    Returns a dict where graph[A] contains B if A embeds B OR B embeds A.
    Only includes edges where both endpoints exist in the universe.
    """
    graph: dict[str, set[str]] = {}
    for cls, info in universe.items():
        for ref in info.sub_message_refs:
            if ref not in universe:
                continue
            graph.setdefault(cls, set()).add(ref)
            graph.setdefault(ref, set()).add(cls)
    return graph


def build_file_to_classes(
    refs: list[tuple[str, str, str]],
    universe: dict[str, ProtoInfo],
) -> dict[str, set[str]]:
    """Map source file → set of proto classes referenced from that file.

    Only includes target_class values that exist in the proto universe.
    """
    file_classes: dict[str, set[str]] = {}
    for file_path, _pkg, target in refs:
        if target in universe:
            file_classes.setdefault(file_path, set()).add(target)
    return file_classes


def build_class_to_packages(
    refs: list[tuple[str, str, str]],
    universe: dict[str, ProtoInfo],
) -> dict[str, set[str]]:
    """Map proto class → set of source_packages that reference it."""
    class_pkgs: dict[str, set[str]] = {}
    for _file, pkg, target in refs:
        if target in universe:
            class_pkgs.setdefault(target, set()).add(pkg)
    return class_pkgs
