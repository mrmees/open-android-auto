#!/usr/bin/env python3
"""
AA SDP Grabber — Act as a fake phone, let the DHU connect to us.

Usage:
  1. Kill any existing adb forward on port 5277
  2. Run: python3 aa_sdp_grabber.py [port]
  3. Launch DHU with: desktop-head-unit --adb ...
  4. DHU connects to localhost:5277 and sends its SDP

The script listens on port 5277 (default), accepts the DHU's connection,
completes the version exchange and TLS handshake (as the TLS server),
then captures the ServiceDiscoveryResponse.

Requires: Python 3.7+ (stdlib only, no pip packages)
          openssl CLI (for generating certs on first run)
"""

import socket
import ssl
import struct
import sys
import os
import json
import time
from datetime import datetime


# --- AA Protocol Constants ---
AA_VERSION_MAJOR = 1
AA_VERSION_MINOR = 7

# Channel 0 subtypes (pre-TLS)
SUBTYPE_VERSION_REQUEST = 0x0001
SUBTYPE_VERSION_RESPONSE = 0x0002
SUBTYPE_SSL_DATA = 0x0003
SUBTYPE_AUTH_COMPLETE = 0x0004

# Post-TLS message types on channel 0
MSG_SERVICE_DISCOVERY_REQUEST = 0x0005
MSG_SERVICE_DISCOVERY_RESPONSE = 0x0006
MSG_CHANNEL_OPEN_REQUEST = 0x0007
MSG_CHANNEL_OPEN_RESPONSE = 0x0008
MSG_PING_REQUEST = 0x000B
MSG_PING_RESPONSE = 0x000C


# --- Protobuf Decoder ---
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
        if shift > 63:
            break
    raise ValueError(f"Malformed varint at offset {offset}")


def encode_varint(value):
    """Encode an integer as a protobuf varint."""
    result = bytearray()
    while value > 0x7F:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result)


def parse_protobuf(data):
    """Parse protobuf into list of (field_num, wire_type, value)."""
    fields = []
    offset = 0
    while offset < len(data):
        try:
            tag, offset = decode_varint(data, offset)
        except (ValueError, IndexError):
            break
        field_num = tag >> 3
        wire_type = tag & 0x07
        if field_num == 0 or field_num > 30000:
            break
        if wire_type == 0:  # varint
            try:
                value, offset = decode_varint(data, offset)
            except (ValueError, IndexError):
                break
            fields.append((field_num, 'varint', value))
        elif wire_type == 1:  # fixed64
            if offset + 8 > len(data):
                break
            value = struct.unpack('<Q', data[offset:offset+8])[0]
            offset += 8
            fields.append((field_num, 'fixed64', value))
        elif wire_type == 2:  # length-delimited
            try:
                length, offset = decode_varint(data, offset)
            except (ValueError, IndexError):
                break
            if length < 0 or offset + length > len(data):
                break
            value = data[offset:offset+length]
            offset += length
            fields.append((field_num, 'bytes', value))
        elif wire_type == 5:  # fixed32
            if offset + 4 > len(data):
                break
            value = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            fields.append((field_num, 'fixed32', value))
        else:
            break
    return fields


def is_likely_protobuf(data):
    """Heuristic: does this look like a valid protobuf message?"""
    if len(data) < 2:
        return False
    try:
        fields = parse_protobuf(data)
        if not fields:
            return False
        return all(0 < f[0] < 500 for f in fields)
    except Exception:
        return False


def protobuf_to_dict(data, depth=0, max_depth=8):
    """Convert protobuf to nested dict for JSON output."""
    if depth > max_depth:
        return {"_raw": data.hex()}
    fields = parse_protobuf(data)
    result = {}
    for field_num, wire_type, value in fields:
        key = f"field_{field_num}"
        if wire_type == 'varint':
            entry = value
        elif wire_type in ('fixed32', 'fixed64'):
            entry = value
        elif wire_type == 'bytes':
            if is_likely_protobuf(value):
                entry = protobuf_to_dict(value, depth + 1, max_depth)
            else:
                try:
                    text = value.decode('utf-8')
                    if all(c == '\n' or c == '\r' or c == '\t' or (32 <= ord(c) < 127) for c in text):
                        entry = text
                    else:
                        entry = {"_hex": value.hex(), "_len": len(value)}
                except UnicodeDecodeError:
                    entry = {"_hex": value[:64].hex(), "_len": len(value)}
        else:
            entry = value

        # Handle repeated fields
        if key in result:
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            result[key].append(entry)
        else:
            result[key] = entry
    return result


def print_protobuf(data, depth=0, max_depth=8):
    """Pretty-print protobuf recursively."""
    if depth > max_depth:
        return
    indent = "  " * depth
    fields = parse_protobuf(data)
    for field_num, wire_type, value in fields:
        if wire_type == 'varint':
            print(f"{indent}field {field_num}: {value}")
        elif wire_type in ('fixed32', 'fixed64'):
            print(f"{indent}field {field_num}: {value} ({wire_type})")
        elif wire_type == 'bytes':
            if is_likely_protobuf(value):
                print(f"{indent}field {field_num} {{  # {len(value)} bytes")
                print_protobuf(value, depth + 1, max_depth)
                print(f"{indent}}}")
            else:
                try:
                    text = value.decode('utf-8')
                    if all(c == '\n' or c == '\r' or c == '\t' or (32 <= ord(c) < 127) for c in text):
                        print(f"{indent}field {field_num}: \"{text}\"")
                    else:
                        print(f"{indent}field {field_num}: [{len(value)} bytes] {value[:32].hex()}")
                except UnicodeDecodeError:
                    print(f"{indent}field {field_num}: [{len(value)} bytes] {value[:32].hex()}")


# --- AA Frame I/O ---
def read_exact(sock, n):
    """Read exactly n bytes from socket."""
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError(f"Connection closed (got {len(data)}/{n} bytes)")
        data.extend(chunk)
    return bytes(data)


def read_aa_frame(sock):
    """Read one AA frame: [1B channel][1B flags][2B length][payload]."""
    header = read_exact(sock, 4)
    channel = header[0]
    flags = header[1]
    length = struct.unpack('>H', header[2:4])[0]
    payload = read_exact(sock, length) if length > 0 else b''
    return channel, flags, payload


def send_aa_frame(sock, channel, flags, payload):
    """Send one AA frame."""
    header = struct.pack('>BBH', channel, flags, len(payload))
    sock.sendall(header + payload)


# --- Certificate Management ---
def ensure_certs(script_dir):
    """Generate server cert + key if they don't exist."""
    cert_file = os.path.join(script_dir, 'server_cert.pem')
    key_file = os.path.join(script_dir, 'server_key.pem')

    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"  Using existing cert: {cert_file}")
        return cert_file, key_file

    print("  Generating self-signed server cert...")
    import subprocess
    subprocess.run([
        'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
        '-keyout', key_file, '-out', cert_file,
        '-days', '3650', '-nodes',
        '-subj', '/C=US/ST=California/L=Mountain View/O=Google Automotive Link/CN=CarService'
    ], check=True, capture_output=True)
    print(f"  Generated: {cert_file}")
    return cert_file, key_file


# --- TLS over AA Frames (Server Side) ---
class AAMemoryBIO:
    """TLS via memory BIOs, tunneled through AA frames. Server mode."""

    def __init__(self, sock, cert_file, key_file):
        self.sock = sock

        # Server-side SSL context
        self.ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        self.ctx.load_cert_chain(cert_file, key_file)
        # Request client cert but don't verify it
        self.ctx.verify_mode = ssl.CERT_OPTIONAL
        self.ctx.check_hostname = False

        # Memory BIOs
        self.incoming = ssl.MemoryBIO()  # data FROM client (DHU)
        self.outgoing = ssl.MemoryBIO()  # data TO client (DHU)
        self.ssl_obj = self.ctx.wrap_bio(self.incoming, self.outgoing,
                                         server_side=True)

    def do_handshake(self):
        """Perform TLS handshake over AA frames (as server)."""
        print("  Starting TLS handshake (server side)...")
        while True:
            try:
                self.ssl_obj.do_handshake()
                out_data = self.outgoing.read()
                if out_data:
                    self._send_tls_data(out_data)
                print("  TLS handshake complete!")
                peer_cert = self.ssl_obj.getpeercert(binary_form=True)
                if peer_cert:
                    print(f"  DHU client cert: {len(peer_cert)} bytes")
                else:
                    print("  DHU did not send a client cert")
                return True
            except ssl.SSLWantReadError:
                out_data = self.outgoing.read()
                if out_data:
                    self._send_tls_data(out_data)
                tls_data = self._recv_tls_data()
                if tls_data:
                    self.incoming.write(tls_data)

    def read(self, size=65536):
        """Read decrypted data."""
        while True:
            try:
                return self.ssl_obj.read(size)
            except ssl.SSLWantReadError:
                tls_data = self._recv_tls_data()
                if tls_data:
                    self.incoming.write(tls_data)

    def write(self, data):
        """Write data through TLS."""
        self.ssl_obj.write(data)
        out_data = self.outgoing.read()
        if out_data:
            self._send_tls_data(out_data)

    def _send_tls_data(self, tls_bytes):
        """Send TLS record bytes wrapped in AA frames."""
        MAX_CHUNK = 60000
        offset = 0
        while offset < len(tls_bytes):
            chunk = tls_bytes[offset:offset + MAX_CHUNK]
            payload = struct.pack('>H', SUBTYPE_SSL_DATA) + chunk
            send_aa_frame(self.sock, 0, 0x03, payload)
            offset += MAX_CHUNK

    def _recv_tls_data(self):
        """Read AA frames until we get TLS data."""
        while True:
            channel, flags, payload = read_aa_frame(self.sock)
            if channel == 0 and len(payload) >= 2:
                subtype = struct.unpack('>H', payload[0:2])[0]
                if subtype == SUBTYPE_SSL_DATA:
                    return payload[2:]
                elif subtype == SUBTYPE_AUTH_COMPLETE:
                    print(f"  [AUTH] DHU sent AUTH_COMPLETE: {payload.hex()}")
                    continue
                else:
                    print(f"  [?] Unexpected subtype 0x{subtype:04x}")
            else:
                print(f"  [?] Non-channel-0 frame: ch={channel} flags=0x{flags:02x}")


# --- Main ---
def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5277
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = script_dir  # save output files next to script

    print(f"AA SDP Grabber (Server Mode)")
    print(f"=" * 50)

    # Step 0: Ensure certs exist
    cert_file, key_file = ensure_certs(script_dir)

    # Listen for DHU connection
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', port))
    server.listen(1)
    print(f"\nListening on 127.0.0.1:{port}")
    print(f"Now launch the DHU with: desktop-head-unit --adb ...")
    print(f"Waiting for DHU to connect...\n")

    conn, addr = server.accept()
    conn.settimeout(15)
    print(f"DHU connected from {addr}")

    try:
        # Step 1: Version exchange — DHU sends request first
        print("\n[1] Version Exchange")

        # In the capture, the PHONE sends the version request first.
        # But we're the fake phone (server). The DHU is the client.
        # From the capture:
        #   Phone -> DHU: version request (subtype 1)
        #   DHU -> Phone: version response (subtype 2)
        #
        # So we (fake phone) send the version request, DHU responds.
        ver_req = struct.pack('>HHH',
            SUBTYPE_VERSION_REQUEST,
            AA_VERSION_MAJOR,
            AA_VERSION_MINOR,
        )
        send_aa_frame(conn, 0, 0x03, ver_req)
        print(f"  Sent version request: v{AA_VERSION_MAJOR}.{AA_VERSION_MINOR}")

        # Read DHU's version response
        channel, flags, payload = read_aa_frame(conn)
        print(f"  Received: ch={channel} flags=0x{flags:02x} len={len(payload)}")
        print(f"  Raw: {payload.hex()}")

        if len(payload) >= 8:
            subtype = struct.unpack('>H', payload[0:2])[0]
            resp_major = struct.unpack('>H', payload[2:4])[0]
            resp_minor = struct.unpack('>H', payload[4:6])[0]
            resp_status = struct.unpack('>H', payload[6:8])[0]
            print(f"  DHU version: v{resp_major}.{resp_minor}, status={resp_status}")
            if resp_status != 0:
                print(f"  [!] Version rejected!")
                return
        elif len(payload) >= 6:
            # Maybe DHU sends version request too?
            subtype = struct.unpack('>H', payload[0:2])[0]
            if subtype == SUBTYPE_VERSION_REQUEST:
                ver_major = struct.unpack('>H', payload[2:4])[0]
                ver_minor = struct.unpack('>H', payload[4:6])[0]
                print(f"  DHU sent version REQUEST: v{ver_major}.{ver_minor}")
                print(f"  Sending version response...")
                ver_resp = struct.pack('>HHHH',
                    SUBTYPE_VERSION_RESPONSE,
                    AA_VERSION_MAJOR,
                    AA_VERSION_MINOR,
                    0,  # status OK
                )
                send_aa_frame(conn, 0, 0x03, ver_resp)
                print(f"  Sent version response: v{AA_VERSION_MAJOR}.{AA_VERSION_MINOR}, status=OK")

                # Now read DHU's response to our request
                channel, flags, payload = read_aa_frame(conn)
                print(f"  DHU response: {payload.hex()}")

        # Step 2: TLS Handshake (we are the TLS server)
        print("\n[2] TLS Handshake")
        tls = AAMemoryBIO(conn, cert_file, key_file)
        tls.do_handshake()

        # Step 3: Handle AUTH_COMPLETE
        print("\n[3] Auth Phase")
        # The phone sends AUTH_COMPLETE after TLS. Let's do that.
        auth_payload = struct.pack('>H', SUBTYPE_AUTH_COMPLETE) + b'\x08\x00'
        send_aa_frame(conn, 0, 0x03, auth_payload)
        print("  Sent AUTH_COMPLETE")

        # Step 4: Read post-TLS messages
        print("\n[4] Reading post-TLS messages...")
        print("    (Looking for ServiceDiscoveryResponse from DHU)")

        all_data = bytearray()
        msg_count = 0
        sdp_found = False
        all_messages = []

        for read_attempt in range(50):
            try:
                data = tls.read(65536)
                if not data:
                    continue

                all_data.extend(data)

                # Parse AA frames from decrypted stream
                offset = 0
                while offset + 4 <= len(all_data):
                    ch = all_data[offset]
                    fl = all_data[offset + 1]
                    length = struct.unpack('>H', all_data[offset+2:offset+4])[0]

                    if offset + 4 + length > len(all_data):
                        break  # incomplete frame

                    frame_payload = bytes(all_data[offset+4:offset+4+length])
                    offset += 4 + length
                    msg_count += 1

                    all_messages.append({
                        'num': msg_count,
                        'channel': ch,
                        'flags': fl,
                        'payload': frame_payload,
                    })

                    print(f"\n  --- Msg {msg_count}: ch={ch} flags=0x{fl:02x} len={length} ---")

                    if ch == 0 and length >= 2:
                        msg_type = struct.unpack('>H', frame_payload[0:2])[0]
                        proto_payload = frame_payload[2:]
                        msg_names = {
                            0x0001: 'VERSION_REQUEST', 0x0002: 'VERSION_RESPONSE',
                            0x0005: 'SERVICE_DISCOVERY_REQUEST',
                            0x0006: 'SERVICE_DISCOVERY_RESPONSE',
                            0x0007: 'CHANNEL_OPEN_REQUEST',
                            0x0008: 'CHANNEL_OPEN_RESPONSE',
                            0x000B: 'PING_REQUEST', 0x000C: 'PING_RESPONSE',
                        }
                        name = msg_names.get(msg_type, f'UNKNOWN_0x{msg_type:04x}')
                        print(f"  Type: 0x{msg_type:04x} ({name})")

                        if msg_type == MSG_SERVICE_DISCOVERY_RESPONSE:
                            print(f"\n  *** SERVICE DISCOVERY RESPONSE ({len(proto_payload)} bytes) ***")
                            sdp_found = True

                        if msg_type == MSG_SERVICE_DISCOVERY_REQUEST:
                            print(f"  DHU sent SDP Request — sending our SDP Response...")
                            # Send a minimal SDP response so the DHU continues
                            # The DHU should then send ITS SDP
                            # For now just acknowledge
                            sdp_resp = build_minimal_sdp_response()
                            msg = struct.pack('>H', MSG_SERVICE_DISCOVERY_RESPONSE) + sdp_resp
                            frame = struct.pack('>BBH', 0, 0x0b, len(msg)) + msg
                            tls.write(frame)
                            print(f"  Sent minimal SDP response ({len(sdp_resp)} bytes)")

                        # Always dump protobuf for interesting messages
                        if len(proto_payload) > 0:
                            print(f"\n  Protobuf ({len(proto_payload)} bytes):")
                            print_protobuf(proto_payload, depth=1)

                            if sdp_found or length > 100:
                                # Save it
                                raw_file = os.path.join(output_dir,
                                    f"msg_{msg_count}_0x{msg_type:04x}_{timestamp}.bin")
                                with open(raw_file, 'wb') as f:
                                    f.write(proto_payload)
                                print(f"\n  Saved to: {raw_file}")

                                json_file = os.path.join(output_dir,
                                    f"msg_{msg_count}_0x{msg_type:04x}_{timestamp}.json")
                                parsed = protobuf_to_dict(proto_payload)
                                with open(json_file, 'w') as f:
                                    json.dump(parsed, f, indent=2, default=str)
                                print(f"  Saved to: {json_file}")

                    elif length >= 2:
                        msg_type = struct.unpack('>H', frame_payload[0:2])[0]
                        print(f"  Channel {ch} msg type: 0x{msg_type:04x}")
                        print(f"  Payload: {frame_payload[:64].hex()}")
                    else:
                        print(f"  Payload: {frame_payload.hex()}")

                all_data = all_data[offset:]

            except socket.timeout:
                print("  [timeout - waiting for more data]")
                if msg_count > 0:
                    break
            except ssl.SSLWantReadError:
                continue
            except ConnectionError as e:
                print(f"  [connection closed: {e}]")
                break
            except Exception as e:
                print(f"  [error: {e}]")
                import traceback
                traceback.print_exc()
                break

        # Summary
        print(f"\n{'=' * 50}")
        print(f"Summary: {msg_count} messages received")
        print(f"SDP found: {sdp_found}")
        if all_messages:
            print(f"\nMessage types seen:")
            for m in all_messages:
                if m['channel'] == 0 and len(m['payload']) >= 2:
                    mt = struct.unpack('>H', m['payload'][0:2])[0]
                    msg_names = {
                        0x0005: 'SDP_REQ', 0x0006: 'SDP_RESP',
                        0x0007: 'CH_OPEN_REQ', 0x0008: 'CH_OPEN_RESP',
                        0x000B: 'PING_REQ', 0x000C: 'PING_RESP',
                    }
                    name = msg_names.get(mt, f'0x{mt:04x}')
                    print(f"  Msg {m['num']}: ch={m['channel']} {name} ({len(m['payload'])} bytes)")
                else:
                    print(f"  Msg {m['num']}: ch={m['channel']} ({len(m['payload'])} bytes)")

        # Save all raw messages
        all_raw_file = os.path.join(output_dir, f"all_messages_{timestamp}.bin")
        with open(all_raw_file, 'wb') as f:
            for m in all_messages:
                # Write with frame header for later replay
                header = struct.pack('>BBH', m['channel'], m['flags'], len(m['payload']))
                f.write(header + m['payload'])
        print(f"\nAll messages saved to: {all_raw_file}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()
        server.close()
        print("\nDone.")


def build_minimal_sdp_response():
    """Build a minimal ServiceDiscoveryResponse protobuf.

    We need to respond with enough for the DHU to continue the handshake.
    The real SDP we want is the DHU's, but the DHU might expect ours first.

    Minimal fields:
      field 1: head_unit_name (string)
      field 2: car_model (string)
    """
    name = b"SDP-Grabber"
    model = b"Virtual"

    # field 1 = string (tag = 0x0a)
    sdp = bytes([0x0a, len(name)]) + name
    # field 2 = string (tag = 0x12)
    sdp += bytes([0x12, len(model)]) + model

    return sdp


if __name__ == '__main__':
    main()
