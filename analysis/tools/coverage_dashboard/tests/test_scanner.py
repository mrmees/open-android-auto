from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from analysis.tools.coverage_dashboard.scanner import scan_audit_tree, ScanResult


def test_scan_empty_tree(tmp_path: Path) -> None:
    """Empty oaa/ dir produces ScanResult with zero counts."""
    (tmp_path / "oaa").mkdir()
    result = scan_audit_tree(tmp_path)
    assert result.total_sidecars == 0
    assert result.total_protos == 0
    assert result.pending_gold_count == 0
    assert result.directories_scanned == 0
    assert result.per_channel == {}
    assert result.missing_sidecars == {}
    assert result.orphan_sidecars == {}


def test_scan_single_bronze(mock_oaa_tree: Path) -> None:
    """Audio directory has 1 bronze sidecar."""
    result = scan_audit_tree(mock_oaa_tree)
    assert "audio" in result.per_channel
    assert result.per_channel["audio"].bronze == 1


def test_scan_evidence_types_dynamic(mock_oaa_tree: Path) -> None:
    """Evidence types discovered dynamically from sidecar data, not hardcoded."""
    result = scan_audit_tree(mock_oaa_tree)
    # The video sidecar has cross_version and apk_static evidence
    assert "silver" in result.evidence_by_tier
    silver_ev = result.evidence_by_tier["silver"]
    assert "cross_version" in silver_ev
    assert "apk_static" in silver_ev
    # The audio bronze sidecar has apk_static
    assert "bronze" in result.evidence_by_tier
    assert "apk_static" in result.evidence_by_tier["bronze"]


def test_pending_platinum_not_counted(mock_oaa_tree: Path) -> None:
    """pending_platinum_evidence entries must NOT appear in evidence_by_tier."""
    result = scan_audit_tree(mock_oaa_tree)
    # The video sidecar has pending_platinum_evidence with type: platinum_evidence
    # But this should NOT be in evidence_by_tier["silver"]
    silver_ev = result.evidence_by_tier.get("silver", {})
    assert "platinum_evidence" not in silver_ev, (
        "pending_platinum_evidence must not be counted in the main evidence breakdown"
    )


def test_missing_sidecar_detected(mock_oaa_tree: Path) -> None:
    """Proto without matching .audit.yaml appears in missing_sidecars."""
    result = scan_audit_tree(mock_oaa_tree)
    assert "audio" in result.missing_sidecars
    assert "OrphanlessProto.proto" in result.missing_sidecars["audio"]


def test_orphan_sidecar_detected(mock_oaa_tree: Path) -> None:
    """.audit.yaml without matching .proto appears in orphan_sidecars."""
    result = scan_audit_tree(mock_oaa_tree)
    assert "sensor" in result.orphan_sidecars
    assert "OrphanSidecar.audit.yaml" in result.orphan_sidecars["sensor"]


def test_oem_match_pending_gold_counted(mock_oaa_tree: Path) -> None:
    """Sidecar with oem_match_pending_gold: true increments pending_gold_count."""
    result = scan_audit_tree(mock_oaa_tree)
    assert result.pending_gold_count == 1


def test_retracted_and_superseded_separate(mock_oaa_tree: Path) -> None:
    """Retracted and superseded counted in their own tier columns."""
    result = scan_audit_tree(mock_oaa_tree)
    assert "control" in result.per_channel
    control = result.per_channel["control"]
    assert control.retracted == 1
    assert control.superseded == 1
    # They should NOT be counted in active tiers
    assert control.bronze == 0
    assert control.silver == 0
    assert control.gold == 0
    assert control.platinum == 0


def test_scan_total_counts(mock_oaa_tree: Path) -> None:
    """Total sidecar and proto counts are correct for the mock tree."""
    result = scan_audit_tree(mock_oaa_tree)
    # 5 sidecars: audio/FakeAudioMessage, video/FakeVideoMessage,
    # control/RetractedMessage, control/SupersededMessage, sensor/OrphanSidecar
    assert result.total_sidecars == 5
    # 4 protos: audio/FakeAudioMessage, audio/OrphanlessProto,
    # video/FakeVideoMessage, control/RetractedMessage, control/SupersededMessage
    assert result.total_protos == 5
    assert result.directories_scanned == 4  # audio, video, control, sensor


def test_scan_evidence_custom_type(tmp_path: Path) -> None:
    """Dynamically discovered evidence types include non-standard types."""
    oaa = tmp_path / "oaa" / "custom"
    oaa.mkdir(parents=True)
    (oaa / "Msg.proto").write_text('syntax = "proto3";\n')
    (oaa / "Msg.audit.yaml").write_text(dedent("""\
        proto_file: oaa/custom/Msg.proto
        confidence: gold
        evidence:
          - type: custom_type
            source: custom_source
            description: Custom evidence
          - type: apk_static
            source: jadx
            description: Static
        last_updated: "2026-01-01"
    """))
    result = scan_audit_tree(tmp_path)
    assert "custom_type" in result.evidence_by_tier["gold"]
    assert result.evidence_by_tier["gold"]["custom_type"] == 1
    assert result.evidence_by_tier["gold"]["apk_static"] == 1
