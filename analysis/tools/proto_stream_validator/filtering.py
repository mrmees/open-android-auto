from __future__ import annotations

from analysis.tools.proto_stream_validator.models import Frame


_AV_CHANNEL_IDS = {3, 4, 5, 6, 7}
_AV_MEDIA_MESSAGE_IDS = {0x0000, 0x0001}


def is_phase1_non_media(frame: Frame) -> bool:
    """Return True when the frame is in scope for phase-1 validation."""
    if frame.channel_id in _AV_CHANNEL_IDS and frame.message_id in _AV_MEDIA_MESSAGE_IDS:
        return False
    return True
