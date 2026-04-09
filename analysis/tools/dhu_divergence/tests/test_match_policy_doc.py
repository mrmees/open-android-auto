"""Content tests for docs/verification/05-oem-match-policy.md (TIER-03).

Cross-file integrity: the schema's match_rules enum MUST exactly equal the
8 MATCH-NN rule IDs defined in the doc (09-RESEARCH.md § Match Rule Set).
"""
from __future__ import annotations

import re
from pathlib import Path


def test_eight_match_rules(repo_root: Path) -> None:
    text = (repo_root / "docs/verification/05-oem-match-policy.md").read_text()
    for i in range(1, 9):
        assert f"MATCH-0{i}" in text, f"Missing MATCH-0{i}"
    # Exactly 8 — no MATCH-09 or higher
    assert "MATCH-09" not in text


def test_four_nomatch_rules(repo_root: Path) -> None:
    text = (repo_root / "docs/verification/05-oem-match-policy.md").read_text()
    for i in range(1, 5):
        assert f"NOMATCH-0{i}" in text, f"Missing NOMATCH-0{i}"
    assert "NOMATCH-05" not in text


def test_schema_enum_matches_doc(repo_root: Path, schema: dict) -> None:
    """The schema's match_rules enum MUST exactly equal the 8 MATCH-NN rule IDs
    defined as level-3 headings in the doc. Locks the doc + schema together."""
    schema_enum = set(
        schema["$defs"]["evidence_entry"]["properties"]["match_rules"]["items"]["enum"]
    )
    expected = {f"MATCH-0{i}" for i in range(1, 9)}
    assert schema_enum == expected, (
        f"Schema match_rules enum {schema_enum} does not match expected {expected}"
    )

    text = (repo_root / "docs/verification/05-oem-match-policy.md").read_text()
    doc_headings = set(re.findall(r"^### (MATCH-\d{2})\b", text, flags=re.MULTILINE))
    assert doc_headings == expected, (
        f"Doc MATCH headings {doc_headings} do not match schema enum {expected}"
    )
