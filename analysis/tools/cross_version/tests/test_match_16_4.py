"""Tests for the two-pass 16.4 class identity matcher.

XVER-01 — matcher snapshot + pure-function unit tests.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def test_match_snapshot() -> None:
    """Snapshot test: matcher output against the real 4 APK DBs matches committed snapshot.

    Source of truth: analysis/tools/cross_version/tests/fixtures/match_snapshot.json
    Regeneration:
        PYTHONPATH=. python3 -m analysis.tools.cross_version.match_16_4 \
          > analysis/tools/cross_version/tests/fixtures/match_snapshot.json
    """
    from analysis.tools.cross_version.match_16_4 import run_matcher

    snapshot = json.loads((FIXTURES / "match_snapshot.json").read_text())
    result = run_matcher()

    # Allow ±5 slack on total committable. Empirical baseline: 93-96 depending
    # on Pass 2 feedback-loop behavior. The RESEARCH.md target is 93 ± 5.
    assert 88 <= result["total_committable"] <= 101, (
        f"Matcher total_committable ({result['total_committable']}) outside expected range [88, 101].\n"
        f"Snapshot baseline: {snapshot['total_committable']} (08-RESEARCH.md empirical sweep).\n"
        f"Regenerate: PYTHONPATH=. python3 -m analysis.tools.cross_version.match_16_4 > "
        f"analysis/tools/cross_version/tests/fixtures/match_snapshot.json"
    )
    # Enums are perfectly stable — all 5 must match uniquely.
    assert result["pass1_enum_commits"] == snapshot["pass1_enum_commits"], (
        f"Enum commit count drift: expected {snapshot['pass1_enum_commits']}, "
        f"got {result['pass1_enum_commits']}. "
        f"Enum fingerprints should be fully stable across APK versions."
    )
    # Message Pass 1 count should match exactly — fingerprint stability is
    # deterministic given the same 4 DBs.
    assert result["pass1_message_commits"] == snapshot["pass1_message_commits"], (
        f"Message Pass 1 commit drift: expected {snapshot['pass1_message_commits']}, "
        f"got {result['pass1_message_commits']}. "
        f"Regenerate the snapshot if the real DBs changed."
    )
    # Total mappings must be exactly 240
    assert result["total_mappings"] == 240


def test_field_tuple_extraction(tmp_path: Path) -> None:
    """_field_tuple returns a stable sorted tuple of (field_num, base_type)."""
    from analysis.tools.cross_version.match_16_4 import _field_tuple

    db = tmp_path / "t.db"
    conn = sqlite3.connect(str(db))
    conn.execute(
        """
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
        """
    )
    conn.executemany(
        "INSERT INTO proto_fields (class_name, field_number, base_type) VALUES (?, ?, ?)",
        [("cls", 3, "string"), ("cls", 1, "int32"), ("cls", 2, "bool")],
    )
    conn.commit()
    conn.close()

    tup = _field_tuple(db, "cls")
    assert tup == ((1, "int32"), (2, "bool"), (3, "string"))


def test_source_class_prefers_16_2() -> None:
    """_source_class returns 16.2 when available, otherwise 16.1, otherwise 15.9."""
    from analysis.tools.cross_version.match_16_4 import _source_class
    from analysis.tools.proto_schema_validator.models import ProtoMapping

    m = ProtoMapping(
        proto_message="X",
        proto_file="oaa/x.proto",
        apk_classes={"15.9": "a", "16.1": "b", "16.2": "c"},
    )
    assert _source_class(m) == ("c", "16.2")

    m2 = ProtoMapping(
        proto_message="Y",
        proto_file="oaa/y.proto",
        apk_classes={"15.9": "a", "16.1": "b"},
    )
    assert _source_class(m2) == ("b", "16.1")

    m3 = ProtoMapping(
        proto_message="Z",
        proto_file="oaa/z.proto",
        apk_classes={"15.9": None, "16.1": None, "16.2": None},
    )
    assert _source_class(m3) == (None, "")


def test_candidates_md_has_table_rows() -> None:
    """After run_matcher(), 16-4-mapping-candidates.md has a row per unresolved mapping."""
    from analysis.tools.cross_version.match_16_4 import CANDIDATES_MD

    # The matcher should already have been run by test_match_snapshot.
    # This test just checks the side-effect file shape.
    assert CANDIDATES_MD.exists(), f"Missing {CANDIDATES_MD}"
    content = CANDIDATES_MD.read_text()
    assert "Total unresolved:" in content
    assert "| Proto | Outcome |" in content
    # Should be at least 130 data rows (empirical: 144 unresolved)
    table_rows = [line for line in content.splitlines() if line.startswith("|")]
    assert len(table_rows) >= 130, f"Too few candidate rows: {len(table_rows)}"
