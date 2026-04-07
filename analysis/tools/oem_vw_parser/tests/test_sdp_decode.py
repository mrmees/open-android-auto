from __future__ import annotations

from dataclasses import fields as dataclass_fields

from analysis.tools.oem_vw_parser.models import (
    IconPresence,
    SdpRequestInfo,
    SdpSnapshot,
)
from analysis.tools.oem_vw_parser.sdp_decode import (
    decode_sdp_request,
    decode_sdp_response,
    determine_sdp_direction,
)


def test_sdp_request(bundle, sdp_request_path):
    """ServiceDiscoveryRequest decodes with phone identity fields populated.

    Source: real `sdp_request.bin` from VW MIB3 OI 2026-04-06 capture.
    Direction: phone -> HU.
    """
    info = decode_sdp_request(bundle, sdp_request_path)

    assert isinstance(info, SdpRequestInfo)
    assert info.device_name == "Android"
    assert info.device_brand == "Google Pixel 8"
    assert info.session_uuid == "ba64e7d4-6347-47cd-9234-fb3cc41c5249"

    assert info.icon_small.present is True
    assert info.icon_small.size_bytes > 0
    assert info.icon_medium.present is True
    assert info.icon_medium.size_bytes > 0
    assert info.icon_large.present is True
    assert info.icon_large.size_bytes > 0

    # Hard guarantee: no PNG bytes embedded anywhere in the dataclass surface.
    # Every field on SdpRequestInfo and IconPresence must be a primitive
    # (str/int/bool) — no `bytes` payloads. The icon bytes never leave the
    # decoder; presence + size are the only thing reports get to see.
    for f in dataclass_fields(SdpRequestInfo):
        v = getattr(info, f.name)
        assert not isinstance(v, bytes), (
            f"SdpRequestInfo.{f.name} must not be bytes (got {type(v).__name__})"
        )
    for icon in (info.icon_small, info.icon_medium, info.icon_large):
        for f in dataclass_fields(IconPresence):
            v = getattr(icon, f.name)
            assert not isinstance(v, bytes), (
                f"IconPresence.{f.name} must not be bytes"
            )


def test_sdp_response(bundle, sdp_response_path):
    """ServiceDiscoveryResponse decodes with HeadUnitInfo + 13 channels.

    Source: real `sdp_response.bin` from VW MIB3 OI 2026-04-06 capture.
    Direction: HU -> phone.
    """
    snap = decode_sdp_response(bundle, sdp_response_path)

    assert isinstance(snap, SdpSnapshot)
    assert snap.head_unit_name == "Volkswagen"
    assert snap.car_model == "VW3363"
    assert snap.car_year == "2024"
    assert snap.car_serial == "092f7b7ed5024eb0"
    assert snap.headunit_manufacturer == "LGE"
    assert snap.headunit_model == "COCKPIT_MIB3OI_GP"
    assert snap.sw_build == "C sample"
    assert snap.sw_version == "2756.04"
    assert snap.session_configuration == 1
    assert snap.display_name == "Volkswagen"
    assert snap.probe_for_support is False
    assert len(snap.services) == 13

    # HeadUnitInfo sub-message extracted as a dict (preserving_proto_field_name).
    assert isinstance(snap.head_unit_info, dict)
    assert snap.head_unit_info.get("make") == "Volkswagen"
    assert snap.head_unit_info.get("model") == "VW3363"
    assert snap.head_unit_info.get("year") == "2024"


def test_channel_set(bundle, sdp_response_path):
    """The 13 declared channels enumerate to the exact set from
    07-RESEARCH.md Correction 1. NO radio, NO car_control, NO vendor_extension,
    NO notification, NO voice, NO media_browser, NO generic_notification.
    """
    snap = decode_sdp_response(bundle, sdp_response_path)
    declared = {(s.channel_id, s.channel_kind) for s in snap.services}

    expected = {
        (1, "av_channel"),
        (2, "input_channel"),
        (3, "av_channel"),
        (4, "av_channel"),
        (5, "av_channel"),
        (6, "av_channel"),
        (7, "av_input_channel"),
        (8, "sensor_channel"),
        (9, "bluetooth_channel"),
        (10, "media_info_channel"),
        (11, "phone_status_channel"),
        (12, "navigation_channel"),
        (13, "wifi_channel"),
    }
    assert declared == expected, f"channel set mismatch: {declared ^ expected}"

    # Negative: forbidden channel kinds for this capture.
    forbidden = {
        "radio_channel",
        "media_browser_channel",
        "vendor_extension_channel",
        "notification_channel",
        "car_control_channel",
        "generic_notification_channel",
        "voice_channel",
    }
    declared_kinds = {s.channel_kind for s in snap.services}
    assert declared_kinds.isdisjoint(forbidden), (
        f"forbidden channels declared: {declared_kinds & forbidden}"
    )


def test_direction_resolution(bundle, sdp_request_path, sdp_response_path):
    """Direction is determined by decode, NOT by file name or README.

    This locks in the corrected direction. Anyone who tries to "fix" the
    README and break the decoder will fail this test.
    """
    assert determine_sdp_direction(bundle, sdp_request_path) == "request"
    assert determine_sdp_direction(bundle, sdp_response_path) == "response"
