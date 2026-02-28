import json
import sqlite3

from analysis.tools.apk_indexer.write_json import write_json_exports
from analysis.tools.apk_indexer.write_sqlite import write_sqlite


def _sample_signals():
    return {
        "uuids": [{"file": "A.java", "line": 1, "value": "4de17a00-52cb-11e6-bdf4-0800200c9a66"}],
        "constants": [{"file": "B.java", "line": 2, "value": "0x1A2B"}],
        "proto_accesses": [{"file": "C.java", "line": 3, "accessor": "setChannelId"}],
        "call_edges": [{"file": "D.java", "line": 4, "target": "transport.sendMessage"}],
        "proto_writes": [{"file": "E.java", "line": 5, "target": "xhqVar.b", "op": "|=", "value": "16"}],
        "enum_maps": [{"file": "vyn.java", "line": 9, "enum_class": "vyn", "int_value": 1, "enum_name": "MEDIA_CODEC_AUDIO_PCM"}],
        "switch_maps": [{"file": "Dispatch.java", "line": 2, "switch_expr": "messageId", "case_value": "7", "target": "handler.handleAudio"}],
        "proto_catalog": [{
            "class_name": "vvh",
            "apk_version": "16.1",
            "confidence": "high",
            "field_count": 3,
            "descriptor": "descriptor",
            "source_file": "sources/defpackage/vvh.java",
        }],
        "proto_evidence": [{
            "class_name": "vvh",
            "evidence_source": "descriptor",
            "evidence_detail": "non-empty descriptor",
            "source_file": "sources/defpackage/vvh.java",
            "line": 0,
        }],
        "proto_unknowns": [{
            "class_name": "x1a",
            "reason": "insufficient_evidence",
            "evidence_count": 1,
            "notes": "manual_review_required",
        }],
        "run_metadata": [{
            "key": "apk_version",
            "value": "16.1",
        }],
    }


def test_sqlite_schema_created(tmp_path):
    db = tmp_path / "apk_index.db"
    write_sqlite(db, _sample_signals())

    with sqlite3.connect(db) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "select name from sqlite_master where type='table'"
            ).fetchall()
        }
        assert "uuids" in tables
        assert "constants" in tables
        assert "proto_accesses" in tables
        assert "call_edges" in tables
        assert "proto_writes" in tables
        assert "enum_maps" in tables
        assert "switch_maps" in tables
        assert "proto_catalog" in tables
        assert "proto_evidence" in tables
        assert "proto_unknowns" in tables
        assert "run_metadata" in tables


def test_json_exports_created(tmp_path):
    out_dir = tmp_path / "json"
    write_json_exports(out_dir, _sample_signals())

    uuids = json.loads((out_dir / "uuids.json").read_text())
    assert uuids[0]["value"] == "4de17a00-52cb-11e6-bdf4-0800200c9a66"


def test_sqlite_inserts_catalog_outputs(tmp_path):
    db = tmp_path / "apk_index.db"
    write_sqlite(db, _sample_signals())

    with sqlite3.connect(db) as conn:
        catalog_count = conn.execute("select count(*) from proto_catalog").fetchone()[0]
        evidence_count = conn.execute("select count(*) from proto_evidence").fetchone()[0]
        unknown_count = conn.execute("select count(*) from proto_unknowns").fetchone()[0]
        metadata_count = conn.execute("select count(*) from run_metadata").fetchone()[0]

    assert catalog_count == 1
    assert evidence_count == 1
    assert unknown_count == 1
    assert metadata_count == 1
