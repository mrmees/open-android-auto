from __future__ import annotations

from analysis.tools.proto_stream_validator.models import Frame


_AV_CHANNEL_IDS = {3, 4, 5, 6, 7}
_AV_MEDIA_MESSAGE_IDS = {0x0000, 0x0001}
_NON_PROTO_CONTROL_IDS = {0x0001, 0x0002, 0x0003}
_IGNORED_NOISE_MESSAGE_NAMES = {"AV_MEDIA_ACK"}


def is_phase1_non_media(frame: Frame) -> bool:
    """Return True when the frame is in scope for phase-1 validation."""
    if frame.channel_id == 0 and frame.message_id in _NON_PROTO_CONTROL_IDS:
        return False
    if frame.channel_id in _AV_CHANNEL_IDS and frame.message_id in _AV_MEDIA_MESSAGE_IDS:
        return False
    if frame.message_name in _IGNORED_NOISE_MESSAGE_NAMES:
        return False
    if frame.message_name.startswith("0x"):
        return False
    return True
