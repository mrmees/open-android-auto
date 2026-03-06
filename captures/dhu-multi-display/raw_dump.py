#!/usr/bin/env python3
"""Dump raw bytes from TCP streams to understand the framing."""
from scapy.all import rdpcap, TCP, Raw
import sys

PCAP_FILE = sys.argv[1] if len(sys.argv) > 1 else "aa_capture.pcap"

packets = rdpcap(PCAP_FILE)

# Group by stream
streams = {}
for pkt in packets:
    if TCP in pkt and Raw in pkt:
        sport = pkt[TCP].sport
        dport = pkt[TCP].dport
        key = (sport, dport)
        if key not in streams:
            streams[key] = bytearray()
        streams[key].extend(bytes(pkt[Raw].load))

for (sport, dport), data in streams.items():
    print(f"\n{'='*60}")
    print(f"Stream :{sport} -> :{dport}  ({len(data)} bytes total)")
    print(f"{'='*60}")

    # Hex dump first 512 bytes
    for i in range(0, min(512, len(data)), 16):
        hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f"  {i:04x}: {hex_part:<48s} {ascii_part}")

    # Look for TLS signatures
    if data[0] == 0x16:
        print(f"\n  ** Starts with TLS ClientHello (0x16) **")
    elif data[0:2] == b'\x00\x01' or data[0:2] == b'\x00\x02':
        print(f"\n  ** Looks like AA version exchange **")

    # Search for known patterns
    for i in range(min(2000, len(data))):
        # TLS record headers
        if i + 5 <= len(data) and data[i] in (0x14, 0x15, 0x16, 0x17) and data[i+1:i+3] == b'\x03\x03':
            rec_len = (data[i+3] << 8) | data[i+4]
            if rec_len < 20000:
                tls_types = {0x14: 'ChangeCipherSpec', 0x15: 'Alert', 0x16: 'Handshake', 0x17: 'AppData'}
                print(f"  TLS record at offset {i}: type={tls_types.get(data[i], '?')} len={rec_len}")
                if i < 20:  # Only show first few
                    pass
