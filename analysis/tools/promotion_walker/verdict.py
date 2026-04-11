from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from analysis.tools.seed_import.generate import validate_audit
from jsonschema.exceptions import ValidationError


class VerdictKind(str, Enum):
    """Possible walker verdicts for a single sidecar."""
    PROMOTE_TO_PLATINUM = "promote_to_platinum"
    FLAG_PENDING_GOLD = "flag_pending_gold"
    NOMATCH_OBSERVATION = "nomatch_observation"
    CONTRADICTION_REVIEW = "contradiction_review"
    SKIP_RETRACTED = "skip_retracted"
    SKIP_SUPERSEDED = "skip_superseded"
    SKIP_ALREADY_PLATINUM = "skip_already_platinum"
    SKIP_SCHEMA_INVALID = "skip_schema_invalid"
    SKIP_MISSING_GOLD_PREREQ = "skip_missing_gold_prereq"
    SKIP_OUT_OF_SDP_SCOPE = "skip_out_of_sdp_scope"


@dataclass(frozen=True)
class Verdict:
    """A single-sidecar walker decision. Frozen so it's hashable and log-friendly."""
    sidecar_path: str
    proto_message: str
    current_tier: str
    kind: VerdictKind
    matched_rules: tuple[str, ...] = ()
    nomatch_rules: tuple[str, ...] = ()
    msg_seq: tuple[int, ...] = ()
    ts_ms: tuple[int, ...] = ()
    message_completeness: str | None = None
    channel_kind: str | None = None
    skip_reason: str | None = None
    contradiction_summary: str | None = None


# Hard-coded: these 3 sidecars bind to car_local_media_channel (NOT in VW SDP)
KNOWN_CAR_LOCAL_MEDIA_PROTOS = frozenset({
    "CarLocalMediaPlaybackStatus",
    "CarLocalMediaPlaybackStatusMessage",
    "CarLocalMediaPlaybackRequest",
    "CarLocalMediaPlaybackRequestMessage",
    "CarLocalMediaPlaybackMetadata",
    "CarLocalMediaPlaybackMetadataMessage",
})


def content_hash(entry: dict[str, Any]) -> str:
    """Stable 16-char sha256 hash of an evidence entry.

    EXCLUDES date and last_updated so walker re-runs on different days dedupe.
    Pattern copied from analysis/tools/cross_version/sidecar_walker.py and
    adapted for platinum_evidence entry shape (10-RESEARCH.md Walker Idempotency Pattern).
    """
    payload = {
        "type": entry.get("type"),
        "source": entry.get("source"),
        "description": entry.get("description"),
        "capture_path": entry.get("capture_path"),
        "vehicle_metadata": entry.get("vehicle_metadata"),
        "msg_seq": entry.get("msg_seq"),
        "ts_ms": entry.get("ts_ms"),
        "message_completeness": entry.get("message_completeness"),
        "attribution_method": entry.get("attribution_method"),
        "oem_scope": entry.get("oem_scope"),
        "applicability": entry.get("applicability"),
        "fields": entry.get("fields"),
        "match_rules": sorted(entry.get("match_rules") or []),
        "nomatch_rules": sorted(entry.get("nomatch_rules") or []),
        # EXCLUDED: date, last_updated (change per run)
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def resolve_channel_binding(
    sidecar: dict[str, Any],
    sidecar_path: Path,
) -> str | None:
    """Resolve a sidecar to its VW-declared channel_kind string.

    Priority:
     1. If proto message is in KNOWN_CAR_LOCAL_MEDIA_PROTOS -> "car_local_media_channel"
        (walker knows this is NOT in VW SDP -- caller will emit SKIP_OUT_OF_SDP_SCOPE)
     2. Directory-based inference:
          oaa/av/ -> "av_channel"
          oaa/audio/ -> "av_channel"
          oaa/video/ -> "av_channel"
          oaa/media/ -> "media_info_channel"
     3. Evidence description text scan for CAR.GAL.{CAR_LOCAL_MEDIA,INST} markers
     4. Default: None (caller emits SKIP_OUT_OF_SDP_SCOPE)
    """
    proto_message = sidecar.get("message", "")
    if proto_message in KNOWN_CAR_LOCAL_MEDIA_PROTOS:
        return "car_local_media_channel"

    # Also check the proto path/filename
    proto = sidecar.get("proto", "")
    for prefix in KNOWN_CAR_LOCAL_MEDIA_PROTOS:
        if prefix in proto:
            return "car_local_media_channel"

    # Directory inference
    path_str = str(sidecar_path).replace("\\", "/")
    for directory, kind in (
        ("/oaa/av/", "av_channel"),
        ("/oaa/audio/", "av_channel"),
        ("/oaa/video/", "av_channel"),
        ("/oaa/media/", "media_info_channel"),
    ):
        if directory in path_str or path_str.startswith(directory.lstrip("/")):
            # Extra check for media/: look at evidence description for CAR_LOCAL_MEDIA
            if directory == "/oaa/media/":
                for ev in sidecar.get("evidence", []):
                    desc = (ev.get("description") or "").lower()
                    if "car_local_media" in desc or "car.gal.car_local_media" in desc or "gal type 20" in desc:
                        return "car_local_media_channel"
                # Also check the channel field
                channel_field = str(sidecar.get("channel", "")).lower()
                if "car_local_media" in channel_field or "gal type 20" in channel_field:
                    return "car_local_media_channel"
            return kind
    return None


def _has_gold_prereqs(sidecar: dict[str, Any]) -> tuple[bool, bool]:
    """Return (has_static, has_cross_version)."""
    evidence = sidecar.get("evidence", [])
    has_static = any(
        e.get("type") in ("apk_static", "apk_deep_trace", "deep_trace")
        for e in evidence
    )
    has_cv = any(e.get("type") == "cross_version" for e in evidence)
    return has_static, has_cv


def _pre_validate(sidecar: dict[str, Any], schema: dict) -> tuple[bool, str | None]:
    """Validate against schema before any edit. Returns (ok, reason)."""
    try:
        validate_audit(sidecar)
        return True, None
    except ValidationError as e:
        return False, f"pre_existing_invalid: {str(e.message)[:120]}"
    except Exception as e:
        return False, f"unexpected_validation_error: {str(e)[:120]}"


def walker_decide(
    sidecar: dict[str, Any],
    sidecar_path: Path,
    index: dict[tuple[str, int, str], list[tuple[int, int]]],
    sdp_kinds: set[str],
    classification: dict[tuple[int, str], str],
    schema: dict | None = None,
) -> Verdict:
    """Pure function -- decide a single sidecar's verdict. See 10-RESEARCH.md Example 2.

    Order of checks matters -- first match wins:
      1. Tier-state skips (platinum, retracted, superseded)
      2. Pre-validate against schema
      3. Channel binding resolution
      4. MATCH-08 (SDP) check
      5. Gold vs Silver/Bronze routing
    """
    proto_msg = sidecar.get("message", "?")
    current_tier = sidecar.get("confidence", "unverified")

    # (1) Tier-state skips
    if current_tier == "platinum":
        return Verdict(
            sidecar_path=str(sidecar_path),
            proto_message=proto_msg,
            current_tier=current_tier,
            kind=VerdictKind.SKIP_ALREADY_PLATINUM,
            skip_reason="already_platinum",
        )
    if current_tier == "retracted":
        return Verdict(
            sidecar_path=str(sidecar_path),
            proto_message=proto_msg,
            current_tier=current_tier,
            kind=VerdictKind.SKIP_RETRACTED,
            skip_reason="confidence: retracted",
        )
    if current_tier == "superseded":
        return Verdict(
            sidecar_path=str(sidecar_path),
            proto_message=proto_msg,
            current_tier=current_tier,
            kind=VerdictKind.SKIP_SUPERSEDED,
            skip_reason="confidence: superseded",
        )

    # (2) Pre-validate
    if schema is not None:
        ok, reason = _pre_validate(sidecar, schema)
        if not ok:
            return Verdict(
                sidecar_path=str(sidecar_path),
                proto_message=proto_msg,
                current_tier=current_tier,
                kind=VerdictKind.SKIP_SCHEMA_INVALID,
                skip_reason=reason,
            )

    # (3) Channel binding
    channel_kind = resolve_channel_binding(sidecar, sidecar_path)
    if channel_kind is None:
        return Verdict(
            sidecar_path=str(sidecar_path),
            proto_message=proto_msg,
            current_tier=current_tier,
            kind=VerdictKind.SKIP_OUT_OF_SDP_SCOPE,
            skip_reason="no_channel_binding_resolved",
        )

    # (4) MATCH-08 baseline
    if channel_kind not in sdp_kinds:
        return Verdict(
            sidecar_path=str(sidecar_path),
            proto_message=proto_msg,
            current_tier=current_tier,
            kind=VerdictKind.SKIP_OUT_OF_SDP_SCOPE,
            channel_kind=channel_kind,
            skip_reason=f"channel_kind_not_in_vw_sdp: {channel_kind}",
        )

    # Walker cites MATCH-08 as baseline; additional MATCH rules may fire below
    matched_rules = ["MATCH-08"]
    msg_seq_list: list[int] = []
    ts_ms_list: list[int] = []
    completeness: str | None = None

    # Look up message-level observations (rare in Phase 10 based on empirical data)
    wire_msg_id = sidecar.get("wire_msg_id")
    if wire_msg_id is not None:
        try:
            mid_str = str(wire_msg_id)
            mid = int(mid_str.replace("0x", ""), 16 if "x" in mid_str.lower() else 10)
        except (ValueError, TypeError):
            mid = None
        if mid is not None:
            for direction in ("in", "out"):
                observations = index.get((channel_kind, mid, direction), [])
                for seq, ts in observations:
                    label = classification.get((mid, direction))
                    if label in ("continuation_or_garbage", "unattributed"):
                        continue  # rejected as evidence
                    if "MATCH-01" not in matched_rules:
                        matched_rules.append("MATCH-01")
                    if label == "standalone":
                        if "MATCH-02" not in matched_rules:
                            matched_rules.append("MATCH-02")
                        completeness = "full"
                    elif label == "reassembled":
                        if "MATCH-03" not in matched_rules:
                            matched_rules.append("MATCH-03")
                        completeness = "full"
                    elif label == "probable_first":
                        completeness = "first_only"
                    msg_seq_list.append(seq)
                    ts_ms_list.append(ts)

    if completeness is None:
        completeness = "full"  # MATCH-08 only; Phase 9 precedent
    if not msg_seq_list:
        msg_seq_list = [0]
        ts_ms_list = [0]

    # Repeat / cross-direction (MATCH-06 / MATCH-07)
    if len(msg_seq_list) >= 2:
        if "MATCH-06" not in matched_rules:
            matched_rules.append("MATCH-06")

    # (5) Tier-specific routing
    if current_tier == "gold":
        has_static, has_cv = _has_gold_prereqs(sidecar)
        if not (has_static and has_cv):
            return Verdict(
                sidecar_path=str(sidecar_path),
                proto_message=proto_msg,
                current_tier=current_tier,
                kind=VerdictKind.SKIP_MISSING_GOLD_PREREQ,
                channel_kind=channel_kind,
                skip_reason=f"static={has_static}, cross_version={has_cv}",
            )
        return Verdict(
            sidecar_path=str(sidecar_path),
            proto_message=proto_msg,
            current_tier=current_tier,
            kind=VerdictKind.PROMOTE_TO_PLATINUM,
            matched_rules=tuple(matched_rules),
            msg_seq=tuple(msg_seq_list),
            ts_ms=tuple(ts_ms_list),
            message_completeness=completeness,
            channel_kind=channel_kind,
        )

    if current_tier in ("silver", "bronze"):
        return Verdict(
            sidecar_path=str(sidecar_path),
            proto_message=proto_msg,
            current_tier=current_tier,
            kind=VerdictKind.FLAG_PENDING_GOLD,
            matched_rules=tuple(matched_rules),
            msg_seq=tuple(msg_seq_list),
            ts_ms=tuple(ts_ms_list),
            message_completeness=completeness,
            channel_kind=channel_kind,
        )

    # Unknown tier -- treat as schema-invalid
    return Verdict(
        sidecar_path=str(sidecar_path),
        proto_message=proto_msg,
        current_tier=current_tier,
        kind=VerdictKind.SKIP_SCHEMA_INVALID,
        skip_reason=f"unknown_tier: {current_tier}",
    )
