from __future__ import annotations

from analysis.tools.oem_vw_parser.attribution import (
    CONTROL_PLANE_RANGE,
    attribute_record,
)
from analysis.tools.oem_vw_parser.models import (
    AttributedRecord,
    ClassifiedRecord,
    DeclaredService,
    SdpSnapshot,
    UnifiedRecord,
    WalkedField,
    WireWalkResult,
)
from analysis.tools.oem_vw_parser.sdp_decode import decode_sdp_response


def make_record(
    msg_type: int,
    direction: str = "out",
    payload: bytes = b"",
) -> UnifiedRecord:
    return UnifiedRecord(
        capture_id="test",
        seq=0,
        ts_ms=0,
        direction=direction,  # type: ignore[arg-type]
        msg_type=msg_type,
        payload=payload,
        payload_len=len(payload),
        channel_id=None,
        flags=None,
        service_type=None,
    )


def make_classified(
    msg_type: int,
    tier: str,
    label: str = "standalone",
    direction: str = "out",
    payload: bytes = b"",
    walk: WireWalkResult | None = None,
) -> ClassifiedRecord:
    rec = make_record(msg_type=msg_type, direction=direction, payload=payload)
    return ClassifiedRecord(
        record=rec,
        tier=tier,  # type: ignore[arg-type]
        label=label,  # type: ignore[arg-type]
        walk_result=walk,
        schema_decoded=False,
        freq=10,
        low_frequency=False,
        notes=(),
    )


def fake_sdp(channel_kinds: tuple[str, ...]) -> SdpSnapshot:
    """Build a stub SdpSnapshot with the given declared channel_kinds."""
    services = tuple(
        DeclaredService(channel_id=i + 1, channel_kind=k, config={})
        for i, k in enumerate(channel_kinds)
    )
    return SdpSnapshot(
        head_unit_name="Test",
        car_model="TestModel",
        car_year="2026",
        car_serial="000000",
        headunit_manufacturer="Test",
        headunit_model="Test",
        sw_build="Test",
        sw_version="0.0",
        session_configuration=1,
        display_name="Test",
        probe_for_support=False,
        can_play_native_media_during_vr=None,
        driver_position=None,
        head_unit_info={},
        services=services,
    )


def test_taxonomy_row_1_control_plane_deterministic():
    """Control plane msg_type=0x0005 (ServiceDiscoveryRequest) → deterministic / high.

    BOTH fields must be populated:
    - service == "control" (the service binding)
    - message_identity == "ServiceDiscoveryRequest" (the proto message name)
    """
    cr = make_classified(msg_type=0x0005, tier="A", direction="out")
    sdp = fake_sdp(("av_channel", "sensor_channel"))

    ar = attribute_record(cr, sdp)

    assert isinstance(ar, AttributedRecord)
    assert ar.attribution_method == "deterministic"
    assert ar.confidence == "high"
    assert ar.service == "control"
    assert ar.message_identity == "ServiceDiscoveryRequest"


def test_taxonomy_row_2_channel_scoped_tier_a():
    """Channel-scoped Tier A → inferred_by_schema / medium / multiple candidates."""
    cr = make_classified(msg_type=0x8003, tier="A", direction="in")
    sdp = fake_sdp(("av_channel", "sensor_channel", "navigation_channel"))

    ar = attribute_record(cr, sdp)

    assert ar.attribution_method == "inferred_by_schema"
    assert ar.confidence == "medium"
    assert len(ar.candidate_services) >= 1
    assert ar.message_identity is None


def test_taxonomy_row_3_tier_b_sdp_narrowed_single():
    """Tier B with a navigation-shaped fingerprint + nav declared → sdp_narrowed."""
    # Build a wire walk that looks navigation-shaped:
    # has length-delimited (string) fields, body in 10-512 range.
    walk = WireWalkResult(
        fields=(
            WalkedField(field_num=1, wire_type=2, raw_size=20, value_summary=""),
            WalkedField(field_num=2, wire_type=2, raw_size=15, value_summary=""),
        ),
        consumed=35,
        total=35,
        error=None,
    )
    cr = make_classified(
        msg_type=0x8006,
        tier="B",
        direction="out",
        payload=b"\x00" * 35,  # nav-sized
        walk=walk,
    )
    # SDP declares navigation but NOT av or bluetooth — so the only nav-matching
    # shape predicate that survives is _is_navigation_shape.
    sdp = fake_sdp(("navigation_channel", "input_channel", "phone_status_channel"))

    ar = attribute_record(cr, sdp)

    assert ar.attribution_method == "sdp_narrowed"
    assert ar.confidence == "medium"
    assert ar.service == "navigation_channel"
    assert ar.message_identity is None


def test_taxonomy_row_4_tier_b_multiple_candidates():
    """Tier B with an ambiguous fingerprint matching multiple SDP services."""
    # Build a wire walk that matches BOTH av and navigation shapes:
    # has length-delimited fields AND body >= 64 bytes.
    walk = WireWalkResult(
        fields=(
            WalkedField(field_num=1, wire_type=2, raw_size=80, value_summary=""),
            WalkedField(field_num=2, wire_type=2, raw_size=20, value_summary=""),
        ),
        consumed=100,
        total=100,
        error=None,
    )
    cr = make_classified(
        msg_type=0x8050,
        tier="B",
        direction="in",
        payload=b"\x00" * 100,
        walk=walk,
    )
    # Both av_channel and navigation_channel are declared and match the shape.
    sdp = fake_sdp(("av_channel", "navigation_channel"))

    ar = attribute_record(cr, sdp)

    assert ar.attribution_method == "sdp_candidates"
    assert ar.confidence == "low"
    assert len(ar.candidate_services) >= 2
    assert ar.service is None
    assert ar.message_identity is None


def test_taxonomy_row_5_tier_b_sdp_zero_candidates():
    """Tier B record with a fingerprint matching nothing → unattributed."""
    walk = WireWalkResult(fields=(), consumed=0, total=0, error=None)
    cr = make_classified(
        msg_type=0x8077,
        tier="B",
        direction="in",
        payload=b"",
        walk=walk,
    )
    sdp = fake_sdp(("phone_status_channel", "media_info_channel"))

    ar = attribute_record(cr, sdp)

    assert ar.attribution_method == "unattributed"
    assert ar.service is None
    assert ar.message_identity is None


def test_garbage_records_skip_attribution():
    """continuation_or_garbage records skip attribution → unattributed."""
    cr = make_classified(
        msg_type=0x5555, tier="C", label="continuation_or_garbage"
    )
    sdp = fake_sdp(("av_channel",))

    ar = attribute_record(cr, sdp)

    assert ar.attribution_method == "unattributed"
    assert ar.confidence == "none"
    assert "skipped_garbage" in ar.attribution_notes


def test_vendor_extension_never_triggered_for_vw(bundle, sdp_response_path):
    """The real VW SDP has NO vendor_extension declared. No record should
    ever land in probable_vendor_extension for this capture."""
    sdp = decode_sdp_response(bundle, sdp_response_path)

    # Sanity: VW does NOT declare a vendor extension.
    declared_kinds = {s.channel_kind for s in sdp.services}
    assert "vendor_extension_channel" not in declared_kinds

    # Build 10 Tier B records with random fingerprints (mostly empty/garbage
    # to maximize the chance they land in unattributed).
    records = []
    for i in range(10):
        walk = WireWalkResult(fields=(), consumed=0, total=0, error=None)
        records.append(
            make_classified(
                msg_type=0x80F0 + i,
                tier="B",
                direction="in",
                payload=b"",
                walk=walk,
            )
        )

    for cr in records:
        ar = attribute_record(cr, sdp)
        assert ar.attribution_method != "probable_vendor_extension"
        assert "probable_vendor_extension" not in ar.attribution_notes


def test_range_tiebreaker_is_last_resort():
    """With empty surviving_hints, ambiguous Tier B records land in
    sdp_candidates rather than being force-attributed via range."""
    walk = WireWalkResult(
        fields=(
            WalkedField(field_num=1, wire_type=2, raw_size=80, value_summary=""),
            WalkedField(field_num=2, wire_type=2, raw_size=20, value_summary=""),
        ),
        consumed=100,
        total=100,
        error=None,
    )
    cr = make_classified(
        msg_type=0x8004,
        tier="B",
        direction="in",
        payload=b"\x00" * 100,
        walk=walk,
    )
    sdp = fake_sdp(("av_channel", "navigation_channel"))

    # Empty surviving_hints — exactly the VW situation.
    ar = attribute_record(cr, sdp, range_hints={"surviving_hints": []})

    assert ar.attribution_method == "sdp_candidates"
    assert ar.service is None


def test_control_plane_range_constant():
    """The control-plane range constant must cover 0x0000-0x001F per CONTEXT.md."""
    assert 0x0005 in CONTROL_PLANE_RANGE
    assert 0x0000 in CONTROL_PLANE_RANGE
    assert 0x001F in CONTROL_PLANE_RANGE
    assert 0x0020 not in CONTROL_PLANE_RANGE
    assert 0x8000 not in CONTROL_PLANE_RANGE
