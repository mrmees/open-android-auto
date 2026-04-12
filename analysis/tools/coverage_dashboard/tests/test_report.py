from __future__ import annotations

import json

from analysis.tools.coverage_dashboard.scanner import ScanResult, ChannelCounts
from analysis.tools.coverage_dashboard.report import render_markdown, render_json


def _sample_result() -> ScanResult:
    """Build a minimal ScanResult for report tests."""
    return ScanResult(
        per_channel={
            "audio": ChannelCounts(bronze=2, silver=1),
            "video": ChannelCounts(gold=1, platinum=1),
        },
        evidence_by_tier={
            "bronze": {"apk_static": 2},
            "silver": {"cross_version": 1},
            "gold": {"deep_trace": 1, "apk_static": 1},
            "platinum": {"platinum_evidence": 1},
        },
        missing_sidecars={
            "audio": ["MissingA.proto", "MissingB.proto"],
            "sensor": ["MissingC.proto"],
        },
        orphan_sidecars={},
        total_sidecars=5,
        total_protos=8,
        pending_gold_count=3,
        directories_scanned=4,
    )


def test_markdown_section_order() -> None:
    """Output has 6 sections in locked order."""
    md = render_markdown(_sample_result())
    sections = [
        "## Summary",
        "## Per-Channel Tier Counts",
        "## Evidence Type Breakdown",
        "## Missing Sidecars",
        "## Orphan Sidecars",
        "## Dashboard Metadata",
    ]
    positions = []
    for s in sections:
        pos = md.find(s)
        assert pos != -1, f"Section '{s}' not found in markdown output"
        positions.append(pos)
    # Verify strict ordering
    for i in range(len(positions) - 1):
        assert positions[i] < positions[i + 1], (
            f"Section '{sections[i]}' must appear before '{sections[i + 1]}'"
        )


def test_table_column_headers() -> None:
    """Per-channel table has exact locked column headers."""
    md = render_markdown(_sample_result())
    expected = "| Channel | Bronze | Silver | Gold | Platinum (s-OEM) | Retracted | Superseded | Total |"
    assert expected in md, (
        f"Expected table header not found.\nExpected: {expected}\nGot markdown:\n{md[:500]}"
    )


def test_json_top_level_keys() -> None:
    """JSON has keys matching section names."""
    json_str = render_json(_sample_result())
    data = json.loads(json_str)
    expected_keys = {
        "summary",
        "per_channel_tier_counts",
        "evidence_type_breakdown",
        "missing_sidecars",
        "orphan_sidecars",
        "metadata",
    }
    assert set(data.keys()) == expected_keys, (
        f"JSON keys mismatch. Expected: {expected_keys}, Got: {set(data.keys())}"
    )


def test_missing_sidecars_grouped_by_directory() -> None:
    """Missing sidecars grouped under directory headings."""
    md = render_markdown(_sample_result())
    assert "### audio (2 missing)" in md
    assert "### sensor (1 missing)" in md
    assert "- MissingA.proto" in md
    assert "- MissingB.proto" in md
    assert "- MissingC.proto" in md


def test_zero_evidence_columns_omitted() -> None:
    """Evidence type with 0 usage across all tiers is not shown in evidence table."""
    result = ScanResult(
        per_channel={"test": ChannelCounts(bronze=1)},
        evidence_by_tier={"bronze": {"apk_static": 1}},
        missing_sidecars={},
        orphan_sidecars={},
        total_sidecars=1,
        total_protos=1,
        pending_gold_count=0,
        directories_scanned=1,
    )
    md = render_markdown(result)
    # Only apk_static should appear as an evidence column; no deep_trace, etc.
    assert "apk_static" in md
    # deep_trace should not appear since it has zero usage
    # Find the evidence table section
    ev_start = md.find("## Evidence Type Breakdown")
    ev_end = md.find("## Missing Sidecars")
    ev_section = md[ev_start:ev_end]
    assert "deep_trace" not in ev_section


def test_json_summary_has_tier_counts() -> None:
    """JSON summary includes tier breakdown and coverage percentage."""
    json_str = render_json(_sample_result())
    data = json.loads(json_str)
    summary = data["summary"]
    assert summary["total_sidecars"] == 5
    assert summary["total_protos"] == 8
    assert "tiers" in summary
    assert summary["tiers"]["bronze"] == 2
    assert summary["tiers"]["platinum"] == 1
    assert summary["pending_gold_count"] == 3


def test_json_per_channel_structure() -> None:
    """JSON per_channel_tier_counts has expected structure."""
    json_str = render_json(_sample_result())
    data = json.loads(json_str)
    channels = data["per_channel_tier_counts"]
    assert "audio" in channels
    assert channels["audio"]["bronze"] == 2
    assert channels["audio"]["silver"] == 1
    assert channels["audio"]["total"] == 3
    assert "video" in channels
    assert channels["video"]["gold"] == 1
    assert channels["video"]["platinum"] == 1


def test_orphan_sidecars_empty_message() -> None:
    """When no orphan sidecars exist, section says so."""
    md = render_markdown(_sample_result())
    orphan_start = md.find("## Orphan Sidecars")
    metadata_start = md.find("## Dashboard Metadata")
    orphan_section = md[orphan_start:metadata_start]
    assert "No orphan sidecars found" in orphan_section


def test_summary_has_pending_gold() -> None:
    """Summary mentions pending_gold_count when > 0."""
    md = render_markdown(_sample_result())
    summary_start = md.find("## Summary")
    tier_start = md.find("## Per-Channel Tier Counts")
    summary_section = md[summary_start:tier_start]
    assert "oem_match_pending_gold" in summary_section
    assert "3" in summary_section
