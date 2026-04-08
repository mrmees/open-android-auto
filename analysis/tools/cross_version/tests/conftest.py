"""Shared fixtures for cross_version tool tests."""
from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest
import yaml

from analysis.tools.proto_schema_validator.models import FieldDef, ProtoMapping


@pytest.fixture
def mock_db_v1(tmp_path: Path) -> Path:
    """Create a temporary SQLite DB mimicking APK index v1 (older version)."""
    db_path = tmp_path / "v1.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE proto_fields (
            class_name TEXT,
            field_number INTEGER,
            name TEXT DEFAULT '',
            base_type TEXT,
            is_repeated INTEGER DEFAULT 0,
            is_packed INTEGER DEFAULT 0,
            is_oneof INTEGER DEFAULT 0,
            is_map INTEGER DEFAULT 0,
            optional INTEGER DEFAULT 0,
            required INTEGER DEFAULT 0,
            oneof_index INTEGER,
            enum_closed INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE proto_classes (
            class_name TEXT PRIMARY KEY,
            field_count INTEGER DEFAULT 0,
            proto_syntax TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE enum_maps (
            enum_class TEXT,
            int_value INTEGER,
            enum_name TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE proto_enum_classes (
            class_name TEXT PRIMARY KEY,
            "values" TEXT
        )
    """)
    # Sample message class with 5 fields
    fields_v1 = [
        ("vnx", 1, "timestamp", "int64", 0, 0),
        ("vnx", 2, "value", "float", 0, 0),
        ("vnx", 3, "sensor_type", "enum", 0, 0),
        ("vnx", 4, "status", "int32", 0, 0),
        ("vnx", 5, "data", "bytes", 0, 0),
    ]
    for cls, fn, name, bt, rep, pack in fields_v1:
        conn.execute(
            "INSERT INTO proto_fields (class_name, field_number, name, base_type, is_repeated, is_packed) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (cls, fn, name, bt, rep, pack),
        )
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('vnx', 5)")

    # Second class for multi-mapping tests
    fields_v1b = [
        ("wab", 1, "id", "int32", 0, 0),
        ("wab", 2, "name", "string", 0, 0),
    ]
    for cls, fn, name, bt, rep, pack in fields_v1b:
        conn.execute(
            "INSERT INTO proto_fields (class_name, field_number, name, base_type, is_repeated, is_packed) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (cls, fn, name, bt, rep, pack),
        )
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('wab', 2)")

    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def mock_db_v2(tmp_path: Path) -> Path:
    """Create a temporary SQLite DB mimicking APK index v2 (newer version).

    Differences from v1:
    - vnx: field 6 added (FIELD_ADDED), field 5 removed (FIELD_REMOVED),
      field 3 type changed from enum to int32 (FIELD_TYPE_CHANGED)
    - wab: identical to v1 (consistent match)
    """
    db_path = tmp_path / "v2.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE proto_fields (
            class_name TEXT,
            field_number INTEGER,
            name TEXT DEFAULT '',
            base_type TEXT,
            is_repeated INTEGER DEFAULT 0,
            is_packed INTEGER DEFAULT 0,
            is_oneof INTEGER DEFAULT 0,
            is_map INTEGER DEFAULT 0,
            optional INTEGER DEFAULT 0,
            required INTEGER DEFAULT 0,
            oneof_index INTEGER,
            enum_closed INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE proto_classes (
            class_name TEXT PRIMARY KEY,
            field_count INTEGER DEFAULT 0,
            proto_syntax TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE enum_maps (
            enum_class TEXT,
            int_value INTEGER,
            enum_name TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE proto_enum_classes (
            class_name TEXT PRIMARY KEY,
            "values" TEXT
        )
    """)
    # vnx equivalent in v2 (different obfuscated name)
    fields_v2 = [
        ("voa", 1, "timestamp", "int64", 0, 0),
        ("voa", 2, "value", "float", 0, 0),
        ("voa", 3, "sensor_type", "int32", 0, 0),  # TYPE CHANGED: enum -> int32
        ("voa", 4, "status", "int32", 0, 0),
        # field 5 removed
        ("voa", 6, "extra", "string", 0, 0),        # NEW FIELD
    ]
    for cls, fn, name, bt, rep, pack in fields_v2:
        conn.execute(
            "INSERT INTO proto_fields (class_name, field_number, name, base_type, is_repeated, is_packed) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (cls, fn, name, bt, rep, pack),
        )
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('voa', 5)")

    # wab equivalent in v2 -- identical fields (consistent match)
    fields_v2b = [
        ("wbc", 1, "id", "int32", 0, 0),
        ("wbc", 2, "name", "string", 0, 0),
    ]
    for cls, fn, name, bt, rep, pack in fields_v2b:
        conn.execute(
            "INSERT INTO proto_fields (class_name, field_number, name, base_type, is_repeated, is_packed) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (cls, fn, name, bt, rep, pack),
        )
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('wbc', 2)")

    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def sample_mappings() -> list[ProtoMapping]:
    """Return a small set of ProtoMapping objects for testing."""
    return [
        ProtoMapping(
            proto_message="SensorData",
            proto_file="oaa/sensor/SensorData.proto",
            proto_fqn="oaa.sensor.SensorData",
            apk_classes={"15.9": "vnx", "16.1": "vnx", "16.2": "voa"},
            confidence="bronze",
        ),
        ProtoMapping(
            proto_message="SimpleMessage",
            proto_file="oaa/common/SimpleMessage.proto",
            proto_fqn="oaa.common.SimpleMessage",
            apk_classes={"15.9": "wab", "16.1": "wab", "16.2": "wbc"},
            confidence="bronze",
        ),
    ]


def _create_mock_schema(conn: sqlite3.Connection, with_proto_enum_classes: bool = True) -> None:
    """Create the canonical mock APK-index schema on a sqlite connection."""
    conn.execute("""
        CREATE TABLE proto_fields (
            class_name TEXT,
            field_number INTEGER,
            name TEXT DEFAULT '',
            base_type TEXT,
            is_repeated INTEGER DEFAULT 0,
            is_packed INTEGER DEFAULT 0,
            is_oneof INTEGER DEFAULT 0,
            is_map INTEGER DEFAULT 0,
            optional INTEGER DEFAULT 0,
            required INTEGER DEFAULT 0,
            oneof_index INTEGER,
            enum_closed INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE proto_classes (
            class_name TEXT PRIMARY KEY,
            field_count INTEGER DEFAULT 0,
            proto_syntax TEXT,
            sub_message_refs TEXT DEFAULT '[]'
        )
    """)
    conn.execute("""
        CREATE TABLE enum_maps (
            enum_class TEXT,
            int_value INTEGER,
            enum_name TEXT
        )
    """)
    if with_proto_enum_classes:
        conn.execute("""
            CREATE TABLE proto_enum_classes (
                class_name TEXT PRIMARY KEY,
                "values" TEXT
            )
        """)


@pytest.fixture
def mock_db_v3(tmp_path: Path) -> Path:
    """Mock 16.2-equivalent APK index DB for 4-version pairwise tests.

    Contains:
    - SensorData-equivalent class 'vob' with same 5-field shape as mock_db_v2's voa.
    - SimpleMessage-equivalent class 'wbd' with same 2-field shape as mock_db_v2's wbc.
    """
    db_path = tmp_path / "v3.db"
    conn = sqlite3.connect(str(db_path))
    _create_mock_schema(conn, with_proto_enum_classes=False)

    # SensorData in 16.2-equivalent: same fields as mock_db_v2.voa but under class 'vob'
    fields_v3 = [
        ("vob", 1, "timestamp", "int64", 0, 0),
        ("vob", 2, "value", "float", 0, 0),
        ("vob", 3, "sensor_type", "int32", 0, 0),
        ("vob", 4, "status", "int32", 0, 0),
        ("vob", 6, "extra", "string", 0, 0),
    ]
    for cls, fn, name, bt, rep, pack in fields_v3:
        conn.execute(
            "INSERT INTO proto_fields (class_name, field_number, name, base_type, is_repeated, is_packed) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (cls, fn, name, bt, rep, pack),
        )
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('vob', 5)")

    # SimpleMessage in 16.2-equivalent: identical to mock_db_v2
    fields_v3b = [
        ("wbd", 1, "id", "int32", 0, 0),
        ("wbd", 2, "name", "string", 0, 0),
    ]
    for cls, fn, name, bt, rep, pack in fields_v3b:
        conn.execute(
            "INSERT INTO proto_fields (class_name, field_number, name, base_type, is_repeated, is_packed) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (cls, fn, name, bt, rep, pack),
        )
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('wbd', 2)")

    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def mock_db_v4(tmp_path: Path) -> Path:
    """Mock 16.4-equivalent APK index DB for 4-version pairwise tests.

    Includes proto_enum_classes table (the real 16.4 DB has it; 16.1 / 16.2 do not).
    Contains:
    - SensorData-equivalent class 'wqs' with same 5-field shape as mock_db_v3's vob.
    - SimpleMessage-equivalent class 'wwb' with same 2-field shape as mock_db_v3's wbd.
    """
    db_path = tmp_path / "v4.db"
    conn = sqlite3.connect(str(db_path))
    _create_mock_schema(conn, with_proto_enum_classes=True)

    fields_v4 = [
        ("wqs", 1, "timestamp", "int64", 0, 0),
        ("wqs", 2, "value", "float", 0, 0),
        ("wqs", 3, "sensor_type", "int32", 0, 0),
        ("wqs", 4, "status", "int32", 0, 0),
        ("wqs", 6, "extra", "string", 0, 0),
    ]
    for cls, fn, name, bt, rep, pack in fields_v4:
        conn.execute(
            "INSERT INTO proto_fields (class_name, field_number, name, base_type, is_repeated, is_packed) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (cls, fn, name, bt, rep, pack),
        )
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('wqs', 5)")

    fields_v4b = [
        ("wwb", 1, "id", "int32", 0, 0),
        ("wwb", 2, "name", "string", 0, 0),
    ]
    for cls, fn, name, bt, rep, pack in fields_v4b:
        conn.execute(
            "INSERT INTO proto_fields (class_name, field_number, name, base_type, is_repeated, is_packed) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (cls, fn, name, bt, rep, pack),
        )
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('wwb', 2)")

    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def sample_mappings_4v(sample_mappings: list[ProtoMapping]) -> list[ProtoMapping]:
    """sample_mappings extended with '16.2' and '16.4' keys for 4-version pairwise tests.

    Note: the existing sample_mappings fixture uses version keys '15.9' / '16.1' / '16.2',
    but the 4-version tests pass db_paths keyed as '15.9' / '16.1' / '16.2' / '16.4'.
    This fixture mutates in place so that:
    - 15.9 -> existing 15.9 value
    - 16.1 -> existing 16.1 value
    - 16.2 -> maps to the mock_db_v3 class (vob / wbd)
    - 16.4 -> maps to the mock_db_v4 class (wqs / wwb)
    """
    # SensorData
    if sample_mappings[0].proto_message == "SensorData":
        sample_mappings[0].apk_classes["16.2"] = "vob"
        sample_mappings[0].apk_classes["16.4"] = "wqs"
    # SimpleMessage
    if sample_mappings[1].proto_message == "SimpleMessage":
        sample_mappings[1].apk_classes["16.2"] = "wbd"
        sample_mappings[1].apk_classes["16.4"] = "wwb"
    return sample_mappings


@pytest.fixture
def tmp_sidecar(tmp_path: Path) -> Path:
    """Create a temporary bronze-tier audit YAML sidecar."""
    sidecar = tmp_path / "oaa" / "sensor" / "SensorData.audit.yaml"
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    audit_data = {
        "proto": "oaa/sensor/SensorData.proto",
        "message": "SensorData",
        "confidence": "bronze",
        "last_updated": "2026-03-01",
        "evidence": [
            {
                "type": "apk_static",
                "method": "string_const",
                "source": "class_mapping.yaml (v15.9:vnx, v16.1:vnx, v16.2:voa)",
                "date": "2026-03-01",
                "description": "Mapped SensorData to obfuscated APK class(es) via string_const analysis.",
            }
        ],
    }
    with open(sidecar, "w") as f:
        yaml.dump(audit_data, f, default_flow_style=False, sort_keys=False)
    return sidecar
