from __future__ import annotations

import json
from pathlib import Path
import sqlite3


def _create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS uuids (
            file TEXT NOT NULL,
            line INTEGER NOT NULL,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS constants (
            file TEXT NOT NULL,
            line INTEGER NOT NULL,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS proto_accesses (
            file TEXT NOT NULL,
            line INTEGER NOT NULL,
            accessor TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS proto_writes (
            file TEXT NOT NULL,
            line INTEGER NOT NULL,
            target TEXT NOT NULL,
            op TEXT NOT NULL,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS enum_maps (
            file TEXT NOT NULL,
            line INTEGER NOT NULL,
            enum_class TEXT NOT NULL,
            int_value INTEGER NOT NULL,
            enum_name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS switch_maps (
            file TEXT NOT NULL,
            line INTEGER NOT NULL,
            switch_expr TEXT NOT NULL,
            case_value TEXT NOT NULL,
            target TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS call_edges (
            file TEXT NOT NULL,
            line INTEGER NOT NULL,
            target TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_uuids_value ON uuids(value);
        CREATE INDEX IF NOT EXISTS idx_constants_value ON constants(value);
        CREATE INDEX IF NOT EXISTS idx_proto_accessor ON proto_accesses(accessor);
        CREATE INDEX IF NOT EXISTS idx_proto_writes_target ON proto_writes(target);
        CREATE INDEX IF NOT EXISTS idx_enum_maps_class ON enum_maps(enum_class);
        CREATE INDEX IF NOT EXISTS idx_switch_maps_expr ON switch_maps(switch_expr);
        CREATE INDEX IF NOT EXISTS idx_call_target ON call_edges(target);
        CREATE TABLE IF NOT EXISTS proto_classes (
            file TEXT NOT NULL,
            class_name TEXT NOT NULL,
            deprecated INTEGER NOT NULL DEFAULT 0,
            field_count INTEGER NOT NULL,
            field_names TEXT NOT NULL,
            field_types TEXT NOT NULL,
            field_decls TEXT NOT NULL,
            sub_message_refs TEXT NOT NULL,
            descriptor TEXT NOT NULL,
            proto_syntax TEXT NOT NULL DEFAULT '',
            decoded_fields TEXT NOT NULL DEFAULT '[]'
        );
        CREATE TABLE IF NOT EXISTS proto_fields (
            class_name TEXT NOT NULL,
            field_number INTEGER NOT NULL,
            type_label TEXT NOT NULL,
            base_type TEXT NOT NULL,
            type_id INTEGER NOT NULL,
            is_repeated INTEGER NOT NULL DEFAULT 0,
            is_packed INTEGER NOT NULL DEFAULT 0,
            is_oneof INTEGER NOT NULL DEFAULT 0,
            is_map INTEGER NOT NULL DEFAULT 0,
            optional INTEGER NOT NULL DEFAULT 0,
            required INTEGER NOT NULL DEFAULT 0,
            oneof_index INTEGER,
            enum_closed INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS class_references (
            file TEXT NOT NULL,
            line INTEGER NOT NULL,
            source_package TEXT NOT NULL,
            target_class TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS proto_catalog (
            class_name TEXT NOT NULL,
            apk_version TEXT NOT NULL,
            confidence TEXT NOT NULL,
            field_count INTEGER NOT NULL,
            descriptor TEXT NOT NULL,
            source_file TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS proto_evidence (
            class_name TEXT NOT NULL,
            evidence_source TEXT NOT NULL,
            evidence_detail TEXT NOT NULL,
            source_file TEXT NOT NULL,
            line INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS proto_unknowns (
            class_name TEXT NOT NULL,
            reason TEXT NOT NULL,
            evidence_count INTEGER NOT NULL,
            notes TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS run_metadata (
            key TEXT NOT NULL,
            value TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_proto_classes_name ON proto_classes(class_name);
        CREATE INDEX IF NOT EXISTS idx_proto_fields_class ON proto_fields(class_name);
        CREATE INDEX IF NOT EXISTS idx_proto_fields_type ON proto_fields(base_type);
        CREATE INDEX IF NOT EXISTS idx_class_refs_target ON class_references(target_class);
        CREATE INDEX IF NOT EXISTS idx_class_refs_source ON class_references(source_package);
        CREATE INDEX IF NOT EXISTS idx_proto_catalog_class ON proto_catalog(class_name);
        CREATE INDEX IF NOT EXISTS idx_proto_catalog_confidence ON proto_catalog(confidence);
        CREATE INDEX IF NOT EXISTS idx_proto_evidence_class ON proto_evidence(class_name);
        CREATE INDEX IF NOT EXISTS idx_proto_unknowns_class ON proto_unknowns(class_name);
        CREATE INDEX IF NOT EXISTS idx_run_metadata_key ON run_metadata(key);
        """
    )


def write_sqlite(db_path: Path, signals: dict[str, list[dict[str, object]]]) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        _create_schema(conn)
        conn.execute("DELETE FROM uuids")
        conn.execute("DELETE FROM constants")
        conn.execute("DELETE FROM proto_accesses")
        conn.execute("DELETE FROM proto_writes")
        conn.execute("DELETE FROM enum_maps")
        conn.execute("DELETE FROM switch_maps")
        conn.execute("DELETE FROM call_edges")
        conn.execute("DELETE FROM proto_classes")
        conn.execute("DELETE FROM proto_fields")
        conn.execute("DELETE FROM class_references")
        conn.execute("DELETE FROM proto_catalog")
        conn.execute("DELETE FROM proto_evidence")
        conn.execute("DELETE FROM proto_unknowns")
        conn.execute("DELETE FROM run_metadata")

        conn.executemany(
            "INSERT INTO uuids(file, line, value) VALUES (?, ?, ?)",
            [(row["file"], row["line"], row["value"]) for row in signals.get("uuids", [])],
        )
        conn.executemany(
            "INSERT INTO constants(file, line, value) VALUES (?, ?, ?)",
            [(row["file"], row["line"], row["value"]) for row in signals.get("constants", [])],
        )
        conn.executemany(
            "INSERT INTO proto_accesses(file, line, accessor) VALUES (?, ?, ?)",
            [
                (row["file"], row["line"], row["accessor"])
                for row in signals.get("proto_accesses", [])
            ],
        )
        conn.executemany(
            "INSERT INTO proto_writes(file, line, target, op, value) VALUES (?, ?, ?, ?, ?)",
            [
                (row["file"], row["line"], row["target"], row["op"], row["value"])
                for row in signals.get("proto_writes", [])
            ],
        )
        conn.executemany(
            "INSERT INTO enum_maps(file, line, enum_class, int_value, enum_name) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    row["file"],
                    row["line"],
                    row["enum_class"],
                    row["int_value"],
                    row["enum_name"],
                )
                for row in signals.get("enum_maps", [])
            ],
        )
        conn.executemany(
            "INSERT INTO switch_maps(file, line, switch_expr, case_value, target) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    row["file"],
                    row["line"],
                    row["switch_expr"],
                    row["case_value"],
                    row["target"],
                )
                for row in signals.get("switch_maps", [])
            ],
        )
        conn.executemany(
            "INSERT INTO call_edges(file, line, target) VALUES (?, ?, ?)",
            [
                (row["file"], row["line"], row["target"])
                for row in signals.get("call_edges", [])
            ],
        )
        conn.executemany(
            "INSERT INTO proto_classes(file, class_name, deprecated, field_count, "
            "field_names, field_types, field_decls, sub_message_refs, descriptor, "
            "proto_syntax, decoded_fields) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    row["file"],
                    row["class_name"],
                    1 if row["deprecated"] else 0,
                    row["field_count"],
                    row["field_names"],
                    row["field_types"],
                    row["field_decls"],
                    row["sub_message_refs"],
                    row["descriptor"],
                    row.get("proto_syntax", ""),
                    row.get("decoded_fields", "[]"),
                )
                for row in signals.get("proto_classes", [])
            ],
        )
        # Flatten decoded fields into proto_fields table
        proto_field_rows = []
        for pc_row in signals.get("proto_classes", []):
            decoded = json.loads(pc_row.get("decoded_fields", "[]"))
            for f in decoded:
                proto_field_rows.append((
                    pc_row["class_name"],
                    f["field_number"],
                    f["type_label"],
                    f["base_type"],
                    f["type_id"],
                    1 if f.get("is_repeated") else 0,
                    1 if f.get("is_packed") else 0,
                    1 if f.get("is_oneof") else 0,
                    1 if f.get("is_map") else 0,
                    1 if f.get("optional") else 0,
                    1 if f.get("required") else 0,
                    f.get("oneof_index"),
                    1 if f.get("enum_closed") else 0,
                ))
        conn.executemany(
            "INSERT INTO proto_fields(class_name, field_number, type_label, base_type, "
            "type_id, is_repeated, is_packed, is_oneof, is_map, optional, required, "
            "oneof_index, enum_closed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            proto_field_rows,
        )
        conn.executemany(
            "INSERT INTO class_references(file, line, source_package, target_class) "
            "VALUES (?, ?, ?, ?)",
            [
                (row["file"], row["line"], row["source_package"], row["target_class"])
                for row in signals.get("class_references", [])
            ],
        )
        conn.executemany(
            "INSERT INTO proto_catalog(class_name, apk_version, confidence, field_count, "
            "descriptor, source_file) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    row["class_name"],
                    row["apk_version"],
                    row["confidence"],
                    row["field_count"],
                    row["descriptor"],
                    row["source_file"],
                )
                for row in signals.get("proto_catalog", [])
            ],
        )
        conn.executemany(
            "INSERT INTO proto_evidence(class_name, evidence_source, evidence_detail, "
            "source_file, line) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    row["class_name"],
                    row["evidence_source"],
                    row["evidence_detail"],
                    row["source_file"],
                    row["line"],
                )
                for row in signals.get("proto_evidence", [])
            ],
        )
        conn.executemany(
            "INSERT INTO proto_unknowns(class_name, reason, evidence_count, notes) "
            "VALUES (?, ?, ?, ?)",
            [
                (
                    row["class_name"],
                    row["reason"],
                    row["evidence_count"],
                    row["notes"],
                )
                for row in signals.get("proto_unknowns", [])
            ],
        )
        conn.executemany(
            "INSERT INTO run_metadata(key, value) VALUES (?, ?)",
            [(row["key"], row["value"]) for row in signals.get("run_metadata", [])],
        )
    return db_path
