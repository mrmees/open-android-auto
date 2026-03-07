from __future__ import annotations

import pytest

from analysis.tools.proto_stream_validator.filtering import is_phase1_non_media
from analysis.tools.proto_stream_validator.message_map import resolve_message_type
from analysis.tools.proto_stream_validator.models import Frame


def test_resolve_known_control_tuple():
    fqcn = resolve_message_type("Phone->HU", 0, 0x0005)
    assert fqcn == "oaa.proto.messages.ServiceDiscoveryRequest"


def test_resolve_by_service_type():
    fqcn = resolve_message_type("HU->Phone", 99, 0x8001, service_type="input_source")
    assert fqcn == "oaa.proto.messages.InputEventIndication"


def test_resolve_sensor_by_service_type():
    fqcn = resolve_message_type("HU->Phone", 1, 0x8003, service_type="sensor_source")
    assert fqcn == "oaa.proto.messages.SensorEventIndication"


def test_resolve_av_by_service_type():
    fqcn = resolve_message_type("Phone->HU", 2, 0x8000, service_type="media_sink")
    assert fqcn == "oaa.proto.messages.AVChannelSetupRequest"


def test_resolve_nav_by_service_type():
    fqcn = resolve_message_type("Phone->HU", 10, 0x8003, service_type="navigation")
    assert fqcn == "oaa.proto.messages.NavigationState"


def test_resolve_phone_by_service_type():
    fqcn = resolve_message_type("Phone->HU", 11, 0x8001, service_type="phone_status")
    assert fqcn == "oaa.proto.messages.PhoneStatusUpdate"


def test_resolve_media_info_by_service_type():
    fqcn = resolve_message_type("Phone->HU", 12, 0x8001, service_type="media_info")
    assert fqcn == "oaa.proto.messages.MediaPlaybackStatus"


def test_resolve_channel_open_on_any_channel():
    """ChannelOpen appears on every channel, not just ch0."""
    fqcn = resolve_message_type("HU->Phone", 5, 0x0007)
    assert fqcn == "oaa.proto.messages.ChannelOpenRequest"
    fqcn2 = resolve_message_type("Phone->HU", 10, 0x0008)
    assert fqcn2 == "oaa.proto.messages.ChannelOpenResponse"


def test_resolve_uses_message_name_fallback_for_dynamic_channel():
    fqcn = resolve_message_type("HU->Phone", 10, 0x0007, "CHANNEL_OPEN_REQUEST")
    assert fqcn == "oaa.proto.messages.ChannelOpenRequest"


def test_unmapped_tuple_raises_key_error():
    with pytest.raises(KeyError):
        resolve_message_type("Phone->HU", 99, 0x9999)


def test_phase1_filter_excludes_av_media_frames():
    frame = Frame(
        ts_ms=1,
        direction="Phone->HU",
        channel_id=3,
        message_id=0x0001,
        message_name="AV_MEDIA_INDICATION",
        payload_hex="00",
    )
    assert is_phase1_non_media(frame) is False


def test_phase1_filter_excludes_av_media_by_service_type():
    frame = Frame(
        ts_ms=1,
        direction="Phone->HU",
        channel_id=2,
        message_id=0x0000,
        message_name="",
        payload_hex="00",
        service_type="media_sink",
    )
    assert is_phase1_non_media(frame) is False


def test_phase1_filter_excludes_version_and_ssl_control_frames():
    frame = Frame(
        ts_ms=1,
        direction="HU->Phone",
        channel_id=0,
        message_id=0x0001,
        message_name="VERSION_REQUEST",
        payload_hex="00010007",
    )
    assert is_phase1_non_media(frame) is False


def test_phase1_filter_excludes_unresolved_hex_named_frames():
    frame = Frame(
        ts_ms=1,
        direction="Phone->HU",
        channel_id=10,
        message_id=0x8001,
        message_name="0x8001",
        payload_hex="00",
    )
    assert is_phase1_non_media(frame) is False


def test_phase1_filter_excludes_av_media_ack_noise():
    frame = Frame(
        ts_ms=1,
        direction="HU->Phone",
        channel_id=4,
        message_id=0x8004,
        message_name="AV_MEDIA_ACK",
        payload_hex="08001001",
    )
    assert is_phase1_non_media(frame) is False


def test_phase1_filter_keeps_non_media_frames():
    frame = Frame(
        ts_ms=1,
        direction="Phone->HU",
        channel_id=2,
        message_id=0x8001,
        message_name="SENSOR_START_REQUEST",
        payload_hex="08011001",
    )
    assert is_phase1_non_media(frame) is True
