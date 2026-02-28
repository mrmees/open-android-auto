from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Frame:
    ts_ms: float
    direction: str
    channel_id: int
    message_id: int
    message_name: str
    payload_hex: str


@dataclass(frozen=True)
class NormalizedFrame:
    frame_index: int
    direction: str
    channel_id: int
    message_id: int
    message_type: str
    decoded: dict[str, Any]
