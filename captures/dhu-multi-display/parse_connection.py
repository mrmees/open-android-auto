#!/usr/bin/env python3
"""Parse AA connection sequence from pcap — pre-TLS version exchange + TLS handshake."""
import struct
import sys
from scapy.all import rdpcap, TCP, Raw

PCAP_FILE = sys.argv[1] if len(sys.argv) > 1 else "aa_connection_sequence.pcap"


def reassemble_tcp_streams(packets):
    """Reassemble TCP streams by (src_port, dst_port) with packet ordering."""
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


def hex_dump(data, max_bytes=256, indent="  "):
    """Compact hex dump."""
    lines = []
    for i in range(0, min(max_bytes, len(data)), 16):
        hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        lines.append(f"{indent}{i:04x}: {hex_part:<48s} {ascii_part}")
    if len(data) > max_bytes:
        lines.append(f"{indent}... ({len(data) - max_bytes} more bytes)")
    return '\n'.join(lines)


def decode_varint(data, offset):
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


def parse_protobuf(data, depth=0):
    """Parse protobuf fields, return list of (field_num, wire_type_name, value)."""
    fields = []
    offset = 0
    while offset < len(data):
        try:
            tag, new_offset = decode_varint(data, offset)
            if new_offset == offset:
                break
            offset = new_offset
        except Exception:
            break
        field_num = tag >> 3
        wire_type = tag & 0x07

        if field_num == 0 or field_num > 10000:
            break

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
            if length > len(data) - offset or length < 0:
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
            break
    return fields


def print_protobuf(data, depth=0, max_depth=6):
    """Pretty print protobuf recursively."""
    if depth > max_depth:
        return
    indent = "    " * depth
    fields = parse_protobuf(data, depth)
    for field_num, wire_type, value in fields:
        if wire_type == 'varint':
            print(f"{indent}field {field_num}: {value}")
        elif wire_type in ('fixed64', 'fixed32'):
            print(f"{indent}field {field_num}: {value} ({wire_type})")
        elif wire_type == 'bytes':
            # Try as submessage first
            sub = parse_protobuf(value)
            if sub and len(sub) >= 1 and all(f[0] > 0 and f[0] < 500 for f in sub):
                print(f"{indent}field {field_num} {{  # {len(value)} bytes")
                print_protobuf(value, depth + 1, max_depth)
                print(f"{indent}}}")
            else:
                # Try as string
                try:
                    text = value.decode('utf-8')
                    if all(c == '\n' or c == '\r' or (32 <= ord(c) < 127) for c in text):
                        print(f"{indent}field {field_num}: \"{text}\"")
                    else:
                        print(f"{indent}field {field_num}: [{len(value)} bytes] {value[:32].hex()}")
                except UnicodeDecodeError:
                    print(f"{indent}field {field_num}: [{len(value)} bytes] {value[:32].hex()}")


def parse_tls_records(data, label=""):
    """Parse TLS record layer."""
    offset = 0
    tls_types = {0x14: 'ChangeCipherSpec', 0x15: 'Alert', 0x16: 'Handshake', 0x17: 'AppData'}
    records = []
    while offset + 5 <= len(data):
        rec_type = data[offset]
        if rec_type not in tls_types:
            break
        version = (data[offset+1] << 8) | data[offset+2]
        length = (data[offset+3] << 8) | data[offset+4]
        if offset + 5 + length > len(data):
            print(f"  TLS {tls_types[rec_type]}: version=0x{version:04x}, length={length} (TRUNCATED)")
            break
        payload = data[offset+5:offset+5+length]
        records.append((rec_type, version, payload))

        desc = tls_types[rec_type]
        if rec_type == 0x16 and length > 0:
            # Handshake message type
            hs_types = {0: 'HelloRequest', 1: 'ClientHello', 2: 'ServerHello',
                       11: 'Certificate', 12: 'ServerKeyExchange',
                       13: 'CertificateRequest', 14: 'ServerHelloDone',
                       15: 'CertificateVerify', 16: 'ClientKeyExchange',
                       20: 'Finished'}
            hs_type = payload[0]
            desc += f" ({hs_types.get(hs_type, f'type={hs_type}')})"

            # Extract cert info
            if hs_type == 11:  # Certificate
                parse_certificate(payload)

        print(f"  TLS {desc}: {length} bytes")
        offset += 5 + length

    return records


def parse_certificate(data):
    """Extract certificate subject/issuer from TLS Certificate message."""
    # Skip handshake header (1 type + 3 length)
    if len(data) < 7:
        return
    certs_len = (data[1] << 16) | (data[2] << 8) | data[3]
    offset = 4
    cert_num = 0
    while offset + 3 < len(data) and offset < 4 + certs_len:
        cert_len = (data[offset] << 16) | (data[offset+1] << 8) | data[offset+2]
        offset += 3
        if offset + cert_len > len(data):
            break
        cert_data = data[offset:offset+cert_len]
        # Look for readable strings in the cert
        strings = extract_strings(cert_data, min_len=4)
        if strings:
            print(f"    Cert {cert_num} ({cert_len} bytes): {', '.join(strings[:8])}")
        offset += cert_len
        cert_num += 1


def extract_strings(data, min_len=4):
    """Extract printable ASCII strings from binary data."""
    strings = []
    current = []
    for b in data:
        if 32 <= b < 127:
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                strings.append(''.join(current))
            current = []
    if len(current) >= min_len:
        strings.append(''.join(current))
    return strings


def parse_aa_messages(data, label):
    """Parse AA protocol messages with [2B type][2B length][payload] framing."""
    offset = 0
    msg_num = 0

    print(f"\n{'='*70}")
    print(f"Stream: {label} ({len(data)} bytes)")
    print(f"{'='*70}")

    while offset + 4 <= len(data):
        msg_type = struct.unpack('>H', data[offset:offset+2])[0]
        msg_len = struct.unpack('>H', data[offset+2:offset+4])[0]

        if offset + 4 + msg_len > len(data):
            print(f"\n[Msg {msg_num}] TRUNCATED: type=0x{msg_type:04x}, expected {msg_len} bytes")
            # Dump remaining data
            remaining = data[offset:]
            print(hex_dump(remaining, max_bytes=128))
            break

        payload = data[offset+4:offset+4+msg_len]
        offset += 4 + msg_len

        print(f"\n--- Msg {msg_num}: type=0x{msg_type:04x}, length={msg_len} ---")

        if msg_type == 0x0003:  # Handshake/version channel
            if msg_len >= 2:
                subtype = struct.unpack('>H', payload[0:2])[0]
                sub_payload = payload[2:]

                if subtype == 0x0001:
                    print(f"  VERSION REQUEST")
                    print(f"  Payload: {payload.hex()}")
                    # Try to parse version fields
                    if len(sub_payload) >= 4:
                        vmaj = struct.unpack('>H', sub_payload[0:2])[0]
                        vmin = struct.unpack('>H', sub_payload[2:4])[0]
                        print(f"  Version: {vmaj}.{vmin}")
                        if len(sub_payload) > 4:
                            print(f"  Extra: {sub_payload[4:].hex()}")

                elif subtype == 0x0002:
                    print(f"  VERSION RESPONSE")
                    print(f"  Payload: {payload.hex()}")
                    if len(sub_payload) >= 4:
                        vmaj = struct.unpack('>H', sub_payload[0:2])[0]
                        vmin = struct.unpack('>H', sub_payload[2:4])[0]
                        print(f"  Version: {vmaj}.{vmin}")
                    if len(sub_payload) >= 6:
                        status = struct.unpack('>H', sub_payload[4:6])[0]
                        print(f"  Status: {status} ({'OK' if status == 0 else 'REJECT'})")
                    if len(sub_payload) > 6:
                        print(f"  Extra: {sub_payload[6:].hex()}")

                elif subtype == 0x0003:
                    print(f"  SSL/TLS DATA ({len(sub_payload)} bytes)")
                    parse_tls_records(sub_payload)

                elif subtype == 0x0004:
                    print(f"  AUTH COMPLETE ({len(sub_payload)} bytes)")
                    print(hex_dump(sub_payload, max_bytes=128))

                else:
                    print(f"  Subtype: 0x{subtype:04x} ({len(sub_payload)} bytes)")
                    print(hex_dump(sub_payload, max_bytes=128))
        else:
            print(f"  Payload ({msg_len} bytes):")
            print(hex_dump(payload, max_bytes=128))

        msg_num += 1

        # Safety limit
        if msg_num > 200:
            print(f"\n... stopping after {msg_num} messages")
            break

    print(f"\nTotal messages parsed: {msg_num}")


def main():
    print(f"Reading {PCAP_FILE}...")
    packets = rdpcap(PCAP_FILE)
    print(f"Read {len(packets)} packets")

    streams = reassemble_tcp_streams(packets)
    print(f"Found {len(streams)} TCP streams")

    for (sport, dport), data in streams.items():
        if dport == 5277:
            label = f"PHONE (:{sport}) -> DHU (:5277)"
        elif sport == 5277:
            label = f"DHU (:5277) -> PHONE (:{dport})"
        else:
            label = f":{sport} -> :{dport}"

        parse_aa_messages(data, label)


if __name__ == '__main__':
    main()
