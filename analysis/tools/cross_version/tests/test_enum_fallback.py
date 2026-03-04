"""Unit tests for the enum-class comparison fallback in compare.py.

Gap 4 (TOOL-02): compare.py converts enum values to synthetic FieldDef entries when
proto_fields is empty. This is documented in 03-01-SUMMARY as a key deviation.
These tests exercise the _get_fields_or_enum fallback path directly.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from analysis.tools.cross_version.compare import _get_fields_or_enum, run_comparison
from analysis.tools.proto_schema_validator.models import IssueKind, ProtoMapping


@pytest.fixture
def db_with_enum_only(tmp_path: Path) -> Path:
    """DB where a class has no proto_fields rows but has enum values in proto_enum_classes."""
    db_path = tmp_path / "enum_db.db"
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
    # Register enum class with no proto_fields rows
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('exa', 0)")
    # Insert enum values into enum_maps (used by get_apk_enum_values)
    conn.executemany(
        "INSERT INTO enum_maps (enum_class, int_value, enum_name) VALUES (?, ?, ?)",
        [("exa", 0, "UNKNOWN"), ("exa", 1, "VALUE_A"), ("exa", 2, "VALUE_B")],
    )
    conn.execute(
        "INSERT INTO proto_enum_classes (class_name, \"values\") VALUES (?, ?)",
        ("exa", '{"0": "UNKNOWN", "1": "VALUE_A", "2": "VALUE_B"}'),
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def db_with_message_fields(tmp_path: Path) -> Path:
    """DB where a class has regular proto_fields rows (non-enum message)."""
    db_path = tmp_path / "msg_db.db"
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
    conn.executemany(
        "INSERT INTO proto_fields (class_name, field_number, name, base_type, is_repeated, is_packed) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [("mxa", 1, "id", "int32", 0, 0), ("mxa", 2, "name", "string", 0, 0)],
    )
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('mxa', 2)")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def db_missing_enum_table(tmp_path: Path) -> Path:
    """DB without proto_enum_classes table (simulates 16.1 schema gap from 03-02-SUMMARY)."""
    db_path = tmp_path / "no_enum_table.db"
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
    # Intentionally NO proto_enum_classes table
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('exa', 0)")
    conn.commit()
    conn.close()
    return db_path


def test_enum_fallback_returns_synthetic_fields(db_with_enum_only: Path):
    """When proto_fields is empty, fallback returns synthetic FieldDef entries from enum values."""
    fields = _get_fields_or_enum(db_with_enum_only, "exa")
    assert len(fields) == 3, (
        f"Expected 3 synthetic fields from enum values, got {len(fields)}"
    )
    field_numbers = {f.field_number for f in fields}
    assert field_numbers == {0, 1, 2}, (
        f"Expected field numbers 0/1/2 from enum int values, got {field_numbers}"
    )


def test_enum_fallback_uses_enum_value_as_base_type(db_with_enum_only: Path):
    """Synthetic FieldDef entries must have base_type='enum_value' per compare.py contract."""
    fields = _get_fields_or_enum(db_with_enum_only, "exa")
    assert all(f.base_type == "enum_value" for f in fields), (
        f"All synthetic fields should have base_type='enum_value', "
        f"got: {[f.base_type for f in fields]}"
    )


def test_message_class_uses_proto_fields_not_enum(db_with_message_fields: Path):
    """When proto_fields has rows, those are returned directly (no enum fallback)."""
    fields = _get_fields_or_enum(db_with_message_fields, "mxa")
    assert len(fields) == 2
    types = {f.base_type for f in fields}
    assert "int32" in types or "string" in types, (
        "Expected real proto field types (int32, string), not enum_value"
    )
    assert "enum_value" not in types


def test_enum_fallback_returns_empty_for_unknown_class(db_with_enum_only: Path):
    """When class has no fields and no enum values, fallback returns empty list."""
    fields = _get_fields_or_enum(db_with_enum_only, "nonexistent_class")
    assert fields == [], (
        f"Expected empty list for unknown class, got {fields}"
    )


def test_enum_fallback_graceful_when_table_missing(db_missing_enum_table: Path):
    """When proto_enum_classes table is absent (16.1 schema gap), returns empty list gracefully."""
    # Should not raise sqlite3.OperationalError -- the fix in mapping.py handles this
    fields = _get_fields_or_enum(db_missing_enum_table, "exa")
    assert isinstance(fields, list), (
        "Should return a list even when proto_enum_classes table is missing"
    )
    assert fields == [], (
        f"Expected empty list when table is missing, got {fields}"
    )


def test_enum_comparison_via_run_comparison_detects_addition(
    db_with_enum_only: Path, tmp_path: Path
):
    """Two enum-only DBs with different values: run_comparison detects the added value."""
    # Create a second DB with an extra enum value
    db2_path = tmp_path / "enum_db2.db"
    conn = sqlite3.connect(str(db2_path))
    conn.execute("""
        CREATE TABLE proto_fields (
            class_name TEXT, field_number INTEGER, name TEXT DEFAULT '',
            base_type TEXT, is_repeated INTEGER DEFAULT 0, is_packed INTEGER DEFAULT 0,
            is_oneof INTEGER DEFAULT 0, is_map INTEGER DEFAULT 0,
            optional INTEGER DEFAULT 0, required INTEGER DEFAULT 0,
            oneof_index INTEGER, enum_closed INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE proto_classes (class_name TEXT PRIMARY KEY, field_count INTEGER DEFAULT 0, proto_syntax TEXT)
    """)
    conn.execute("CREATE TABLE enum_maps (enum_class TEXT, int_value INTEGER, enum_name TEXT)")
    conn.execute("""CREATE TABLE proto_enum_classes (class_name TEXT PRIMARY KEY, "values" TEXT)""")
    conn.execute("INSERT INTO proto_classes (class_name, field_count) VALUES ('exa', 0)")
    conn.executemany(
        "INSERT INTO enum_maps (enum_class, int_value, enum_name) VALUES (?, ?, ?)",
        [
            ("exa", 0, "UNKNOWN"),
            ("exa", 1, "VALUE_A"),
            ("exa", 2, "VALUE_B"),
            ("exa", 3, "VALUE_C"),  # New enum value in v2
        ],
    )
    conn.execute(
        "INSERT INTO proto_enum_classes (class_name, \"values\") VALUES (?, ?)",
        ("exa", '{"0": "UNKNOWN", "1": "VALUE_A", "2": "VALUE_B", "3": "VALUE_C"}'),
    )
    conn.commit()
    conn.close()

    mappings = [
        ProtoMapping(
            proto_message="SomeEnum",
            proto_file="oaa/sensor/SomeEnum.proto",
            apk_classes={"v1": "exa", "v2": "exa"},
        )
    ]
    results = run_comparison(
        db_paths={"v1": db_with_enum_only, "v2": db2_path},
        mappings=mappings,
    )
    assert len(results) == 1
    r = results[0]
    added = [i for i in r.issues if i.kind == IssueKind.FIELD_ADDED]
    assert len(added) >= 1, (
        f"Expected FIELD_ADDED for new enum value 3, issues were: {r.issues}"
    )
    assert added[0].field_number == 3
