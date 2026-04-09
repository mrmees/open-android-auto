# OEM Match Policy

This document defines the closed-enum MATCH and NOMATCH rule IDs that Phase 10
(the Gold→Platinum promotion walk) cites when transitioning a sidecar between
tiers. The rule set is small, fine-grained, and deliberately permanent: once
Phase 10 cites `MATCH-04`, that rule's meaning cannot be renamed without
rewriting every sidecar citation. The schema in `audit-schema.json` enforces
the IDs as a closed enum, so ad-hoc drift is caught at validation time rather
than discovered during audit.

Phase 9 defines these rules; Phase 10 is the first consumer. The source of
truth for the tier model itself is [01-confidence-tiers.md](01-confidence-tiers.md);
for what CANNOT be claimed from an on-phone hook capture, see
[06-capture-non-claim-boundary.md](06-capture-non-claim-boundary.md).

---

## MATCH rules

Every `platinum_evidence` entry MUST cite at least one MATCH rule via the
closed-enum `match_rules` list. Cite every rule that applies — cherry-picking
is not allowed. The following eight rules form the complete, closed enum.

### MATCH-01 — Message presence

**Definition.** The `msg_type` was observed on the expected service in the VW
capture at least once (`N = 1` is sufficient; see the baseline threshold
section below).

**Example.** `RadioStateRequest` observed once on service 15 (Radio).

**Phase 10 citation.** `match_rules: [MATCH-01]` as the baseline whenever any
observation exists for a proto.

### MATCH-02 — Standalone full payload

**Definition.** Presence AND the observation was classified `standalone` per
the OEM-01 taxonomy (not `probable_first`, not `continuation_or_garbage`). The
full wire payload is available for field-level decoding — not just a fragment.

**Example.** `SensorBatchRequest` observed with `label=standalone` on service 1.

**Phase 10 citation.** Cite `MATCH-02` alongside `MATCH-01` whenever the full
payload is available, even if no field-level claim is being made. Keeps
payload completeness distinct from field verification.

### MATCH-03 — Reassembled multi-fragment

**Definition.** Observation classified `reassembled` per OEM-01 (multi-fragment
payload successfully reassembled at capture time).

**Example.** *(none in v1.5)*

**Phase 10 citation.** None in v1.5. Zero usage — Phase 7's classifier reports
`reassembled=0` on the live VW capture. The rule is retained in the closed
enum for future captures with fragmented payloads; removing it later would be
a breaking schema change.

### MATCH-04 — Field-level value match

**Definition.** A specific field's decoded value matches the declared proto
field type and semantics. Implies MATCH-02 (you need a standalone payload to
decode fields). Requires `applicability: fields` and a populated `fields` list
on the sidecar evidence entry.

**Example.** `HeadUnitInfo.make` observed with value `"Volkswagen"`, matching
the declared `string` type.

**Phase 10 citation.** `match_rules: [MATCH-01, MATCH-02, MATCH-04]` plus
`applicability: fields, fields: [<field_numbers>]`.

### MATCH-05 — Enum value match

**Definition.** An observed enum value matches a declared enum value in the
proto. Special case of MATCH-04 for enums specifically, kept distinct because
enum fingerprints are the stable signal across APK obfuscation.

**Example.** `VideoResolution = VIDEO_1920x1080` observed in a `VideoConfig`
message.

**Phase 10 citation.** Cite `MATCH-05` alongside `MATCH-04` when the matched
field is an enum.

### MATCH-06 — Repeat observation

**Definition.** The same `(msg_type, direction)` was observed `N >= 2` times
in the capture session.

**Example.** `PingRequest` observed 6 times during the 60s session.

**Phase 10 citation.** Optional — cite when available. Not required for
MATCH-01 eligibility; MATCH-06 is the stronger rule.

### MATCH-07 — Cross-direction observation

**Definition.** Both `phone -> HU` and `HU -> phone` directions were observed
for the same proto.

**Example.** `Ping` observed in both directions during the session.

**Phase 10 citation.** Useful for protos with request/response symmetry. Cite
alongside `MATCH-01`/`MATCH-06` when both directions are present.

### MATCH-08 — SDP descriptor match

**Definition.** The service/channel descriptor in VW's `sdp_response.bin`
matches the declared proto's channel binding. This is SDP-layer evidence
rather than per-message layer evidence.

**Example.** VW SDP declares `sensor_channel` on channel 8; `SensorRequest`'s
proto claims the Sensor service binding → MATCH-08.

**Phase 10 citation.** Always citable when the declared service appears in
VW's SDP response, even if no specific message was observed on the wire. The
minimum honest citation for any proto bound to a service that VW exercised.

---

## NOMATCH rules

NOMATCH rules record the reason a claim is explicitly NOT made. They appear
in the optional `nomatch_rules` list on a `platinum_evidence` entry. The
following four rules form the complete, closed enum.

### NOMATCH-01 — Below framing layer

**Definition.** The claim is about a surface the VW capture CANNOT validate:
`channel_id`, `flags`, outer frame header semantics, encryption, or
fragmentation behavior. TIER-05 operationalized.

**Example.** Any claim of the form "`VideoFocusNotification` uses
`channel_id: 3`" — the on-phone hook fires above the framing layer, so
`channel_id` is literally invisible to the capture.

**See.** [06-capture-non-claim-boundary.md](06-capture-non-claim-boundary.md)
for the full list of 5 non-claim surfaces and why the hook cannot see them.

### NOMATCH-02 — Not observed

**Definition.** The proto exists in the declaration but was not seen in the
VW capture. No claim is made either way — this is honest absence and does
NOT demote the proto's existing tier.

**Example.** `RadioSearchRequest` does not appear in the 60s VW session; the
sidecar stays at Gold rather than being promoted to Platinum.

### NOMATCH-03 — Ambiguous attribution

**Definition.** Observed, but msg_type attribution is ambiguous across
services (e.g., msg_type 0x8002 could belong to Service A or Service B and
the capture lacks enough context to pin which one).

**Example.** Per Phase 7 Plan 02: VW Tier B records with multiple
`sdp_candidates` — no single service can be attributed.

### NOMATCH-04 — Fragment-only observation

**Definition.** Observed but classified `continuation_or_garbage` per OEM-01.
No standalone payload is available, so fields cannot be verified and even the
msg_type is uncertain (it may be trailing fragment bytes rather than a real
message boundary).

**Example.** Any observation with Phase 7 label `continuation_or_garbage`
(approximately 3804 out of 7954 records in the live VW capture).

---

## Baseline observation threshold

`N = 1` observation is sufficient for MATCH-01. `MATCH-06` is the stronger
rule that requires `N >= 2`.

**Rationale.** The VW capture is a single 60s session. Demanding `N >= 2`
universally would reject legitimate once-per-session events — connection
handshakes, initial status updates, one-shot HVAC reports — and would penalise
protos for being event-triggered rather than periodic. MATCH-06 stays
available for Phase 10 to cite when repeat observation IS present, but is not
a precondition for promotion.

---

## Phase 10 citation format

A promotion entry cites every applicable rule. The `match_rules` list is a
closed-enum array with `minItems: 1` and `uniqueItems: true`.

**Example citation.**

```yaml
- type: platinum_evidence
  ...
  applicability: fields
  fields: [1, 3, 4]
  match_rules: [MATCH-01, MATCH-02, MATCH-04, MATCH-06]
```

This says: the msg was observed (`MATCH-01`), had a full standalone payload
(`MATCH-02`), had field-level value verification for fields 1/3/4 (`MATCH-04`),
and was observed `N >= 2` times during the session (`MATCH-06`). Phase 10 MUST
cite every rule it satisfied — cherry-picking a subset is not allowed because
audit trails need full detail to survive re-examination.

A minimum honest citation when only SDP-level evidence is available is
`match_rules: [MATCH-08]`, with `applicability: message` (no `fields` list).

---

## Closed enum enforcement

The schema enforces `match_rules` as a closed-enum list via
`items.enum + uniqueItems + minItems: 1` (see
[audit-schema.json](audit-schema.json)). Unknown rule IDs, duplicates, and
empty lists are all rejected at schema load. This prevents ad-hoc citation
drift over time: a future contributor cannot invent an out-of-enum rule ID
or pass an empty list without the schema validator catching it.

The `nomatch_rules` list uses the same pattern with the 4 NOMATCH IDs.
