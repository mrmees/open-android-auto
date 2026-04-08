from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from analysis.tools.proto_stream_validator.message_map import resolve_message_type

from .models import (
    AttributedRecord,
    ClassifiedRecord,
    SdpSnapshot,
    WireWalkResult,
)


# Path to the committed pre-flight result. Loaded once at module import.
# This file MUST exist by the time attribution runs — Task 2 of plan 07-02
# is the pre-flight task that creates it. Reading at module load means there
# is no per-record file I/O, and the surviving_hints list is identical across
# every call to attribute_record().
_DATA_DIR = Path(__file__).parent / "data"

# Control-plane msg_type range. Per CONTEXT.md § "Service attribution":
# "Control plane (0x0000-0x001F) = globally unique IDs. 0x0005 is always
# ServiceDiscoveryRequest, no matter where it appears."
CONTROL_PLANE_RANGE = range(0x0000, 0x0020)


def _load_range_hints() -> dict:
    p = _DATA_DIR / "range_hints.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    # Defensive fallback if Task 2 didn't run yet — never falsely attribute.
    return {"surviving_hints": [], "dropped_hints": []}


# Module-load time read. The attribution code path uses this dict directly
# unless the caller passes their own range_hints (used by tests).
RANGE_HINTS = _load_range_hints()


# ---------------------------------------------------------------------------
# Structural fingerprint shape predicates.
#
# Per 07-CONTEXT.md § Claude's Discretion:
#   "Phase 7 only needs enough shape profiles to reasonably narrow SDP
#    candidates for the 13 VW channels."
#
# Each predicate takes a wire_walk result and a payload length and returns
# True if the record's structural fingerprint is consistent with the channel
# kind. The predicates are deliberately loose — they're a TIER B narrower,
# not a verifier. The taxonomy handles overlap correctly:
#   - 1 match → sdp_narrowed (medium confidence, accept the binding)
#   - >1 match → sdp_candidates (low confidence, do NOT pick)
#   - 0 matches → unattributed
# ---------------------------------------------------------------------------


ShapePredicate = Callable[[WireWalkResult | None, int], bool]


def _is_sensor_shape(walk: WireWalkResult | None, payload_len: int) -> bool:
    """Sensor channel shape: varint-heavy, small/medium body."""
    if walk is None or not walk.fields:
        return False
    varint_fraction = sum(1 for f in walk.fields if f.wire_type == 0) / max(
        1, len(walk.fields)
    )
    return varint_fraction >= 0.7 and payload_len < 128


def _is_navigation_shape(walk: WireWalkResult | None, payload_len: int) -> bool:
    """Navigation channel shape: has length-delimited fields (strings/sub-msgs)."""
    if walk is None or not walk.fields:
        return False
    return any(f.wire_type == 2 for f in walk.fields) and 10 < payload_len < 512


def _is_av_shape(walk: WireWalkResult | None, payload_len: int) -> bool:
    """AV channel shape: mostly length-delimited, larger bodies."""
    if walk is None or not walk.fields:
        return False
    ld_fraction = sum(1 for f in walk.fields if f.wire_type == 2) / max(
        1, len(walk.fields)
    )
    return ld_fraction >= 0.5 and payload_len >= 64


def _is_av_input_shape(walk: WireWalkResult | None, payload_len: int) -> bool:
    """AV input channel shape: small varint-heavy control/status (NOT PCM)."""
    if walk is None or not walk.fields:
        return False
    return payload_len < 32


def _is_bluetooth_shape(walk: WireWalkResult | None, payload_len: int) -> bool:
    """Bluetooth channel shape: small/medium body with a string field."""
    if walk is None or not walk.fields:
        return False
    return any(f.wire_type == 2 for f in walk.fields) and payload_len < 256


_SHAPE_PROFILES: dict[str, ShapePredicate] = {
    "sensor_channel": _is_sensor_shape,
    "navigation_channel": _is_navigation_shape,
    "av_channel": _is_av_shape,
    "av_input_channel": _is_av_input_shape,
    "bluetooth_channel": _is_bluetooth_shape,
}


def _narrow_by_sdp(
    walk: WireWalkResult | None,
    payload_len: int,
    sdp: SdpSnapshot,
) -> list[str]:
    """Match the structural fingerprint against shape profiles for ONLY
    SDP-declared services. Profiles for services VW didn't declare are
    skipped — that's the whole point of SDP narrowing.
    """
    declared_kinds = {s.channel_kind for s in sdp.services}
    candidates: list[str] = []
    for kind, predicate in _SHAPE_PROFILES.items():
        if kind in declared_kinds and predicate(walk, payload_len):
            candidates.append(kind)
    return candidates


def attribute_record(
    classified: ClassifiedRecord,
    sdp: SdpSnapshot,
    range_hints: dict | None = None,
) -> AttributedRecord:
    """Apply the 5-row attribution taxonomy to a single ClassifiedRecord.

    See 07-CONTEXT.md § "Hard attribution taxonomy" for the rules. The
    `vendor_extension_channel` code path stays in for forward compatibility
    but produces no output for VW (which declares none).
    """
    if range_hints is None:
        range_hints = RANGE_HINTS

    record = classified.record

    # ------------------------------------------------------------------
    # Skip fragments. Garbage records do not get attributed.
    # ------------------------------------------------------------------
    if classified.label == "continuation_or_garbage":
        return AttributedRecord(
            classified=classified,
            service=None,
            candidate_services=(),
            attribution_method="unattributed",
            confidence="none",
            attribution_notes=("skipped_garbage",),
            message_identity=None,
        )

    # ------------------------------------------------------------------
    # Row 1: Control plane + Tier A → deterministic.
    # message_identity is populated via the validator's message_map.
    # service is the binding ("control"); message_identity is the proto name.
    # ------------------------------------------------------------------
    if record.msg_type in CONTROL_PLANE_RANGE and classified.tier == "A":
        message_identity: str | None = None
        try:
            fqn = resolve_message_type(
                direction=record.direction,
                channel_id=0,
                message_id=record.msg_type,
                message_name=None,
                service_type=None,
            )
            # Strip the package prefix; report the bare message name.
            message_identity = fqn.split(".")[-1]
        except (KeyError, AttributeError):
            message_identity = None
        return AttributedRecord(
            classified=classified,
            service="control",
            candidate_services=("control",),
            attribution_method="deterministic",
            confidence="high",
            attribution_notes=("control_plane_descriptor_match",),
            message_identity=message_identity,
        )

    # ------------------------------------------------------------------
    # Row 2: Channel-scoped + Tier A → inferred_by_schema.
    # The descriptor match is real but msg_type alone doesn't pin down the
    # channel — same ID can appear on multiple channels. Candidates are the
    # SDP-declared channel kinds.
    # ------------------------------------------------------------------
    if classified.tier == "A" and record.msg_type >= 0x8000:
        declared_kinds = tuple(sorted({s.channel_kind for s in sdp.services}))
        return AttributedRecord(
            classified=classified,
            service=None,
            candidate_services=declared_kinds,
            attribution_method="inferred_by_schema",
            confidence="medium",
            attribution_notes=("tier_a_channel_scoped_descriptor_match",),
            message_identity=None,
        )

    # ------------------------------------------------------------------
    # Tier B: SDP narrowing via structural fingerprint.
    # ------------------------------------------------------------------
    if classified.tier == "B":
        payload_len = len(record.payload)
        matches = _narrow_by_sdp(classified.walk_result, payload_len, sdp)

        # Row 3: Exactly one match → sdp_narrowed.
        if len(matches) == 1:
            return AttributedRecord(
                classified=classified,
                service=matches[0],
                candidate_services=tuple(matches),
                attribution_method="sdp_narrowed",
                confidence="medium",
                attribution_notes=("sdp_narrowed_via_structural_fingerprint",),
                message_identity=None,
            )

        # Row 4: Multiple matches → consult range hints (tiebreaker only).
        if len(matches) > 1:
            surviving = [
                h
                for h in range_hints.get("surviving_hints", [])
                if h.get("claimed_service") in matches
            ]
            range_matching = [
                h
                for h in surviving
                if h.get("range_lo", 0) <= record.msg_type <= h.get("range_hi", -1)
            ]
            if len(range_matching) == 1:
                svc = range_matching[0]["claimed_service"]
                return AttributedRecord(
                    classified=classified,
                    service=svc,
                    candidate_services=tuple(matches),
                    attribution_method="inferred_by_range",
                    confidence="low",
                    attribution_notes=("tiebreaker_via_range_hint",),
                    message_identity=None,
                )
            return AttributedRecord(
                classified=classified,
                service=None,
                candidate_services=tuple(matches),
                attribution_method="sdp_candidates",
                confidence="low",
                attribution_notes=("sdp_multiple_candidates",),
                message_identity=None,
            )

        # Row 5: Zero matches → unattributed.
        # Vendor-extension surfacing stays in as a forward-compat hook.
        # For VW (no vendor_extension_channel declared) this branch never
        # adds the probable_vendor_extension note.
        declared_kinds = {s.channel_kind for s in sdp.services}
        notes = ["sdp_narrowing_returned_zero"]
        if "vendor_extension_channel" in declared_kinds:
            notes.append("probable_vendor_extension")
        return AttributedRecord(
            classified=classified,
            service=None,
            candidate_services=(),
            attribution_method="unattributed",
            confidence="none",
            attribution_notes=tuple(notes),
            message_identity=None,
        )

    # Tier C records that somehow weren't caught by the garbage skip earlier
    # (label != continuation_or_garbage but tier == C). Fall through to
    # unattributed — never silently drop.
    return AttributedRecord(
        classified=classified,
        service=None,
        candidate_services=(),
        attribution_method="unattributed",
        confidence="none",
        attribution_notes=("fallthrough",),
        message_identity=None,
    )
