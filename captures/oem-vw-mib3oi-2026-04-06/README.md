# OEM Capture: Volkswagen MIB3 OI (2024)

**First OEM head-unit capture in the project.** Production Volkswagen MIB3 OI
("Modular Infotainment Toolkit, third generation, OI variant") cockpit running
against a Pixel 8 with Android Auto 16.4.661034.

## Vehicle / Hardware

| Field | Value |
|---|---|
| Make | Volkswagen |
| Model | VW3363 |
| Year | 2024 |
| Head unit hw_id | `COCKPIT_MIB3OI_GP` |
| Head unit sw_build | `2756.04` |
| Head unit build label | `C sample` |
| MAC addresses | `84:96:90:8C:34:0B`, `86:96:90:8C:77:EF` |
| AA Session UUID | `ba64e7d4-6347-47cd-9234-fb3cc41c5249` |

(All extracted from the embedded `CarInfo` / `HeadUnitInfo` protos in
`sdp_response.bin` — message 2 of `messages.jsonl`.)

## Capture Provenance

- **Tool:** `aa-capture-app` v5 (on-phone Android app)
- **Method:** `native_interceptor_regnatives` — Frida-style native `Interceptor`
  hooks on `ENGINE_SSL_read_direct` / `ENGINE_SSL_write_direct` inside
  `libconscrypt_gmscore_jni.so`. Sees plaintext after BoringSSL has decrypted
  inbound records and before it encrypts outbound ones.
- **Phone:** Pixel 8 (rooted, Magisk + frida-server), Android Auto 16.4.661034
- **Capture project:** `/mnt/e/claude/personal/android-auto-dhu/` (Windows host,
  separate Claude instance — see that project's `CLAUDE.md` for the full
  pipeline)
- **Captured:** 2026-04-06 14:49:06Z – 14:50:06Z (60s)
- **Imported into this repo:** 2026-04-07

## What's In Here

| File | Bytes | Notes |
|---|---|---|
| `messages.jsonl` | 50,307,502 | 7,954 plaintext AA messages (one JSON per line) |
| `sdp_request.bin` | 877 | Service Discovery Request from phone → VW HU |
| `sdp_response.bin` | 610 | Service Discovery Response from VW HU → phone |
| `session.json` | 456 | Capture metadata (start/end, count, queue stats) |

Capture stats from `session.json`:
- `message_count`: 7954
- `dropped_messages`: 0
- `skipped_media_frames`: 0
- `skipped_media_bytes`: 0
- `queue_high_watermark`: 257

## Wire Format (per message)

```json
{
  "seq":         1,
  "ts_ms":       5,
  "direction":   "out",
  "msg_type":    5,
  "payload_b64": "AAUKmAGJUE5HDQoaCg…",
  "payload_len": 879
}
```

- `direction` is `"in"` (HU → phone) or `"out"` (phone → HU)
- `msg_type` is the AA inner message type (the 2-byte type that lives at the
  start of a FIRST-flagged frame's plaintext payload)
- `payload_b64` is the **full plaintext payload including the 2-byte msg_type
  prefix** — i.e. `AAU…` (`0x0005`) for a ServiceDiscoveryRequest

## Format Limitations (vs the PC tcpdump pipeline)

**The on-phone hook fires on ENGINE_SSL_read/write_direct, which see TLS
plaintext but live INSIDE the AA framing layer.** That has consequences:

- ❌ **No `channel_id`.** The `[1B channel][1B flags][2B length]` outer frame
  header lives outside TLS and the hook never sees it.
- ❌ **No `flags` byte.** Same reason. You can't tell FIRST/LAST/CTRL/ENC.
- ❌ **No TLS handshake.** Hook only fires for application data.
- ❌ **Continuation fragments look like garbage `msg_type`.** When a logical
  message spans multiple wire frames, only the FIRST frame has a real type
  byte; continuations are raw payload bytes whose first two bytes get
  interpreted as a "msg_type" by the parser. Filter or reassemble accordingly.
- ❌ **Not raw network bytes.** For raw TLS records you'd need the PC pipeline
  (`phone_full_capture.py`: tcpdump on wlan0 + Frida key extraction).

**What still works for protocol analysis:**

- ✅ **SDP parses cleanly.** SDP is a single FIRST-flagged message; the full
  protobuf is in `payload_b64` of one record. `sdp_request.bin` and
  `sdp_response.bin` are pre-extracted for convenience.
- ✅ **Per-msg-type analysis works** for any signaling type whose msg_type ID
  is unambiguous across services. The msg_type spaces are mostly disjoint:
  Radio uses `0x801A–0x8023`, Car Control uses `0x8001–0x8007`, etc.
- ✅ **Direction is preserved**, so you can split by `in`/`out` for any
  per-direction validation.
- ✅ **Real production CarInfo / HeadUnitInfo values** — names, model codes,
  MACs, sw_build, hw_id — are inside `sdp_request.bin` (see hardware table
  above for the extracted fields).

## Why It Matters

`STATE.md` flagged "no OEM captures done yet → Gold tier remains unachieved"
as a v1.0 carryover blocker. This capture is the unblock:

- **First Gold-tier evidence source** for any proto whose schema/values
  match between this VW capture and the existing DHU baselines.
- **First production CarInfo** to compare against the proto sidecars (which
  currently have field schemas but unverified content semantics).
- **OEM-vs-DHU divergence detection** — first chance to answer "does the DHU
  advertise the same channel set, capability flags, and fields as a real
  production unit?"

## Caveats / Open Questions

- **Single OEM, single model, single session.** One capture is *evidence*, not
  *proof*. Anything labeled OEM-Gold off the back of just this capture is
  really "VW MIB3 OI 2024 Gold" — any other OEM (Audi MMI, BMW iDrive,
  aftermarket Pioneer/Kenwood, etc.) may diverge.
- **VW MIB3 OI is not a representative baseline.** VW infotainment firmware
  has historically been quirky (early MIB3 had Wireless AA bugs that took
  years to settle). Treat VW-specific quirks as VW-specific until a second OEM
  capture confirms otherwise.
- **No vehicle context.** The `messages.jsonl` doesn't tell you what the user
  was doing in the car during the 60s window — was the HU idle, was nav
  active, was music playing? Look at message density per channel/type to
  infer scenario.
- **Channel correlation requires inference.** Without `channel_id`, you can't
  point at a message and say "this came in on channel 8." If you need that,
  the PC pipeline (`phone_full_capture.py`) is the path — but that's
  out-of-scope for v2.0 analysis-only work.

## Related

- Capture pipeline source: `/mnt/e/claude/personal/android-auto-dhu/CLAUDE.md`
  (other Claude instance)
- Decryption methodology: `/mnt/e/claude/personal/android-auto-dhu/docs/phone-capture-pipeline.md`
- DHU baseline captures (for comparison): `captures/general/`,
  `captures/idle-baseline/`, `captures/music-playback/`,
  `captures/active-navigation/`
- Project blocker note: `.planning/STATE.md` — "Blockers/Concerns" section


## Analysis Outputs

Phase 7 analysis artifacts live under `analysis/reports/oem-vw/`:

- [`sdp-values.md`](../../analysis/reports/oem-vw/sdp-values.md) — production SDP values (HeadUnitInfo, 13 channels)
- [`sdp-values.json`](../../analysis/reports/oem-vw/sdp-values.json) — machine-readable SDP values
- [`msg-type-classification.md`](../../analysis/reports/oem-vw/msg-type-classification.md) — per-msg-type fragment classification (from plan 07-01)
- [`msg-type-classification.json`](../../analysis/reports/oem-vw/msg-type-classification.json) — machine-readable classification
- [`coverage-manifest.md`](../../analysis/reports/oem-vw/coverage-manifest.md) — VW session coverage (observed / intrinsic gaps / comparative gaps / anomalies)
- [`coverage.json`](../../analysis/reports/oem-vw/coverage.json) — machine-readable coverage manifest with `baseline_snapshot_hash`
- [`candidate-oem-only-msg-types.md`](../../analysis/reports/oem-vw/candidate-oem-only-msg-types.md) — msg_types seen in VW but not DHU baselines (filtered through fragment classification, labeled `candidate`)
- [`candidate-oem-only-msg-types.json`](../../analysis/reports/oem-vw/candidate-oem-only-msg-types.json) — machine-readable candidate list

**Correction applied 2026-04-07:** the SDP direction labels in the file table above were swapped. Plan 07-02 verified by direct decode that `sdp_request.bin` is phone→HU and `sdp_response.bin` is HU→phone, and fixed the table in a targeted one-line edit.
