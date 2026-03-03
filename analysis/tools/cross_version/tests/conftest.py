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
