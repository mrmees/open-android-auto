from __future__ import annotations

from pathlib import Path
from typing import Literal

from google.protobuf import json_format, message_factory

from analysis.tools.proto_stream_validator.descriptors import DescriptorBundle

from .models import (
    DeclaredService,
    IconPresence,
    SdpRequestInfo,
    SdpSnapshot,
)


# ChannelDescriptor sub-message field names, in field-number order. Each
# entry maps to a populated channel kind via `HasField(name)`. The order
# matches `oaa/control/ChannelDescriptorData.proto`. Field numbers are
# the canonical "channel_kind" identifiers used everywhere downstream
# (attribution, coverage, override schema).
_CHANNEL_SUB_FIELDS = (
    "sensor_channel",            # 2
    "av_channel",                # 3
    "input_channel",             # 4
    "av_input_channel",          # 5
    "bluetooth_channel",         # 6
    "radio_channel",             # 7
    "navigation_channel",        # 8
    "media_info_channel",        # 9
    "phone_status_channel",      # 10
    "media_browser_channel",     # 11
    "vendor_extension_channel",  # 12
    "notification_channel",      # 13
    "wifi_channel",              # 14
    "car_control_channel",       # 15
    "generic_notification_channel",  # 16
    "voice_channel",             # 17
)


def _message_class(bundle: DescriptorBundle, fqn: str):
    """Resolve a fully-qualified proto type to its message class via the
    descriptor pool. Mirrors the validator's _message_class_for_descriptor
    pattern but uses GetMessageClass directly.
    """
    desc = bundle.pool.FindMessageTypeByName(fqn)
    return message_factory.GetMessageClass(desc)


def decode_sdp_response(bundle: DescriptorBundle, path: Path) -> SdpSnapshot:
    """Decode `sdp_response.bin` (HU -> phone) into an SdpSnapshot.

    Iterates the ChannelDescriptor entries and resolves each one's populated
    sub-message field name. The sub-message dict is rendered via
    json_format.MessageToDict with `preserving_proto_field_name=True` so
    snake_case field names survive the round-trip.
    """
    cls = _message_class(bundle, "oaa.proto.messages.ServiceDiscoveryResponse")
    msg = cls()
    msg.ParseFromString(Path(path).read_bytes())

    services: list[DeclaredService] = []
    for ch in msg.channels:
        kind = next((f for f in _CHANNEL_SUB_FIELDS if ch.HasField(f)), "unknown")
        if kind == "unknown":
            # Channel descriptor with only channel_id populated. Record it as
            # 'unknown' rather than dropping it — anomalies should be visible.
            services.append(
                DeclaredService(channel_id=ch.channel_id, channel_kind="unknown", config={})
            )
            continue
        sub = getattr(ch, kind)
        cfg = json_format.MessageToDict(sub, preserving_proto_field_name=True)
        services.append(
            DeclaredService(channel_id=ch.channel_id, channel_kind=kind, config=cfg)
        )

    head_unit_info_dict: dict = {}
    if msg.HasField("headunit_info"):
        head_unit_info_dict = json_format.MessageToDict(
            msg.headunit_info, preserving_proto_field_name=True
        )

    return SdpSnapshot(
        head_unit_name=msg.head_unit_name,
        car_model=msg.car_model,
        car_year=msg.car_year,
        car_serial=msg.car_serial,
        headunit_manufacturer=msg.headunit_manufacturer,
        headunit_model=msg.headunit_model,
        sw_build=msg.sw_build,
        sw_version=msg.sw_version,
        session_configuration=msg.session_configuration,
        display_name=msg.display_name,
        probe_for_support=msg.probe_for_support,
        can_play_native_media_during_vr=(
            msg.can_play_native_media_during_vr
            if msg.HasField("can_play_native_media_during_vr")
            else None
        ),
        driver_position=(
            int(msg.driver_position) if msg.HasField("driver_position") else None
        ),
        head_unit_info=head_unit_info_dict,
        services=tuple(services),
    )


def decode_sdp_request(bundle: DescriptorBundle, path: Path) -> SdpRequestInfo:
    """Decode `sdp_request.bin` (phone -> HU) into an SdpRequestInfo.

    Captures icon presence + size only — the raw PNG bytes are NEVER stored
    on the dataclass surface. Reports get to prove icons were transmitted
    without dragging hundreds of bytes of base64 PNG through every artifact.
    """
    cls = _message_class(bundle, "oaa.proto.messages.ServiceDiscoveryRequest")
    msg = cls()
    msg.ParseFromString(Path(path).read_bytes())

    def _icon(field_name: str) -> IconPresence:
        if msg.HasField(field_name):
            return IconPresence(
                present=True, size_bytes=len(getattr(msg, field_name))
            )
        return IconPresence(present=False, size_bytes=0)

    session_uuid = ""
    if msg.HasField("session_info"):
        session_uuid = msg.session_info.session_uuid

    return SdpRequestInfo(
        device_name=msg.device_name,
        device_brand=msg.device_brand,
        session_uuid=session_uuid,
        icon_small=_icon("phone_icon_small"),
        icon_medium=_icon("phone_icon_medium"),
        icon_large=_icon("phone_icon_large"),
    )


def determine_sdp_direction(
    bundle: DescriptorBundle, path: Path
) -> Literal["request", "response"]:
    """Determine SDP direction by decode success, NOT by file name or README.

    Returns 'request' for phone -> HU bins, 'response' for HU -> phone bins.
    This function is the ground-truth direction resolver — anyone who tries
    to "fix" the capture README's swapped direction labels and accidentally
    relabels the decoder will fail the test_direction_resolution test.
    """
    data = Path(path).read_bytes()

    req_cls = _message_class(bundle, "oaa.proto.messages.ServiceDiscoveryRequest")
    req_msg = req_cls()
    resp_cls = _message_class(bundle, "oaa.proto.messages.ServiceDiscoveryResponse")
    resp_msg = resp_cls()

    req_ok = False
    resp_ok = False
    try:
        req_msg.ParseFromString(data)
        req_ok = (
            req_msg.HasField("device_name")
            or req_msg.HasField("device_brand")
            or req_msg.HasField("phone_icon_small")
        )
    except Exception:  # noqa: BLE001 — protobuf raises bare exceptions
        req_ok = False
    try:
        resp_msg.ParseFromString(data)
        resp_ok = (
            bool(resp_msg.head_unit_name)
            or bool(resp_msg.car_model)
            or len(resp_msg.channels) > 0
        )
    except Exception:  # noqa: BLE001 — protobuf raises bare exceptions
        resp_ok = False

    if resp_ok and not req_ok:
        return "response"
    if req_ok and not resp_ok:
        return "request"
    # Both decode non-trivially or both fail: prefer the one with more
    # populated fields. ServiceDiscoveryRequest has 6 fields, Response has
    # 14+; the field count is a reliable disambiguator on real bins.
    req_fields = len(list(req_msg.ListFields()))
    resp_fields = len(list(resp_msg.ListFields()))
    if resp_fields > req_fields:
        return "response"
    if req_fields > resp_fields:
        return "request"
    raise ValueError(f"could not determine SDP direction for {path}")
