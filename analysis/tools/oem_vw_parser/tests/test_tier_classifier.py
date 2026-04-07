from __future__ import annotations

from analysis.tools.oem_vw_parser.io import load_vw_capture
from analysis.tools.oem_vw_parser.models import (
    UnifiedRecord,
    WalkedField,
    WireWalkResult,
)
from analysis.tools.oem_vw_parser.tier_classifier import (
    classify_capture,
    classify_record,
    derive_frequency_threshold,
    determine_tier,
)


def make_record(msg_type: int, direction: str, payload_len: int) -> UnifiedRecord:
    return UnifiedRecord(
        capture_id="test",
        seq=0,
        ts_ms=0,
        direction=direction,  # type: ignore[arg-type]
        msg_type=msg_type,
        payload=b"\x00" * payload_len,
        payload_len=payload_len,
        channel_id=None,
        flags=None,
        service_type=None,
    )


def test_tier_a_known_descriptor(bundle):
    # Tier A is gated by descriptor map presence — passing in_descriptor_map=True
    # forces Tier A regardless of structural range.
    assert determine_tier(msg_type=11, in_descriptor_map=True) == "A"
    assert determine_tier(msg_type=0x0005, in_descriptor_map=True) == "A"


def test_tier_b_plausible_range():
    assert determine_tier(msg_type=0x8004, in_descriptor_map=False) == "B"
    assert determine_tier(msg_type=0xFFFF, in_descriptor_map=False) == "B"
    assert determine_tier(msg_type=0x0010, in_descriptor_map=False) == "B"


def test_tier_c_implausible():
    assert determine_tier(msg_type=0x5555, in_descriptor_map=False) == "C"
    assert determine_tier(msg_type=0x1234, in_descriptor_map=False) == "C"


def test_msg_type_zero_demotion(vw_micro_path, bundle):
    """Every msg_type=0 out record with payload_len > 32 must be demoted to
    Tier C with the msg_type_zero_demoted_to_C note."""
    records = list(load_vw_capture(vw_micro_path, capture_id="vw_micro"))
    classified, _ = classify_capture(records, bundle)

    big_zero_records = [
        cr
        for cr in classified
        if cr.record.msg_type == 0
        and cr.record.direction == "out"
        and cr.record.payload_len > 32
    ]
    assert len(big_zero_records) >= 3, (
        f"vw_micro fixture should contain at least 3 large msg_type=0 out records, "
        f"got {len(big_zero_records)}"
    )
    for cr in big_zero_records:
        assert cr.tier == "C", f"expected Tier C, got {cr.tier} for {cr.record}"
        assert cr.label == "continuation_or_garbage"
        assert "msg_type_zero_demoted_to_C" in cr.notes


def test_frequency_derivation():
    # Part 1: a histogram resembling the VW capture distribution should derive 3.
    vw_like = {}
    for i in range(1032):
        vw_like[(0x1000 + i, "in")] = 1
    for i in range(5):
        vw_like[(0x2000 + i, "in")] = 2
    for i in range(12):
        vw_like[(0x0010 + i, "in")] = 119
    derived = derive_frequency_threshold(vw_like)
    assert derived == 3, f"Expected knee at 3 for VW-like distribution, got {derived}"

    # Part 2: synthetic histogram with the knee at 5 — proves the function
    # actually inspects the distribution rather than returning a constant.
    synthetic = {}
    for i in range(100):
        synthetic[(0x3000 + i, "in")] = 1
    for i in range(80):
        synthetic[(0x4000 + i, "in")] = 2
    for i in range(60):
        synthetic[(0x5000 + i, "in")] = 3
    for i in range(40):
        synthetic[(0x6000 + i, "in")] = 4
    for i in range(5):
        synthetic[(0x7000 + i, "in")] = 5
    for i in range(50):
        synthetic[(0x8000 + i, "in")] = 100
    derived2 = derive_frequency_threshold(synthetic)
    assert derived2 == 5, (
        f"Expected knee at 5 for synthetic distribution, got {derived2}"
    )


def test_low_frequency_second_signal_rule():
    # A plausible Tier A msg_type with freq=1 (singleton) but schema_ok=True
    # should stay `standalone` via the second-signal corroboration rule.
    record = make_record(msg_type=0x0005, direction="out", payload_len=20)
    label, notes = classify_record(
        record,
        tier="A",
        wire_result=None,
        schema_ok=True,
        freq=1,
        freq_threshold=3,
    )
    assert label == "standalone"
    assert "low_frequency" in notes


def test_low_frequency_no_second_signal_demotes():
    record = make_record(msg_type=0x0005, direction="out", payload_len=20)
    thin_wire = WireWalkResult(
        fields=(WalkedField(field_num=1, wire_type=0, raw_size=2, value_summary=""),),
        consumed=2,
        total=2,
        error=None,
    )
    label, notes = classify_record(
        record,
        tier="A",
        wire_result=thin_wire,
        schema_ok=False,
        freq=1,
        freq_threshold=3,
    )
    # Strict expectation per the rule in <behavior>: walked_ok is True
    # (clean_to_eob), the function enters the schema_ok-or-walked_ok branch,
    # freq < threshold so it requires a second signal, schema_ok=False and
    # len(wire_result.fields) == 1 < 2, so second_signal is False.
    assert label == "continuation_or_garbage"
    assert "low_frequency_second_signal_failed" in notes


def test_atomic_label_mapping():
    # Case 1: Tier C → continuation_or_garbage
    tier_c_record = make_record(msg_type=0x5555, direction="in", payload_len=20)
    label, _ = classify_record(
        tier_c_record,
        tier="C",
        wire_result=None,
        schema_ok=False,
        freq=1,
        freq_threshold=3,
    )
    assert label == "continuation_or_garbage"

    # Case 2: Tier A, schema_ok, high freq → standalone
    tier_a_record = make_record(msg_type=0x000B, direction="out", payload_len=10)
    label, _ = classify_record(
        tier_a_record,
        tier="A",
        wire_result=None,
        schema_ok=True,
        freq=119,
        freq_threshold=3,
    )
    assert label == "standalone"

    # Case 3: Tier B, partial walk, schema_ok=False → probable_first
    partial_walk = WireWalkResult(
        fields=(WalkedField(field_num=1, wire_type=2, raw_size=4, value_summary=""),),
        consumed=4,
        total=20,
        error="value-decode-failed at 4: truncated len-delim",
    )
    tier_b_record = make_record(msg_type=0x8004, direction="in", payload_len=20)
    label, _ = classify_record(
        tier_b_record,
        tier="B",
        wire_result=partial_walk,
        schema_ok=False,
        freq=2752,
        freq_threshold=3,
    )
    assert label == "probable_first"

    # Negative: assert the function NEVER returns reassembled or unattributed
    cases = [
        classify_record(tier_c_record, "C", None, False, 1, 3),
        classify_record(tier_a_record, "A", None, True, 119, 3),
        classify_record(tier_b_record, "B", partial_walk, False, 2752, 3),
    ]
    for case_label, _ in cases:
        assert case_label not in {"reassembled", "unattributed"}


def test_reassembled_never_populated(vw_micro_path, bundle):
    records = list(load_vw_capture(vw_micro_path, capture_id="vw_micro"))
    classified, _ = classify_capture(records, bundle)
    assert all(cr.label != "reassembled" for cr in classified)
    assert all(cr.label != "unattributed" for cr in classified)
