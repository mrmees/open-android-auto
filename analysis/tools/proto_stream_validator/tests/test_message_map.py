from __future__ import annotations

import pytest

from analysis.tools.proto_stream_validator.filtering import is_phase1_non_media  # type: ignore[attr-defined]
from analysis.tools.proto_stream_validator.message_map import resolve_message_type  # type: ignore[attr-defined]
from analysis.tools.proto_stream_validator.models import Frame


def test_resolve_known_control_tuple():
    fqcn = resolve_message_type("Phone->HU", 0, 0x0005)
    assert fqcn == "oaa.proto.messages.ServiceDiscoveryRequest"


def test_resolve_known_sensor_tuple():
    fqcn = resolve_message_type("HU->Phone", 2, 0x8003)
    assert fqcn == "oaa.proto.messages.SensorEventIndication"


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
