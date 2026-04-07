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
