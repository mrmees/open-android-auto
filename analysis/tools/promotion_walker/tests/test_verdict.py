from __future__ import annotations
import json
from pathlib import Path

import pytest
import yaml

from analysis.tools.promotion_walker.verdict import (
    Verdict, VerdictKind, walker_decide, content_hash,
)
from analysis.tools.promotion_walker.run import _build_platinum_evidence_entry

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_already_platinum_skip(schema: dict, mock_sdp: dict) -> None:
    sidecar = _load("sidecar_already_platinum.audit.yaml")
    sdp_kinds = {c["channel_kind"] for c in mock_sdp["response"]["channels"]}
    verdict = walker_decide(sidecar, Path("oaa/video/test.audit.yaml"), {}, sdp_kinds, {}, schema)
    assert verdict.kind == VerdictKind.SKIP_ALREADY_PLATINUM


def test_stated_platinum_without_derived_prerequisites_routes_review(
    schema: dict, mock_sdp: dict
) -> None:
    sidecar = _load("sidecar_already_platinum.audit.yaml")
    sidecar["evidence"][-1]["match_rules"] = ["MATCH-08"]
    verdict = walker_decide(
        sidecar,
        Path("oaa/video/test.audit.yaml"),
        {},
        {"av_channel"},
        {},
        schema,
    )
    assert verdict.kind == VerdictKind.CONTRADICTION_REVIEW
    assert "canonical evidence policy" in (verdict.contradiction_summary or "")


def test_retracted_skip(schema: dict, mock_sdp: dict) -> None:
    sidecar = _load("sidecar_retracted.audit.yaml")
    sdp_kinds = {c["channel_kind"] for c in mock_sdp["response"]["channels"]}
    verdict = walker_decide(sidecar, Path("oaa/media/test.audit.yaml"), {}, sdp_kinds, {}, schema)
    assert verdict.kind == VerdictKind.SKIP_RETRACTED


def test_superseded_skip(schema: dict, mock_sdp: dict) -> None:
    # Synthetic: no fixture for superseded; construct one
    sidecar = {"proto": "oaa/media/Synthetic.proto", "message": "SyntheticSuperseded", "confidence": "superseded"}
    sdp_kinds = {c["channel_kind"] for c in mock_sdp["response"]["channels"]}
    verdict = walker_decide(sidecar, Path("oaa/media/synthetic.audit.yaml"), {}, sdp_kinds, {}, None)
    assert verdict.kind == VerdictKind.SKIP_SUPERSEDED


def test_schema_invalid_skip(schema: dict, mock_sdp: dict) -> None:
    # Synthetic sidecar with an unknown top-level field (caught by additionalProperties: false)
    sidecar = {
        "proto": "oaa/media/Synthetic.proto",
        "message": "SyntheticInvalid",
        "confidence": "gold",
        "bogus_field_that_does_not_exist": True,
    }
    sdp_kinds = {c["channel_kind"] for c in mock_sdp["response"]["channels"]}
    verdict = walker_decide(sidecar, Path("oaa/media/synthetic.audit.yaml"), {}, sdp_kinds, {}, schema)
    assert verdict.kind == VerdictKind.SKIP_SCHEMA_INVALID
    assert verdict.skip_reason is not None


def test_out_of_sdp_scope_verdict(schema: dict, mock_sdp: dict) -> None:
    sidecar = _load("sidecar_out_of_sdp_scope.audit.yaml")
    sdp_kinds = {c["channel_kind"] for c in mock_sdp["response"]["channels"]}
    # mock SDP does NOT contain car_local_media_channel
    assert "car_local_media_channel" not in sdp_kinds
    verdict = walker_decide(sidecar, Path("oaa/media/test.audit.yaml"), {}, sdp_kinds, {}, schema)
    assert verdict.kind == VerdictKind.SKIP_OUT_OF_SDP_SCOPE
    assert verdict.skip_reason is not None
    assert "car_local_media" in (verdict.skip_reason or "") or verdict.channel_kind == "car_local_media_channel"


def test_gold_prereq_missing_cv(schema: dict, mock_sdp: dict) -> None:
    sidecar = _load("sidecar_gold_no_cv.audit.yaml")
    sidecar["wire_msg_id"] = "0x8001"
    sdp_kinds = {"av_channel", "media_info_channel"}
    verdict = walker_decide(
        sidecar,
        Path("oaa/video/test.audit.yaml"),
        {("av_channel", 0x8001, "in"): [(2, 20)]},
        sdp_kinds,
        {(0x8001, "in"): "standalone"},
        schema,
    )
    assert verdict.kind == VerdictKind.SKIP_MISSING_GOLD_PREREQ
    assert "Gold prerequisites" in (verdict.skip_reason or "")


def test_match08_only_gold_is_service_binding_not_platinum(schema: dict, mock_sdp: dict) -> None:
    sidecar = _load("sidecar_gold_clean.audit.yaml")
    sdp_kinds = {"av_channel", "media_info_channel"}
    verdict = walker_decide(sidecar, Path("oaa/media/fixture.audit.yaml"), {}, sdp_kinds, {}, schema)
    assert verdict.kind == VerdictKind.NOMATCH_OBSERVATION
    assert verdict.matched_rules == ("MATCH-08",)
    assert verdict.nomatch_rules == ("NOMATCH-02",)
    assert "service_binding_only" in (verdict.skip_reason or "")


def test_match08_only_silver_is_not_pending_gold(schema: dict, mock_sdp: dict) -> None:
    sidecar = _load("sidecar_silver_clean.audit.yaml")
    sdp_kinds = {"av_channel", "media_info_channel"}
    verdict = walker_decide(sidecar, Path("oaa/audio/fixture.audit.yaml"), {}, sdp_kinds, {}, schema)
    assert verdict.kind == VerdictKind.NOMATCH_OBSERVATION
    assert verdict.matched_rules == ("MATCH-08",)
    assert verdict.nomatch_rules == ("NOMATCH-02",)


def test_message_observation_can_promote_eligible_gold(schema: dict) -> None:
    sidecar = _load("sidecar_gold_clean.audit.yaml")
    sidecar["wire_msg_id"] = "0x8001"
    index = {("media_info_channel", 0x8001, "in"): [(7, 1234)]}
    classification = {(0x8001, "in"): "standalone"}
    verdict = walker_decide(
        sidecar,
        Path("oaa/media/fixture.audit.yaml"),
        index,
        {"media_info_channel"},
        classification,
        schema,
    )
    assert verdict.kind == VerdictKind.PROMOTE_TO_PLATINUM
    assert verdict.matched_rules == ("MATCH-08", "MATCH-01", "MATCH-02")
    assert verdict.msg_seq == (7,)
    assert verdict.ts_ms == (1234,)


def test_evidence_builder_rejects_match08_only_verdict() -> None:
    verdict = Verdict(
        sidecar_path="oaa/video/example.audit.yaml",
        proto_message="Example",
        current_tier="gold",
        kind=VerdictKind.PROMOTE_TO_PLATINUM,
        matched_rules=("MATCH-08",),
        msg_seq=(0,),
        ts_ms=(0,),
        message_completeness="full",
        channel_kind="av_channel",
    )
    with pytest.raises(ValueError, match="MATCH-08"):
        _build_platinum_evidence_entry(verdict, "captures/example", "2026-07-25")


def test_content_hash_is_date_independent() -> None:
    """Idempotency: content_hash excludes date so two entries with different dates hash the same."""
    a = {"type": "platinum_evidence", "source": "x", "date": "2026-04-09",
         "description": "same", "match_rules": ["MATCH-08"]}
    b = dict(a, date="2025-01-01")
    assert content_hash(a) == content_hash(b)
