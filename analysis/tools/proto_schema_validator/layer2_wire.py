"""Layer 2: Validate our schemas against wire capture data."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from google.protobuf import message_factory
from google.protobuf.internal import decoder as _pb_decoder
from google.protobuf.internal import wire_format

from analysis.tools.proto_schema_validator.models import (
    IssueKind,
    Severity,
    WireIssue,
)
from analysis.tools.proto_stream_validator.descriptors import DescriptorBundle
from analysis.tools.proto_stream_validator.io import load_capture_jsonl
from analysis.tools.proto_stream_validator.message_map import resolve_message_type


def _get_message_class(bundle: DescriptorBundle, message_type: str):
    """Get a message class from the descriptor pool."""
    descriptor = bundle.pool.FindMessageTypeByName(message_type)
    get_cls = getattr(message_factory, "GetMessageClass", None)
    if callable(get_cls):
        return get_cls(descriptor)
    factory = message_factory.MessageFactory()
    return factory.GetPrototype(descriptor)


def _extract_wire_field_numbers(payload: bytes) -> set[int]:
    """Extract field numbers from raw protobuf wire data."""
    field_nums: set[int] = set()
    pos = 0
    buf = memoryview(payload)
    while pos < len(payload):
        # Read varint tag
        try:
            tag, pos = _pb_decoder._DecodeVarint(buf, pos)
        except Exception:
            break
        field_number = tag >> 3
        wire_type = tag & 0x7
        field_nums.add(field_number)

        # Skip field value based on wire type
        if wire_type == wire_format.WIRETYPE_VARINT:
            try:
                _, pos = _pb_decoder._DecodeVarint(buf, pos)
            except Exception:
                break
        elif wire_type == wire_format.WIRETYPE_FIXED64:
            pos += 8
        elif wire_type == wire_format.WIRETYPE_LENGTH_DELIMITED:
            try:
                length, pos = _pb_decoder._DecodeVarint(buf, pos)
                pos += length
            except Exception:
                break
        elif wire_type == wire_format.WIRETYPE_FIXED32:
            pos += 4
        elif wire_type in (wire_format.WIRETYPE_START_GROUP, wire_format.WIRETYPE_END_GROUP):
            pass  # Groups are rare; just note the field number
        else:
            break

    return field_nums


def run_layer2(
    bundle: DescriptorBundle,
    capture_path: Path,
) -> tuple[list[WireIssue], dict]:
    """Run Layer 2 wire capture validation.

    Returns (issues, stats) where stats has counts for decoded/failed/unmapped.
    """
    frames = load_capture_jsonl(capture_path)

    issues: list[WireIssue] = []
    stats = {"decoded": 0, "failed": 0, "unmapped": 0, "total": len(frames)}

    # Track field coverage: message_type -> set of field numbers seen in wire
    field_coverage: dict[str, set[int]] = defaultdict(set)
    # Track unknown fields: message_type -> Counter of field numbers
    unknown_fields: dict[str, Counter] = defaultdict(Counter)
    # Track parse failures per message type
    parse_failures: dict[str, int] = Counter()

    # Cache: message_type -> set of known field numbers
    known_fields_cache: dict[str, set[int]] = {}

    for idx, frame in enumerate(frames):
        # Resolve message type
        try:
            msg_type = resolve_message_type(
                frame.direction, frame.channel_id, frame.message_id, frame.message_name
            )
        except KeyError:
            stats["unmapped"] += 1
            continue

        payload = bytes.fromhex(frame.payload_hex) if frame.payload_hex else b""
        if not payload:
            stats["decoded"] += 1
            continue

        # Try to decode
        try:
            cls = _get_message_class(bundle, msg_type)
        except KeyError:
            stats["failed"] += 1
            parse_failures[msg_type] += 1
            continue

        msg = cls()
        try:
            msg.ParseFromString(payload)
        except Exception:
            stats["failed"] += 1
            parse_failures[msg_type] += 1
            continue

        stats["decoded"] += 1

        # Get known field numbers for this message type
        if msg_type not in known_fields_cache:
            try:
                descriptor = bundle.pool.FindMessageTypeByName(msg_type)
                known_fields_cache[msg_type] = {fd.number for fd in descriptor.fields}
            except KeyError:
                known_fields_cache[msg_type] = set()

        known_nums = known_fields_cache[msg_type]

        # Extract field numbers from raw wire data
        wire_nums = _extract_wire_field_numbers(payload)
        field_coverage[msg_type].update(wire_nums)

        # Check for unknown fields (in wire but not in schema)
        for fn in wire_nums - known_nums:
            unknown_fields[msg_type][fn] += 1

    # Generate issues from parse failures
    for msg_type, count in parse_failures.items():
        short_name = msg_type.rsplit(".", 1)[-1]
        issues.append(WireIssue(
            proto_message=short_name,
            kind=IssueKind.PARSE_FAILURE,
            severity=Severity.ERROR,
            detail=f"{count} frames failed to decode as {msg_type}",
        ))

    # Generate issues from unknown fields
    for msg_type, field_counts in sorted(unknown_fields.items()):
        short_name = msg_type.rsplit(".", 1)[-1]
        for field_num, count in sorted(field_counts.items()):
            issues.append(WireIssue(
                proto_message=short_name,
                kind=IssueKind.UNKNOWN_WIRE_FIELD,
                severity=Severity.WARNING,
                field_number=field_num,
                detail=f"unknown field {field_num} seen {count} times in wire data "
                       f"(not in our schema for {msg_type})",
            ))

    # Generate issues for defined fields never seen in wire data
    for msg_type, seen_fields in sorted(field_coverage.items()):
        short_name = msg_type.rsplit(".", 1)[-1]
        known_nums = known_fields_cache.get(msg_type, set())
        for fn in sorted(known_nums - seen_fields):
            try:
                descriptor = bundle.pool.FindMessageTypeByName(msg_type)
                fd = next((f for f in descriptor.fields if f.number == fn), None)
                name = fd.name if fd else f"field_{fn}"
            except KeyError:
                name = f"field_{fn}"
            issues.append(WireIssue(
                proto_message=short_name,
                kind=IssueKind.FIELD_NEVER_SEEN,
                severity=Severity.INFO,
                field_number=fn,
                detail=f"field {fn} ({name}) defined but never seen in wire data",
            ))

    return issues, stats
