from __future__ import annotations

from google.protobuf.internal import decoder

from .models import WalkedField, WireWalkResult


def walk_proto(data: bytes) -> WireWalkResult:
    """Walk a protobuf payload tag-by-tag using the protobuf internal varint
    decoder. Returns a WireWalkResult describing what was consumed.

    Tolerates trailing zero padding by treating ``field_num == 0`` as a
    clean bail signal — in real BoringSSL output on the VW MIB3 OI capture,
    PingRequest and ChannelOpenResponse records can carry trailing ``\\x00``
    bytes that break ``protoc --decode_raw`` but are otherwise structurally
    sound. The wire walker stops at the first zero byte and reports the
    fields walked up to that point.

    See ``.planning/phases/07-vw-capture-analysis/07-CONTEXT.md`` gotcha #7
    and the verified pattern in ``07-RESEARCH.md`` § Pattern 2.
    """
    fields: list[WalkedField] = []
    pos = 0
    n = len(data)
    error: str | None = None

    while pos < n:
        tag_start = pos
        try:
            tag, new_pos = decoder._DecodeVarint(data, pos)
        except Exception as e:  # noqa: BLE001 — varint decoder raises bare exceptions
            error = f"tag-decode-failed at {pos}: {e}"
            break

        field_num = tag >> 3
        wire_type = tag & 0x7

        # Padding-bail sentinel: trailing \x00 bytes look like field 0, which
        # is not a legal proto field number. Stop here and report what we
        # walked. The pos value at this point is the byte index of the
        # sentinel — the consumed count therefore EXCLUDES the sentinel byte.
        if field_num == 0:
            error = f"field=0 at pos={pos} (likely padding sentinel)"
            break

        try:
            if wire_type == 0:  # varint
                _, new_pos = decoder._DecodeVarint(data, new_pos)
            elif wire_type == 1:  # fixed64
                if new_pos + 8 > n:
                    raise ValueError("truncated fixed64")
                new_pos += 8
            elif wire_type == 2:  # length-delimited
                length, new_pos = decoder._DecodeVarint(data, new_pos)
                if new_pos + length > n:
                    raise ValueError("truncated len-delim")
                new_pos += length
            elif wire_type == 5:  # fixed32
                if new_pos + 4 > n:
                    raise ValueError("truncated fixed32")
                new_pos += 4
            else:
                # wire types 3 and 4 are deprecated proto2 group markers
                error = f"wire-type {wire_type} unsupported at pos={pos}"
                break
        except Exception as e:  # noqa: BLE001 — protobuf raises bare exceptions
            error = f"value-decode-failed at {pos}: {e}"
            break

        fields.append(
            WalkedField(
                field_num=field_num,
                wire_type=wire_type,
                raw_size=new_pos - tag_start,
                value_summary="",  # deliberately empty in 07-01
            )
        )
        pos = new_pos

    return WireWalkResult(
        fields=tuple(fields),
        consumed=pos,
        total=n,
        error=error,
    )
