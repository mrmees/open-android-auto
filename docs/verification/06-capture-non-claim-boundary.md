# Capture Evidence Boundary — VW OEM Capture (and Future On-Phone Captures)

This document is the single source of truth for what the VW MIB3 OI OEM
capture — and any future on-phone AA capture that uses the same framing-layer
hook — CANNOT validate. It exists so that contributors citing "VW evidence"
can check one page to see whether a given claim is even eligible for
verification by that evidence source.

Phase 9 publishes this doc; Phase 10's promotion walk cites it via
[NOMATCH-01](05-oem-match-policy.md#nomatch-01--below-framing-layer). Every
claim about a surface listed here must cite NOMATCH-01 as its non-match
reason, because the capture's hook literally cannot see the surface — no
amount of re-processing existing capture data can change that.

The tier model (Gold, Platinum, retracted) is defined in
[01-confidence-tiers.md](01-confidence-tiers.md). The rule IDs Phase 10 cites
are defined in [05-oem-match-policy.md](05-oem-match-policy.md).

---

## The 5 non-claim surfaces

The VW capture's on-phone hook fires inside the AA framing layer: below the
outer frame parser and above the protobuf decoder. It sees the
reassembled, decrypted protobuf payload — exactly what the project needs to
verify proto field semantics — and nothing else. Each of the five surfaces
below lives on the "below the hook" side of that boundary.

### 1. channel_id

The on-phone hook fires per channel-handler, so the channel is implicit in
the hook target rather than a value the hook reads off the wire. No
`channel_id` field is recorded in `messages.jsonl`, and the capture pipeline
has no way to recover it. Claims of the form "proto X is sent on
channel_id N" cannot be verified or refuted by the VW capture.

### 2. flags

The `[1B channel][1B flags][2B length BE]` outer frame header carries a
`flags` byte that encodes `FrameType`, `MessageType`, and `EncryptionType`
bits (see `docs/protocol-overview.md`). The hook fires after the outer frame
is consumed, so the flags byte is gone by the time the hook sees the
payload. The capture cannot validate any claim about `flags` behavior.

### 3. Outer frame header layout

Related to (1) and (2): the 4-byte outer frame header's byte layout
(`[1B channel][1B flags][2B length BE]`) is not recorded. Claims about
alternative framing, header sizes, or variable-length header variants
cannot be validated against the VW capture.

### 4. Fragmentation semantics

AA fragments large payloads across multiple frames, with continuation frames
signalled by the `FrameType` bits in the flags byte. The hook fires on the
*reassembled* payload — by the time the hook runs, the fragments have
already been reassembled by the framing layer, and the per-fragment wire
state is invisible. Claims about fragmentation thresholds, fragment ordering,
or reassembly edge cases cannot be validated by the capture.

### 5. Encryption / TLS behavior

The AA session is wrapped in TLS 1.2 (BoringSSL). The on-phone hook fires
*after* decryption — it sees plaintext protobuf bytes, not ciphertext. Any
claim about cipher suites, TLS version, handshake behavior, or encryption
boundaries cannot be validated by the VW capture's payload stream. (TLS
session artifacts from separate reverse-engineering work — the Frida
master-secret extraction documented in MEMORY.md — live at the socket
layer, not in `messages.jsonl`.)

---

## Why the hook is where it is

The hook's location is a deliberate trade-off. The project's primary
verification goal is proto field semantics: do the observed values match the
declared field types and enums? That question needs the decoded protobuf
payload, which is exactly what the hook captures. Moving the hook lower
(wire-bytes level) would enable validation of the surfaces above, but would
complicate proto decoding dramatically: the hook would then have to reimplement
frame reassembly and protobuf decoding outside the phone's own AA stack, and
stay synchronized with whatever internal wire changes Google ships in future
AA versions.

The honest trade-off: wire-level surfaces are out of scope for the current
capture methodology in exchange for reliable proto-level evidence. This
document names the cost so that Phase 10 can cite it rather than pretending
the gap doesn't exist.

---

## What this means for TIER-04 promotions

Any claim Phase 10 makes about one of the 5 surfaces above MUST cite
[NOMATCH-01](05-oem-match-policy.md#nomatch-01--below-framing-layer) in its
`nomatch_rules` list. `NOMATCH-01` exists specifically to operationalize this
doc's scope boundary — it is the "below framing layer" rule.

A promotion that would otherwise look like "Platinum / single-OEM because
`channel_id: 3` was observed" is a category error: the `channel_id` was never
observed, regardless of how complete the rest of the evidence is. Phase 10
MUST either (a) drop the channel_id claim, (b) cite NOMATCH-01, or (c) scope
the promotion to the fields the hook can actually see.

Conversely, a claim about a proto field's *value* (e.g.,
`HeadUnitInfo.make == "Volkswagen"`) is fully in scope, because the decoded
field value lives above the hook — the hook sees exactly those bytes.

---

## Other places these surfaces are discussed

The following docs reference framing-layer surfaces. Channel docs in the
first group get an automated cross-link callout pointing back to this file
(inserted by `analysis/tools/cross_link_walker`), so a reader who lands on
one of them sees the scope boundary immediately.

**Channel docs with automated cross-link callouts:**

- `docs/channels/wifi-projection.md`
- `docs/channel-map.md`
- `docs/channels/audio.md`
- `docs/channels/video.md`
- `docs/channels/sensor.md`

**Docs outside the automated cross-link scope that still discuss frame
headers (listed for reader awareness only):**

- `docs/interactions/02-version-ssl-auth.md` — frame header ASCII diagrams
- `docs/interactions/03-service-discovery.md` — `channel_id` in frame headers
- `docs/interactions/04-channel-lifecycle.md` — fragmentation via frame header
- `docs/protocol-overview.md` — 4-byte frame header definition
- `docs/capture-pipeline-fixes.md` — debug reference to the frame header bytes
- `docs/verification/03-verification-procedures.md` — frame header in the
  legacy `oem_capture` procedure section

No automated cross-link is inserted into the second group: they are explainer
docs rather than channel references, and a cross-link on every mention of the
frame header would be visual noise.

---

## Future captures

A second OEM capture with a lower-level hook — bytes-off-the-wire rather than
framing-layer-internal — WOULD be able to validate the 5 surfaces above.
Acquiring such a capture is out of scope for v1.5 (see CAP-01 in the v2
deferred section of `REQUIREMENTS.md`).

The closed-enum design of `match_rules` and `nomatch_rules` means such a
future capture would NOT require a schema migration: new MATCH rules covering
the wire surfaces could be added, and NOMATCH-01's scope could be narrowed
doc-side without renaming the rule ID. The rule IDs themselves are permanent.
