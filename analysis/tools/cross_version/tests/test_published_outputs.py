"""Integration test: published cross-version output files exist with expected content.

Gap 1 (PROTO-03): Verifies that docs/cross-version/ mapping tables exist on disk
with the correct structure -- markdown tables with version columns for 15.9, 16.1, 16.2.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
CROSS_VERSION_DIR = REPO_ROOT / "docs" / "cross-version"


def test_cross_version_dir_exists():
    """docs/cross-version/ directory must exist as a published artifact."""
    assert CROSS_VERSION_DIR.exists(), (
        f"docs/cross-version/ not found at {CROSS_VERSION_DIR}"
    )
    assert CROSS_VERSION_DIR.is_dir()


def test_category_tables_exist_for_each_oaa_subdir():
    """Each oaa/ subdirectory must have a corresponding mapping table in docs/cross-version/."""
    oaa_root = REPO_ROOT / "oaa"
    oaa_categories = {d.name for d in oaa_root.iterdir() if d.is_dir()}

    published_tables = {
        p.stem for p in CROSS_VERSION_DIR.glob("*.md")
        if p.name != "consistency-report.md"
    }

    missing = oaa_categories - published_tables
    assert not missing, (
        f"Missing mapping tables for oaa/ categories: {sorted(missing)}\n"
        f"Published tables: {sorted(published_tables)}"
    )


def test_mapping_tables_have_version_columns():
    """Each mapping table must include columns for 15.9, 16.1, and 16.2."""
    table_files = [
        p for p in CROSS_VERSION_DIR.glob("*.md")
        if p.name != "consistency-report.md"
    ]
    assert len(table_files) >= 5, (
        f"Expected at least 5 mapping table files, found {len(table_files)}"
    )

    for table_path in table_files:
        content = table_path.read_text(encoding="utf-8")
        assert "15.9" in content, (
            f"{table_path.name}: missing '15.9' column header"
        )
        assert "16.1" in content, (
            f"{table_path.name}: missing '16.1' column header"
        )
        assert "16.2" in content, (
            f"{table_path.name}: missing '16.2' column header"
        )


def test_mapping_tables_contain_markdown_table_syntax():
    """Each mapping table must contain markdown table rows (pipe-delimited)."""
    table_files = [
        p for p in CROSS_VERSION_DIR.glob("*.md")
        if p.name != "consistency-report.md"
    ]

    for table_path in table_files:
        content = table_path.read_text(encoding="utf-8")
        lines_with_pipes = [l for l in content.splitlines() if "|" in l]
        assert len(lines_with_pipes) >= 3, (
            f"{table_path.name}: expected at least 3 pipe-delimited rows "
            f"(header, separator, data), found {len(lines_with_pipes)}"
        )


def test_mapping_tables_have_proto_name_column():
    """Each mapping table must have a 'Proto Name' column header."""
    table_files = [
        p for p in CROSS_VERSION_DIR.glob("*.md")
        if p.name != "consistency-report.md"
    ]

    for table_path in table_files:
        content = table_path.read_text(encoding="utf-8")
        assert "Proto Name" in content, (
            f"{table_path.name}: missing 'Proto Name' column header"
        )


def test_consistency_report_exists():
    """docs/cross-version/consistency-report.md must exist."""
    report = CROSS_VERSION_DIR / "consistency-report.md"
    assert report.exists(), "consistency-report.md missing from docs/cross-version/"
    assert report.stat().st_size > 0, "consistency-report.md is empty"


def test_consistency_report_has_summary_section():
    """The consistency report must contain a Summary section."""
    report = CROSS_VERSION_DIR / "consistency-report.md"
    content = report.read_text(encoding="utf-8")
    assert "Summary" in content, (
        "consistency-report.md missing 'Summary' section"
    )


def test_mapping_tables_contain_obfuscated_class_names():
    """Tables must contain backtick-quoted obfuscated class names (3-letter patterns like `vnr`)."""
    table_files = [
        p for p in CROSS_VERSION_DIR.glob("*.md")
        if p.name != "consistency-report.md"
    ]

    found_obfuscated = 0
    for table_path in table_files:
        content = table_path.read_text(encoding="utf-8")
        # Obfuscated class names appear as backtick-quoted 3-letter lowercase strings
        import re
        matches = re.findall(r"`[a-z]{3}`", content)
        found_obfuscated += len(matches)

    assert found_obfuscated > 10, (
        f"Expected many backtick-quoted obfuscated class names across all tables, "
        f"found only {found_obfuscated}"
    )
