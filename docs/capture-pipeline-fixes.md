# Capture Pipeline Bug Report for MINIMEES Claude

**From:** claude-dev (open-android-auto validator)
**Script:** `E:\claude\personal\android-auto-dhu\aa_parse_capture.py`
**Date:** 2026-03-07

## Summary

The proto_stream_validator on claude-dev decoded 15,242 frames from 4 DHU captures. After fixing the validator to handle service-type-aware resolution (channel IDs are session-specific), we achieved ~54% decode rate. The remaining ~46% is correctly filtered (raw AV data, SSL, version exchange). However, **74 frames across the 4 captures are corrupt** due to 3 bugs in `aa_parse_capture.py`.

---

## Bug 1: AA frame header read from wrong offset (CRITICAL)

### Symptom

MediaPlaybackMetadata messages appear on channel 0 (control) with `msg_type=0x8003`. Decoded payload contains song metadata ("Born To Die", "Get Out My Head"), confirming this is media info, not a control channel message.

### Evidence

```
music-playback frame 125: ch=0 flags=1 msg_type=0x8003 len=16120
  payload decoded: b'\n\x0bBorn To Die\x12\x0cLana '
```

Occurs in every capture: general (1x), idle-baseline (1x), music-playback (7x), active-navigation (1x) = **10 frames total**.

### Root Cause

`aa_parse_capture.py` line 195-196:
```python
aa_channel = data[i - 4]
aa_flags = data[i - 3]
```

This reads the AA outer frame header as 4 bytes before the TLS record. This is wrong when:
1. The TLS record is NOT immediately preceded by an AA frame header (e.g., the AA frame was fragmented across multiple TLS records)
2. The pcap packet boundary falls between the AA header and the TLS record
3. The AA frame spans multiple TLS Application Data records

The `flags=1` (0x01) on these misrouted frames confirms the issue — valid post-TLS AA flags are 0x03 (plaintext first+last), 0x0b (encrypted first+last), 0x0f (encrypted+control). Flag 0x01 means only FIRST bit set, which suggests we're reading a byte that isn't actually a flags byte.

### Fix

Instead of reading 4 bytes before each TLS record, you need to **reassemble the decrypted TLS stream first**, then parse AA frames from the reassembled plaintext. The AA framing is INSIDE the TLS layer, not outside it.

Current approach (wrong):
```
pcap bytes: [...AA_HDR...][TLS_RECORD][...AA_HDR...][TLS_RECORD]
                 ↑ read from here      ↑ read from here
```

Correct approach:
```
1. Decrypt all TLS Application Data records in order → plaintext stream
2. Parse AA frames from plaintext: [1B channel][1B flags][2B len BE][payload]
3. Within payload: [2B msg_type BE][proto_data]
```

The AA wire protocol puts the channel/flags/length header INSIDE the encrypted TLS payload, not outside it. The current code is reading random pcap bytes as channel/flags.

Wait — actually, looking more carefully at the code and the fact that MOST frames decode correctly (731 out of 741 in general), the header IS outside TLS for the common case. Let me reconsider.

The AA protocol layers:
- USB/TCP transport → AA frames [channel][flags][length][payload]
- When encrypted: the entire AA frame (including header) goes into a TLS record
- OR: the AA header is outside and only the payload is encrypted

Looking at your code: you read channel/flags from `data[i-4:i-2]` (before the TLS record header at offset `i`), then decrypt the TLS record to get the plaintext payload. This works when each TLS record corresponds to exactly one AA frame and the AA header is right before the TLS record in the TCP stream.

The failures (10 frames) likely happen when:
- A large AA message gets split across multiple TLS records
- The 4 bytes before the TLS record aren't actually an AA header

**Revised fix:** Add validation after reading the AA header:
```python
aa_channel = data[i - 4]
aa_flags = data[i - 3]
aa_length = struct.unpack('>H', data[i-2:i])[0]

# Validate: channel should be 0-14, flags should be a known value
VALID_FLAGS = {0x03, 0x08, 0x0a, 0x0b, 0x0f}
if aa_channel > 14 or aa_flags not in VALID_FLAGS:
    # This TLS record is a continuation of a multi-record AA frame
    # Skip AA header parsing, use previous frame's channel/flags
    # OR: mark as "continuation" and skip entirely
```

---

## Bug 2: Undecrypted frames emitted as messages (HIGH)

### Symptom

Frames on `media_info` and `nav_status` channels have random high msg_type values (0x38ec, 0xb314, 0xed5f, 0x8989, etc.) with high-entropy payloads. These are NOT valid AA protocol message IDs.

### Evidence

```
music-playback:
  frame 126: ch=12 flags=8  msg=0x38ec len=16124 payload=38ec4e4f4fa3b72f5e7c...
  frame 127: ch=12 flags=8  msg=0xb314 len=16124 payload=b314c27ebf33afefeea7...
  frame 128: ch=12 flags=8  msg=0xed5f len=16124 payload=ed5f9fe7f076abe85d4c...
```

Patterns:
- Always `flags=8` (0x08) or `flags=0x0a` — these are "encrypted first frame" and "encrypted continuation" flags
- Payload is high-entropy (encrypted/compressed data)
- Fixed payload size of 16124 bytes (suspicious — looks like an MTU)
- Appears on ch12 (media_info) and ch6 (media_sink)

Occurs: general (5), idle-baseline (5), music-playback (35), active-navigation (5) = **50+ frames**.

### Root Cause

These frames have `flags=0x08` which means "encrypted data, first frame". Your code treats flags 0x08 and 0x0a as regular decrypted messages. But these flags indicate the AA payload itself is encrypted (the inner encryption, separate from TLS). The TLS decryption works fine, but the resulting plaintext is still AA-encrypted.

Looking at the flags more carefully:
```python
FLAG_FIRST = 0x01
FLAG_LAST = 0x02
FLAG_CTRL = 0x04
FLAG_ENC = 0x08
```

- `flags=0x0b` (FIRST|LAST|ENC) = encrypted control message, single frame — your code handles these correctly
- `flags=0x08` (ENC only) = encrypted data, first frame of a multi-frame message — NOT a complete message
- `flags=0x0a` (LAST|ENC) = encrypted data, last frame of a multi-frame message

The code doesn't reassemble multi-frame messages. It emits each TLS record as a separate message, which means:
1. Multi-frame AA messages get split into fragments
2. The first 2 bytes of each fragment are read as `msg_type`, but they're actually continuation data

### Fix

Add flag-based filtering:
```python
if plaintext is not None:
    # Only emit as a complete message if it's a single-frame message (FIRST|LAST set)
    is_first = bool(aa_flags & FLAG_FIRST)
    is_last = bool(aa_flags & FLAG_LAST)

    if is_first and is_last:
        # Complete single-frame message — parse msg_type normally
        msg_type = struct.unpack('>H', plaintext[:2])[0]
        # ... emit message
    elif is_first:
        # First frame of multi-frame message — start reassembly buffer
        reassembly_buffer = plaintext
        reassembly_channel = aa_channel
    elif is_last:
        # Last frame — complete reassembly, then parse msg_type from full payload
        reassembly_buffer += plaintext
        msg_type = struct.unpack('>H', reassembly_buffer[:2])[0]
        # ... emit complete reassembled message
    else:
        # Middle frame — append to reassembly buffer
        reassembly_buffer += plaintext
```

Simpler alternative if you don't want to reassemble: just skip frames where `flags & 0x03 != 0x03` (not both FIRST and LAST):
```python
if not (aa_flags & FLAG_FIRST and aa_flags & FLAG_LAST):
    continue  # skip fragments
```

This loses multi-frame messages entirely but eliminates the garbage.

---

## Bug 3: `general/channel_map.json` has swapped labels (LOW)

### Symptom

In the general capture, ch10 is labeled "media_info" and ch12 is "nav_status". All other captures correctly label ch10 as "navigation" and ch12 as "media_info".

### Evidence

The SDP binary (`sdp_response.bin`) is **byte-for-byte identical** across all 4 captures (844 bytes, same hash). The current `parse_sdp_channels()` function correctly produces ch10=navigation, ch12=media_info when run against this SDP data.

```
ch10 config_raw: 080a 42 0d 08f40310011a06086410641810
                      ^^ field 8 (0x42) = NavigationChannelConfig
ch12 config_raw: 080c 4a 00
                      ^^ field 9 (0x4a) = MediaInfoChannelConfig
```

### Root Cause

The `general/channel_map.json` was generated by an older version of `aa_parse_capture.py` that had the field number → service type mapping wrong (likely fields 8 and 9 were swapped).

### Fix

Re-run the current `aa_parse_capture.py` on the general capture to regenerate `channel_map.json`. No code changes needed — this is already fixed in the current version.

OR: just delete and regenerate `general/channel_map.json`:
```
python aa_parse_capture.py --pcap <general_pcap> --keylog <keylog> --out captures/general/
```

---

## Bug 4: `flags=0x00` frames on control channel (LOW)

### Symptom

52 frames in music-playback have `ch=0 flags=0 msg=0x0000 len=16120`. Flag 0x00 means no FIRST, no LAST, no CTRL, no ENC — which is not a valid AA flag combination.

### Root Cause

Same as Bug 1 — these are TLS records where the 4 bytes before the record aren't an AA header. The "channel=0, flags=0, msg_type=0" are just whatever bytes happen to be at that offset. The constant `len=16120` across all of them suggests these are large TLS records (probably AV data) where the AA framing doesn't align with TLS record boundaries.

### Fix

Same as Bug 1 — validate AA header values before using them.

---

## Flags Summary

Here's the actual flags distribution from the music-playback capture:

| Flags | Hex | Count | Meaning | Status |
|-------|-----|-------|---------|--------|
| 11 | 0x0b | 4750 | FIRST\|LAST\|ENC (single-frame encrypted) | OK - most messages |
| 15 | 0x0f | 28 | FIRST\|LAST\|CTRL\|ENC (encrypted control) | OK |
| 0 | 0x00 | 52 | No flags set | BUG - invalid AA header |
| 8 | 0x08 | 44 | ENC only (encrypted first fragment) | BUG - fragment, not complete msg |
| 10 | 0x0a | 60 | LAST\|ENC (encrypted last fragment) | BUG - fragment, not complete msg |
| 1 | 0x01 | 4 | FIRST only | BUG - invalid (from bad header read) |
| 2 | 0x02 | 3 | LAST only | BUG - invalid (from bad header read) |

Only `0x0b` (4750) and `0x0f` (28) are valid single-frame encrypted messages = 4778/4941 = **96.7% of frames are fine**.

---

## Recommended Fix Priority

1. **Filter by flags** (quick win): Skip any frame where `flags & 0x03 != 0x03`. This eliminates all corrupt frames immediately. You lose multi-frame messages but those are mostly large media data that the validator skips anyway.

2. **Validate AA header** (medium): Check `channel <= 14` and `flags in {0x03, 0x0b, 0x0f}` before trusting the header bytes.

3. **Reassemble multi-frame messages** (nice to have): Buffer fragments and reassemble. Only needed if you want to decode large messages that span multiple TLS records.

4. **Regenerate general channel_map.json** (trivial): Re-run current script on general capture.
