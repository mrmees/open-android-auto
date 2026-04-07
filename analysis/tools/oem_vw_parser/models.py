from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Direction = Literal["in", "out"]


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
