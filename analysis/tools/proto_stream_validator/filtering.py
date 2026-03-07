from __future__ import annotations

from analysis.tools.proto_stream_validator.models import Frame


_AV_CHANNEL_IDS = {3, 4, 5, 6, 7}
_AV_SERVICE_TYPES = {"media_sink"}
_AV_MEDIA_MESSAGE_IDS = {0x0000, 0x0001}
# Valid proto message IDs on AV channels (everything else is raw media data)
_AV_PROTO_MESSAGE_IDS = set(range(0x8000, 0x8009)) | {0x0007, 0x0008}
_NON_PROTO_CONTROL_IDS = {0x0000, 0x0001, 0x0002, 0x0003}
_IGNORED_NOISE_MESSAGE_NAMES = {"AV_MEDIA_ACK"}


def _is_av_channel(frame: Frame) -> bool:
    """Check if frame is on an AV channel (by service_type or legacy channel_id)."""
    if frame.service_type:
        return frame.service_type in _AV_SERVICE_TYPES
    return frame.channel_id in _AV_CHANNEL_IDS


def is_phase1_non_media(frame: Frame) -> bool:
    """Return True when the frame is in scope for phase-1 validation."""
    # Skip version exchange, SSL handshake, padding on control channel
    if frame.channel_id == 0 and frame.message_id in _NON_PROTO_CONTROL_IDS:
        return False
    # On AV channels: skip raw media data AND only allow known proto msg IDs
    if _is_av_channel(frame):
        if frame.message_id in _AV_MEDIA_MESSAGE_IDS:
            return False
        if frame.message_id not in _AV_PROTO_MESSAGE_IDS:
            return False
    # Skip AV_MEDIA_ACK noise
    if frame.message_name in _IGNORED_NOISE_MESSAGE_NAMES:
        return False
    # Skip frames with unresolved hex names (no proto mapping yet)
    if frame.message_name.startswith("0x"):
        return False
    return True
