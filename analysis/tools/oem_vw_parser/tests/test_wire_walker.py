from __future__ import annotations

from analysis.tools.oem_vw_parser.models import WalkedField, WireWalkResult
from analysis.tools.oem_vw_parser.wire_walker import walk_proto


def test_walks_clean_ping_response():
    # PingResponse-shape body: field 1 varint 1, field 2 varint 1, field 3 varint 3
    body = bytes.fromhex("080110011803")
    result = walk_proto(body)
    assert result.error is None
    assert result.consumed == 6
    assert result.total == 6
    assert result.clean_to_eob is True
    assert len(result.fields) == 3
    assert [f.field_num for f in result.fields] == [1, 2, 3]
    assert all(f.wire_type == 0 for f in result.fields)  # all varints


def test_padding_bail(padded_ping_hex):
    """Real PingRequest body from VW capture (seq=58) has trailing zero
    padding that breaks protoc --decode_raw. The wire walker must bail
    cleanly on field=0 and report what it walked before the padding."""
    full_payload = bytes.fromhex(padded_ping_hex)
    # Strip the 2-byte 0x000B msg_type prefix to get the body
    assert full_payload[:2] == b"\x00\x0b"
    body = full_payload[2:]
    result = walk_proto(body)
    assert result.consumed > 0
    assert result.error is not None
    assert result.error.startswith("field=0")
    assert result.clean_with_padding is True
    assert len(result.fields) >= 1


def test_truncated_len_delim_reports_error():
    # Field 1 wire_type 2 (length-delimited) length 3 but only 1 byte follows
    body = bytes.fromhex("0a03ab")
    result = walk_proto(body)
    assert result.error is not None
    assert result.error.startswith("value-decode-failed")
    assert result.consumed == 0
    assert len(result.fields) == 0


def test_clean_to_eob_vs_with_padding():
    empty = WireWalkResult(fields=(), consumed=0, total=0, error=None)
    assert empty.clean_to_eob is True
    assert empty.clean_with_padding is False

    padded = WireWalkResult(
        fields=(WalkedField(field_num=1, wire_type=0, raw_size=2, value_summary=""),),
        consumed=2,
        total=4,
        error="field=0 at pos=2 (likely padding sentinel)",
    )
    assert padded.clean_with_padding is True
    assert padded.clean_to_eob is False
