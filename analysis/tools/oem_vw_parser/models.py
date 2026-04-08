from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Direction = Literal["in", "out"]


# ---------------------------------------------------------------------------
# SDP decode dataclasses (added in 07-02 Task 1).
#
# These describe the decoded SDP request and response payloads. PNG icon bytes
# are NEVER stored — only presence and size are recorded so report consumers
# can prove icons were transmitted without dragging 800 bytes of base64 PNG
# through every artifact.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IconPresence:
    """Phone icon presence + size, never the bytes themselves."""

    present: bool
    size_bytes: int


@dataclass(frozen=True)
class SdpRequestInfo:
    """Decoded ServiceDiscoveryRequest (phone -> HU)."""

    device_name: str
    device_brand: str
    session_uuid: str
    icon_small: IconPresence
    icon_medium: IconPresence
    icon_large: IconPresence


@dataclass(frozen=True)
class DeclaredService:
    """One ChannelDescriptor entry from the SDP response.

    `channel_kind` is the populated sub-message field name (e.g.,
    'av_channel', 'sensor_channel', 'navigation_channel'). `config` is the
    json_format.MessageToDict view of that sub-message — empty dict for
    marker-only channels (PhoneStatusChannel, MediaInfoChannel).
    """

    channel_id: int
    channel_kind: str
    config: dict


@dataclass(frozen=True)
class SdpSnapshot:
    """Decoded ServiceDiscoveryResponse (HU -> phone)."""

    head_unit_name: str
    car_model: str
    car_year: str
    car_serial: str
    headunit_manufacturer: str
    headunit_model: str
    sw_build: str
    sw_version: str
    session_configuration: int
    display_name: str
    probe_for_support: bool
    can_play_native_media_during_vr: bool | None
    driver_position: int | None
    head_unit_info: dict
    services: tuple[DeclaredService, ...]


@dataclass(frozen=True)
class UnifiedRecord:
    """A single decoded AA record from any capture source.

    Direction is phone-relative: 'in' = HU→phone, 'out' = phone→HU.
    """

    capture_id: str
    seq: int
    ts_ms: int
    direction: Direction
    msg_type: int
    payload: bytes  # FULL plaintext including the 2-byte msg_type prefix
    payload_len: int
    channel_id: int | None  # None for capture_version=5 (on-phone hook)
    flags: int | None  # None for capture_version=5
    service_type: str | None  # None for capture_version=5


@dataclass(frozen=True)
class WalkedField:
    """One protobuf field observed by the schema-agnostic wire walker."""

    field_num: int
    wire_type: int
    raw_size: int
    value_summary: str  # short repr for fingerprint use; deliberately empty in 07-01


@dataclass(frozen=True)
class WireWalkResult:
    """Result of walking a protobuf payload tag-by-tag.

    `clean_to_eob` is True only when every byte was consumed without error.
    `clean_with_padding` is True only when the walker hit `field=0` (the padding
    sentinel) AFTER walking at least one real field — i.e., trailing zero
    padding on an otherwise valid record.
    """

    fields: tuple[WalkedField, ...]
    consumed: int
    total: int
    error: str | None

    @property
    def clean_to_eob(self) -> bool:
        return self.error is None and self.consumed == self.total

    @property
    def clean_with_padding(self) -> bool:
        return (
            self.error is not None
            and self.error.startswith("field=0")
            and self.consumed > 0
        )


@dataclass(frozen=True)
class ClassifiedRecord:
    """A UnifiedRecord plus its tier, label, and decode evidence."""

    record: UnifiedRecord
    tier: Literal["A", "B", "C"]
    label: Literal[
        "standalone",
        "probable_first",
        "continuation_or_garbage",
        "reassembled",
        "unattributed",
    ]
    walk_result: WireWalkResult | None
    schema_decoded: bool
    freq: int
    low_frequency: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class FrequencyProfile:
    """Per-session frequency derivation result with the histogram for audit."""

    threshold: int
    histogram: dict[tuple[int, str], int]  # (msg_type, direction) → count
    source: str  # justification string for the manifest


# ---------------------------------------------------------------------------
# Attribution dataclass (added in 07-02 Task 3).
#
# The attribution pipeline produces one AttributedRecord per ClassifiedRecord.
# The 5-row attribution taxonomy (07-CONTEXT.md § "Service attribution") is
# enforced by the `attribution_method` literal set. The taxonomy is NEVER
# flattened to a single field — `service`, `candidate_services`, and
# `message_identity` are separate slots.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Coverage manifest dataclasses (added in 07-02 Task 4).
#
# Per 07-CONTEXT.md § "Coverage manifest (OEM-03)" — msg_type-level granularity
# is the floor; the schema is extensible to field-level later without
# breakage. The three-part absence model (observed / gaps.intrinsic /
# gaps.comparative + anomalies) is keyed by (channel_id, channel_kind)
# tuples for the intrinsic side. The top-level channel_kind_summary slot
# preserves kind-level aggregation for consumers that want it.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MsgTypeCoverageEntry:
    """Per-(service, msg_type, direction) coverage entry with temporal profile."""

    service: str | None
    msg_type: int
    direction: str
    count: int
    bytes: int
    first_seen_ts_ms: int
    last_seen_ts_ms: int
    mean_rate_per_sec: float
    observation_span_s: float
    duty_cycle: float
    burstiness: Literal["steady", "bursty", "singleton", "unknown"]
    confidence_distribution: dict
    fields_observed: None  # Phase 7 leaves this None; Phase 9 may populate.


@dataclass(frozen=True)
class CoverageManifest:
    """Aggregated coverage manifest for a single VW capture session."""

    capture_id: str
    capture_duration_s: float
    observed: tuple[dict, ...]                      # entries keyed by (channel_id, channel_kind)
    gaps_intrinsic: tuple[dict, ...]                # entries keyed by (channel_id, channel_kind)
    gaps_comparative: tuple[dict, ...]              # entries keyed by channel_kind only
    anomalies_service_not_declared: tuple[dict, ...]
    anomalies_unattributed: tuple[dict, ...]
    gap_analysis: dict                              # { compared_against_baselines, baseline_snapshot_hash }
    per_msg_type: tuple[MsgTypeCoverageEntry, ...]
    channel_kind_summary: dict                      # {channel_kind: {declared, observed, silent}}


@dataclass(frozen=True)
class AttributedRecord:
    """A ClassifiedRecord plus its service attribution + confidence.

    The `service` field carries the SERVICE binding (e.g., "control",
    "sensor_channel", "navigation_channel"). The `message_identity` field
    carries the MESSAGE TYPE name (e.g., "ServiceDiscoveryRequest", "PingRequest").

    Mixing these in one field muddles the attribution taxonomy. For
    control-plane records (msg_type 0x0000-0x001F), the (msg_type → message
    name) mapping is deterministic via the validator's message_map, so we
    populate `message_identity`. For channel-scoped records (0x8000+),
    msg_type alone does not uniquely identify a proto message (the same
    msg_id can mean different things on different channels), so
    `message_identity` stays None.
    """

    classified: "ClassifiedRecord"
    service: str | None
    candidate_services: tuple[str, ...]
    attribution_method: Literal[
        "deterministic",
        "inferred_by_schema",
        "sdp_narrowed",
        "sdp_candidates",
        "inferred_by_range",
        "unattributed",
    ]
    confidence: Literal["high", "medium", "low", "none"]
    attribution_notes: tuple[str, ...]
    message_identity: str | None
