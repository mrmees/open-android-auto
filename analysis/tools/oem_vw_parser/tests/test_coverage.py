from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis.tools.oem_vw_parser.attribution import attribute_record
from analysis.tools.oem_vw_parser.coverage import (
    VALID_OVERRIDE_RATIONALES,
    build_coverage_manifest,
    compute_baseline_snapshot_hash,
    temporal_profile,
    validate_override,
)
from analysis.tools.oem_vw_parser.io import load_vw_capture
from analysis.tools.oem_vw_parser.models import (
    CoverageManifest,
    DeclaredService,
    MsgTypeCoverageEntry,
    SdpSnapshot,
)
from analysis.tools.oem_vw_parser.sdp_decode import decode_sdp_response
from analysis.tools.oem_vw_parser.tier_classifier import classify_capture


def _build_manifest_from_micro(bundle, vw_micro_path, sdp_response_path):
    records = list(load_vw_capture(vw_micro_path, capture_id="vw_micro"))
    classified, _ = classify_capture(records, bundle)
    sdp = decode_sdp_response(bundle, sdp_response_path)
    attributed = [attribute_record(cr, sdp) for cr in classified]
    capture_duration_s = (
        (max(r.ts_ms for r in records) - min(r.ts_ms for r in records)) / 1000.0
        if records
        else 0.0
    )
    return build_coverage_manifest(
        classified=classified,
        attributed=attributed,
        sdp=sdp,
        capture_duration_s=capture_duration_s,
        dhu_baseline_paths=[],
        dhu_records=[],
    )


def test_manifest_schema(bundle, vw_micro_path, sdp_response_path):
    """Every per-msg_type entry has all 13 required fields."""
    manifest = _build_manifest_from_micro(bundle, vw_micro_path, sdp_response_path)
    assert isinstance(manifest, CoverageManifest)
    required_fields = {
        "service",
        "msg_type",
        "direction",
        "count",
        "bytes",
        "first_seen_ts_ms",
        "last_seen_ts_ms",
        "mean_rate_per_sec",
        "observation_span_s",
        "duty_cycle",
        "burstiness",
        "confidence_distribution",
        "fields_observed",
    }
    assert len(manifest.per_msg_type) > 0
    for entry in manifest.per_msg_type:
        assert isinstance(entry, MsgTypeCoverageEntry)
        for field in required_fields:
            assert hasattr(entry, field), f"missing field {field}"
        assert entry.fields_observed is None


def test_absence_model(bundle, vw_micro_path, sdp_response_path):
    """Three-part absence model is populated correctly."""
    # Build a few synthetic DHU records covering services VW doesn't declare
    # so the comparative gaps test branch is non-empty.
    from analysis.tools.oem_vw_parser.models import UnifiedRecord

    fake_dhu_records = [
        UnifiedRecord(
            capture_id="dhu_fake",
            seq=i,
            ts_ms=i * 100,
            direction="in",
            msg_type=0x801A,
            payload=b"\x00\x80\x1a\x10",
            payload_len=4,
            channel_id=15,
            flags=11,
            service_type="radio_source",  # NOT in VW SDP
        )
        for i in range(3)
    ]

    records = list(load_vw_capture(vw_micro_path, capture_id="vw_micro"))
    classified, _ = classify_capture(records, bundle)
    sdp = decode_sdp_response(bundle, sdp_response_path)
    attributed = [attribute_record(cr, sdp) for cr in classified]

    manifest = build_coverage_manifest(
        classified=classified,
        attributed=attributed,
        sdp=sdp,
        capture_duration_s=60.0,
        dhu_baseline_paths=[Path("captures/general"), Path("captures/idle-baseline")],
        dhu_records=fake_dhu_records,
    )

    # Required structure exists.
    assert isinstance(manifest.observed, tuple)
    assert isinstance(manifest.gaps_intrinsic, tuple)
    assert isinstance(manifest.gaps_comparative, tuple)
    assert isinstance(manifest.anomalies_service_not_declared, tuple)
    assert isinstance(manifest.anomalies_unattributed, tuple)

    # The micro fixture covers some VW services but not all 13 channels —
    # gaps.intrinsic must be non-empty.
    assert len(manifest.gaps_intrinsic) >= 1, (
        "expected at least one intrinsic gap given the micro fixture's coverage"
    )

    # Comparative gaps must be non-empty (we fed in fake DHU records on a
    # service VW doesn't declare).
    assert len(manifest.gaps_comparative) >= 1, (
        "expected at least one comparative gap given the synthetic DHU records"
    )


def test_zero_observation_entries(bundle, sdp_response_path):
    """Empty record list → every declared channel becomes a zero-obs gap entry.

    Aggregation key is (channel_id, channel_kind), NOT channel_kind alone.
    Sum across channel_kind_summary['declared'] must equal 13 for VW.
    """
    sdp = decode_sdp_response(bundle, sdp_response_path)
    manifest = build_coverage_manifest(
        classified=[],
        attributed=[],
        sdp=sdp,
        capture_duration_s=60.0,
        dhu_baseline_paths=[],
        dhu_records=[],
    )

    # The locked aggregation key: 13 declared channels → 13 entries in gaps.intrinsic.
    assert len(manifest.gaps_intrinsic) == 13, (
        f"expected 13 intrinsic gap entries (one per declared channel), "
        f"got {len(manifest.gaps_intrinsic)}"
    )
    assert len(manifest.observed) == 0
    assert len(manifest.gaps_intrinsic) + len(manifest.observed) == 13

    for gap in manifest.gaps_intrinsic:
        assert gap["observed_count"] == 0
        assert gap["declared_in_sdp"] is True
        assert "channel_id" in gap
        assert "channel_kind" in gap

    # channel_kind_summary aggregates back across channel_kinds.
    assert isinstance(manifest.channel_kind_summary, dict)
    total_declared = sum(
        s["declared"] for s in manifest.channel_kind_summary.values()
    )
    assert total_declared == 13, (
        f"channel_kind_summary 'declared' values must sum to 13 (the 13 declared "
        f"VW channels), got {total_declared}"
    )
    # av_channel has 5 declared channels (1, 3, 4, 5, 6).
    assert manifest.channel_kind_summary.get("av_channel", {}).get("declared") == 5


def test_snapshot_hash_stable(tmp_path):
    """Running compute_baseline_snapshot_hash twice with the same input
    produces byte-identical output."""
    base = tmp_path / "fake_baseline"
    base.mkdir()
    (base / "a.jsonl").write_text("hello\n")
    (base / "b.jsonl").write_text("world\n")

    h1 = compute_baseline_snapshot_hash([base])
    h2 = compute_baseline_snapshot_hash([base])
    assert h1 == h2
    assert isinstance(h1, str)
    assert len(h1) == 64  # sha256 hex


def test_override_schema_enforcement():
    """Override validator rejects missing fields, invalid rationale,
    empty evidence."""
    valid = {
        "service": "hvac_control",
        "msg_type": 32801,
        "observed_in_current_capture": False,
        "override": {
            "rationale": "transitive_evidence",
            "evidence": [
                {
                    "type": "observed_in_other_capture",
                    "capture": "captures/prodigy/active-navigation",
                }
            ],
            "approver": "matthew",
            "approved_at": "2026-04-07T14:23:00Z",
            "review_notes": "Structural match with Prodigy capture",
        },
    }
    # No exception for valid override.
    validate_override(valid)

    # Missing 'service' field.
    invalid_missing = dict(valid)
    del invalid_missing["service"]
    with pytest.raises(ValueError, match="missing"):
        validate_override(invalid_missing)

    # Invalid rationale (free text).
    invalid_rationale = json.loads(json.dumps(valid))  # deep copy
    invalid_rationale["override"]["rationale"] = "free text reason"
    with pytest.raises(ValueError, match="rationale"):
        validate_override(invalid_rationale)

    # Empty evidence.
    invalid_empty_evidence = json.loads(json.dumps(valid))
    invalid_empty_evidence["override"]["evidence"] = []
    with pytest.raises(ValueError, match="evidence"):
        validate_override(invalid_empty_evidence)

    # The locked vocabulary.
    assert VALID_OVERRIDE_RATIONALES == frozenset(
        {
            "structural_equivalence",
            "transitive_evidence",
            "external_spec",
            "cross_capture_convergence",
        }
    )


def test_burstiness_singleton_rule():
    """count == 1 → singleton, no ZeroDivisionError."""
    profile = temporal_profile(
        ts_ms_list=[1000],
        capture_duration_s=60.0,
    )
    assert profile["burstiness"] == "singleton"
    assert profile["count"] == 1


def test_burstiness_count_2_is_unknown():
    """count == 2 → unknown (only 1 inter-arrival, can't characterize)."""
    profile = temporal_profile(
        ts_ms_list=[1000, 2000],
        capture_duration_s=60.0,
    )
    assert profile["burstiness"] == "unknown"
    assert profile["count"] == 2


def test_burstiness_steady_vs_bursty():
    """Tight inter-arrivals → steady; wildly varying → bursty."""
    # Steady: every 100ms.
    steady = temporal_profile(
        ts_ms_list=[i * 100 for i in range(20)],
        capture_duration_s=60.0,
    )
    assert steady["burstiness"] == "steady"

    # Bursty: clustered, then long pause, then more clusters.
    bursty = temporal_profile(
        ts_ms_list=[100, 105, 110, 115, 120, 5000, 5005, 5010, 30000, 30005],
        capture_duration_s=60.0,
    )
    assert bursty["burstiness"] == "bursty"
