"""Tests for the markdown mapping table generator."""
from __future__ import annotations

from pathlib import Path

from analysis.tools.proto_schema_validator.models import ProtoMapping
from analysis.tools.cross_version.tables import generate_tables


def test_generates_markdown(
    mock_db_v1: Path, mock_db_v2: Path, sample_mappings: list[ProtoMapping], tmp_path: Path,
):
    """Tables module produces markdown files in the output directory."""
    output_dir = tmp_path / "cross-version"
    db_paths = {"15.9": mock_db_v1, "16.1": mock_db_v1, "16.2": mock_db_v2}
    created = generate_tables(db_paths, sample_mappings, output_dir)

    assert len(created) >= 1, "Should produce at least one markdown file"
    for p in created:
        assert p.exists(), f"Output file {p} should exist"
        content = p.read_text()
        assert "|" in content, "Output should contain markdown table syntax"
        assert "Proto Name" in content or "proto_message" in content.lower() or "Proto" in content


def test_coverage(
    mock_db_v1: Path, mock_db_v2: Path, sample_mappings: list[ProtoMapping], tmp_path: Path,
):
    """Output tables include all mappings from the input (no silent drops)."""
    output_dir = tmp_path / "cross-version"
    db_paths = {"15.9": mock_db_v1, "16.1": mock_db_v1, "16.2": mock_db_v2}
    generate_tables(db_paths, sample_mappings, output_dir)

    # Read all generated markdown content
    all_content = ""
    for md_file in output_dir.glob("*.md"):
        all_content += md_file.read_text()

    # Every mapping's proto_message should appear in the output
    for m in sample_mappings:
        assert m.proto_message in all_content, (
            f"Mapping {m.proto_message} missing from generated tables"
        )
