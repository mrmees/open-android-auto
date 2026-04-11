from __future__ import annotations
import json
from pathlib import Path

import pytest
import yaml

from analysis.tools.promotion_walker.verdict import (
    Verdict, VerdictKind, walker_decide, content_hash,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_already_platinum_skip(schema: dict, mock_sdp: dict) -> None:
    sidecar = _load("sidecar_already_platinum.audit.yaml")
    sdp_kinds = {c["channel_kind"] for c in mock_sdp["response"]["channels"]}
    verdict = walker_decide(sidecar, Path("oaa/video/test.audit.yaml"), {}, sdp_kinds, {}, schema)
    assert verdict.kind == VerdictKind.SKIP_ALREADY_PLATINUM


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
    sdp_kinds = {"av_channel", "media_info_channel"}
    verdict = walker_decide(sidecar, Path("oaa/video/test.audit.yaml"), {}, sdp_kinds, {}, schema)
    assert verdict.kind == VerdictKind.SKIP_MISSING_GOLD_PREREQ
    assert "cross_version=False" in (verdict.skip_reason or "")


def test_promote_clean_gold(schema: dict, mock_sdp: dict) -> None:
    sidecar = _load("sidecar_gold_clean.audit.yaml")
    sdp_kinds = {"av_channel", "media_info_channel"}
    # The fixture is oaa/media/FixtureMediaPlaybackStatusMessage -- should resolve to media_info_channel
    verdict = walker_decide(sidecar, Path("oaa/media/fixture.audit.yaml"), {}, sdp_kinds, {}, schema)
    assert verdict.kind == VerdictKind.PROMOTE_TO_PLATINUM
    assert "MATCH-08" in verdict.matched_rules
    # Walker never cites MATCH-04 or MATCH-05
    assert "MATCH-04" not in verdict.matched_rules
    assert "MATCH-05" not in verdict.matched_rules


def test_silver_pending_gold(schema: dict, mock_sdp: dict) -> None:
    sidecar = _load("sidecar_silver_clean.audit.yaml")
    sdp_kinds = {"av_channel", "media_info_channel"}
    # Fixture is oaa/audio/ -> av_channel binding
    verdict = walker_decide(sidecar, Path("oaa/audio/fixture.audit.yaml"), {}, sdp_kinds, {}, schema)
    assert verdict.kind == VerdictKind.FLAG_PENDING_GOLD
    assert verdict.matched_rules == ("MATCH-08",)


def test_content_hash_is_date_independent() -> None:
    """Idempotency: content_hash excludes date so two entries with different dates hash the same."""
    a = {"type": "platinum_evidence", "source": "x", "date": "2026-04-09",
         "description": "same", "match_rules": ["MATCH-08"]}
    b = dict(a, date="2025-01-01")
    assert content_hash(a) == content_hash(b)
