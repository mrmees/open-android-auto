#!/usr/bin/env python3
"""Parse AA protocol frames from a pcap capture of a DHU session.

AA wire format (after TCP):
  - Version exchange: first 4 bytes each direction
  - Then framed messages:
    - 2 bytes: channel ID (big-endian)
    - 1 byte: flags (encrypted, control, etc.)
    - 2 bytes: payload length (big-endian)
    - N bytes: payload (protobuf)

Channel 0 = control channel (ServiceDiscoveryRequest/Response, etc.)
"""

import struct
import sys
from scapy.all import rdpcap, TCP, Raw

PCAP_FILE = sys.argv[1] if len(sys.argv) > 1 else "aa_capture.pcap"


def reassemble_tcp_streams(packets):
    """Reassemble TCP streams by (src_port, dst_port) pairs."""
    streams = {}
    for pkt in packets:
        if TCP in pkt and Raw in pkt:
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
            key = (sport, dport)
            if key not in streams:
                streams[key] = bytearray()
            streams[key].extend(bytes(pkt[Raw].load))
    return streams


def decode_varint(data, offset):
    """Decode a protobuf varint."""
    result = 0
    shift = 0
    while offset < len(data):
        b = data[offset]
        result |= (b & 0x7F) << shift
        offset += 1
        if (b & 0x80) == 0:
            return result, offset
        shift += 7
    return result, offset


def parse_protobuf_fields(data, depth=0):
    """Parse raw protobuf into field numbers and values."""
    fields = []
    offset = 0
    while offset < len(data):
        try:
            tag, offset = decode_varint(data, offset)
        except Exception:
            break
        field_num = tag >> 3
        wire_type = tag & 0x07

        if wire_type == 0:  # varint
            value, offset = decode_varint(data, offset)
            fields.append((field_num, 'varint', value))
        elif wire_type == 1:  # 64-bit
            if offset + 8 > len(data):
                break
            value = struct.unpack('<Q', data[offset:offset+8])[0]
            offset += 8
            fields.append((field_num, 'fixed64', value))
        elif wire_type == 2:  # length-delimited
            length, offset = decode_varint(data, offset)
            if offset + length > len(data):
                break
            value = data[offset:offset+length]
            offset += length
            fields.append((field_num, 'bytes', value))
        elif wire_type == 5:  # 32-bit
            if offset + 4 > len(data):
                break
            value = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            fields.append((field_num, 'fixed32', value))
        else:
            break  # unknown wire type
    return fields


def print_protobuf(data, depth=0, label=""):
    """Recursively print protobuf fields."""
    indent = "  " * depth
    fields = parse_protobuf_fields(data, depth)
    for field_num, wire_type, value in fields:
        if wire_type == 'varint':
            print(f"{indent}field {field_num}: {value} (varint)")
        elif wire_type == 'fixed64':
            print(f"{indent}field {field_num}: {value} (fixed64)")
        elif wire_type == 'fixed32':
            print(f"{indent}field {field_num}: {value} (fixed32)")
        elif wire_type == 'bytes':
            # Try to parse as sub-message
            try:
                sub_fields = parse_protobuf_fields(value)
                if sub_fields and all(f[0] > 0 and f[0] < 1000 for f in sub_fields):
                    print(f"{indent}field {field_num}: {{ (submessage, {len(value)} bytes)")
                    print_protobuf(value, depth + 1)
                    print(f"{indent}}}")
                else:
                    raise ValueError("not a submessage")
            except (ValueError, Exception):
                # Print as raw bytes or string
                try:
                    text = value.decode('utf-8')
                    if all(32 <= ord(c) < 127 for c in text):
                        print(f"{indent}field {field_num}: \"{text}\" (string)")
                    else:
                        print(f"{indent}field {field_num}: [{len(value)} bytes] {value[:64].hex()}")
                except UnicodeDecodeError:
                    print(f"{indent}field {field_num}: [{len(value)} bytes] {value[:64].hex()}")


def parse_aa_frames(stream_data, label=""):
    """Parse AA protocol frames from a reassembled TCP stream."""
    offset = 0
    frames = []

    # Skip version exchange (first 4 bytes: major(2) + minor(2))
    if len(stream_data) < 4:
        return frames

    version_major = struct.unpack('>H', stream_data[0:2])[0]
    version_minor = struct.unpack('>H', stream_data[2:4])[0]
    print(f"\n{'='*60}")
    print(f"Stream: {label}")
    print(f"Version: {version_major}.{version_minor}")
    print(f"Total stream bytes: {len(stream_data)}")
    print(f"{'='*60}")

    offset = 4

    frame_num = 0
    while offset + 5 <= len(stream_data):
        channel_id = struct.unpack('>H', stream_data[offset:offset+2])[0]
        flags = stream_data[offset+2]
        payload_len = struct.unpack('>H', stream_data[offset+3:offset+5])[0]

        if offset + 5 + payload_len > len(stream_data):
            print(f"\n[Frame {frame_num}] Truncated: channel={channel_id}, flags=0x{flags:02x}, "
                  f"expected {payload_len} bytes, only {len(stream_data) - offset - 5} available")
            break

        payload = stream_data[offset+5:offset+5+payload_len]
        offset += 5 + payload_len

        encrypted = bool(flags & 0x08)
        control = bool(flags & 0x04)
        first_frame = bool(flags & 0x01)
        last_frame = bool(flags & 0x02)

        flag_str = []
        if encrypted: flag_str.append("ENC")
        if control: flag_str.append("CTRL")
        if first_frame: flag_str.append("FIRST")
        if last_frame: flag_str.append("LAST")

        frames.append({
            'num': frame_num,
            'channel': channel_id,
            'flags': flags,
            'encrypted': encrypted,
            'control': control,
            'payload': payload,
            'flag_str': '|'.join(flag_str) if flag_str else 'NONE'
        })

        # Print all control channel frames and first few frames of other channels
        if channel_id == 0 or frame_num < 50:
            print(f"\n--- Frame {frame_num}: channel={channel_id}, flags=0x{flags:02x} [{frames[-1]['flag_str']}], "
                  f"payload={payload_len} bytes ---")
            if not encrypted and payload_len > 0 and payload_len < 10000:
                # For control channel, try to parse the control message wrapper
                if control and channel_id == 0:
                    # Control messages have a 2-byte message type prefix
                    if payload_len >= 2:
                        msg_type = struct.unpack('>H', payload[0:2])[0]
                        print(f"  Control msg type: 0x{msg_type:04x} ({msg_type})")
                        if payload_len > 2:
                            print(f"  Protobuf payload:")
                            print_protobuf(payload[2:], depth=2)
                elif not encrypted:
                    print(f"  Raw: {payload[:128].hex()}")
                    if payload_len < 2000:
                        print(f"  Protobuf parse attempt:")
                        print_protobuf(payload, depth=2)

        frame_num += 1

    print(f"\nTotal frames: {frame_num}")
    return frames


def main():
    print(f"Reading {PCAP_FILE}...")
    packets = rdpcap(PCAP_FILE)
    print(f"Read {len(packets)} packets")

    streams = reassemble_tcp_streams(packets)
    print(f"Found {len(streams)} TCP streams")

    for (sport, dport), data in streams.items():
        label = f":{sport} -> :{dport}"
        if len(data) > 4:
            frames = parse_aa_frames(data, label)


if __name__ == '__main__':
    main()
