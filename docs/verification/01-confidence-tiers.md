# Confidence Tiers

## Quick Reference

The confidence ladder is:

```
unverified -> bronze -> silver -> gold -> platinum
```

plus `retracted` as a separate, non-ordinal state (a proto that was promoted
and then invalidated). The ladder is strictly ordered: a proto at Silver
cannot jump directly to Platinum — it must earn Gold first.

| Tier | Evidence required | Meaning |
|------|-------------------|---------|
| **Platinum** | Gold prerequisites AND OEM wire capture confirmation | Production-verified on at least one OEM. Badge ALWAYS shows scope qualifier: `Platinum / single-OEM` or `Platinum / multi-OEM`. |
| **Gold** | Deep-trace APK analysis + cross-version verified across 2+ APK versions | Handler-level trace produces unambiguous proto identity; structure is stable across versions. Matches the 32 existing Gold sidecars (no migration required by the Phase 9 rewrite). |
| **Silver** | 2+ distinct evidence types | Corroborated from independent sources (e.g., `apk_static` + `cross_version`). |
| **Bronze** | Any single piece of evidence | Supported by one source; directionally correct. |
| **Unverified** | None yet | Known to exist but not yet confirmed. |
| **Retracted** | *(non-ordinal)* | A proto that was previously promoted, then invalidated (wrong class fingerprint, obfuscated-name collision, or semantic misidentification). Downstream tools treat `retracted` entries as "do not cite as evidence." |

See [04-source-provenance.md](04-source-provenance.md) for which sources are
valid, [05-oem-match-policy.md](05-oem-match-policy.md) for the MATCH/NOMATCH
rule IDs Phase 10 cites during Platinum promotion, and
[06-capture-non-claim-boundary.md](06-capture-non-claim-boundary.md) for the
surfaces a Platinum-scoped on-phone capture CANNOT validate.

---

## Unverified

No evidence yet. Phase 2 seed imports enter the system at this tier. Unverified
is a valid state — it indicates a proto field or message type is known to
exist (e.g., referenced in decompiled code) but no structured verification
evidence has been recorded.

Unverified does not mean "wrong." It means "not yet examined."

## Bronze

Single-source evidence. A claim reaches Bronze when it has **any single piece
of evidence** from a valid source. One `apk_static` entry, one
`dhu_observation`, one `cross_version` match — any of these moves the claim
out of Unverified.

Bronze means the claim is directionally correct but has not yet been
independently corroborated. It should be treated as a working assumption
rather than established fact.

## Silver

Corroborated claim with independent evidence. A claim reaches Silver when it
is supported by **two or more distinct evidence types**.

The key word is *types*. Two entries of the same evidence type do not
constitute independent corroboration:

- `apk_static` + `apk_static` (different methods) = still one type = **Bronze**
- `apk_static` + `cross_version` = two types = **Silver**
- `apk_static` + `dhu_observation` = two types = **Silver**

Silver represents high confidence from static analysis. The claim has been
verified through independent methodologies that arrived at the same
conclusion. Phase 8's cross-version walker promoted ~143 protos to Silver in
the v1.x milestone work.

## Gold

**Phase 9 redefinition.** Gold is "deep-trace APK analysis + cross-version
verified." This matches what the 32 existing Gold sidecars already represent:
each one has a handler-level trace through the APK (e.g., `ied.java m20258P`
for `VideoFocusRequest`) that unambiguously pins the obfuscated class to a
proto, plus structural consistency across 2+ APK versions. No migration of
existing Gold sidecars is required — the rewrite matches them, not the other
way around.

Gold does NOT require OEM capture evidence. That was the pre-Phase-9
definition; it's been moved up to Platinum. The move reflects reality: the
deep-trace APK work was already producing ground-truth evidence, and calling
that "Gold" is honest.

A Silver proto reaches Gold by adding a `deep_trace` or `apk_deep_trace`
evidence entry that traces the proto through its handler class in the APK
(see [03-verification-procedures.md](03-verification-procedures.md) for the
procedure). Cross-version consistency is a prerequisite — if the handler
trace can't be reproduced across the version set the sidecar covers, the
proto stays at Silver.

## Platinum

Platinum is **strictly above Gold**. It requires BOTH:

1. **All Gold prerequisites** — deep-trace APK evidence + cross-version
   structural consistency. A Silver proto cannot jump directly to Platinum;
   it must earn Gold first (via deep-trace APK work + cross-version
   verification), and THEN receive a Platinum promotion once OEM capture
   evidence lands.
2. **OEM wire capture confirmation** — at least one `platinum_evidence` entry
   in the sidecar's evidence array, citing a real capture file and at least
   one `MATCH-*` rule from
   [05-oem-match-policy.md](05-oem-match-policy.md).

The Platinum tier was introduced in Phase 9 to honestly represent the jump
from "we're confident this is the proto because the APK says so across
versions" to "we've actually seen this proto on the wire between a phone and
a production head unit."

Phase 10 is the first promotion walker for Platinum. Protos matched in the
OEM capture but without Gold prerequisites receive the sidecar-level flag
`oem_match_pending_gold: true` instead of being promoted (see below).

## Retracted

Retracted is a **non-ordinal** state. A retracted sidecar was previously
promoted to some tier (typically Silver, occasionally Bronze), then later
invalidated when deep-trace work revealed the identification was wrong: the
obfuscated class name was reused across APK versions for different protos,
or a BFS-triage name was fabricated without direct evidence, or the proto
structurally matched something else entirely.

Retraction records WHAT went wrong so the mistake doesn't repeat. Downstream
tools interpret `confidence: retracted` as "do not cite as evidence." The 6
retracted sidecars currently in the repo all validate against the Phase 9
schema; several of them carry legacy `retraction`, `previous_evidence`, or
`retraction_reason` top-level fields preserved for the audit trail.

Retracted sidecars are NEVER deleted — they stand as documentation of the
re-examination that caught the error.

---

## Platinum scope: the single-OEM trap

A Platinum promotion says "this proto has been verified against one OEM
capture." That is materially different from "this proto is the production
truth for all Android Auto head units." The VW MIB3 OI capture (2024, AA
16.4.661034) is the only OEM capture in v1.5, so every Platinum promotion in
v1.5 is a single-OEM claim. Until and unless a second OEM capture lands, a
reader cannot distinguish "VW-specific quirk" from "universal OEM behavior"
by looking at a single Platinum sidecar.

This is the **single-OEM trap**: naming it up-front on every badge is the
project's defense against silently treating single-OEM evidence as universal
truth.

### `platinum_scope` sidecar field

Every Platinum sidecar MUST set a top-level `platinum_scope` field:

- `platinum_scope: single_oem` — one OEM capture corroborates the proto.
  Every Phase 10 promotion in v1.5 uses this value.
- `platinum_scope: multi_oem` — two or more OEM captures from distinct
  vehicles/head units agree. Reserved for v2 / MOEM-01..03; not emitted in
  v1.5 but representable in the schema so v2 work does not need another
  migration.

The schema enforces this: if `confidence: platinum` is set, `platinum_scope`
must be set. Sidecars at lower tiers MUST NOT set `platinum_scope`.

### Badge rendering rule

**Badges ALWAYS show the scope qualifier.** A reader NEVER sees bare
`Platinum`. The rendered badge formats are:

- `Platinum / single-OEM`
- `Platinum / multi-OEM`

Phase 12's coverage dashboard and every per-channel doc honor this rule. The
`/ single-OEM` or `/ multi-OEM` suffix is part of the tier name when
rendered; there is no prose footnote or tooltip qualifier that could be
missed. If this is visually inconvenient, that inconvenience IS the point —
it keeps the single-OEM trap visible rather than buried in methodology prose.

### `oem_match_pending_gold` flag

Phase 10 will find protos that match in the VW capture but don't yet have
Gold prerequisites (Bronze or Silver protos that were seen on the wire). They
cannot be promoted to Platinum directly, because the ladder is strict: no
skipping Gold.

Instead, such sidecars get a top-level boolean flag
`oem_match_pending_gold: true`. The flag is a sidecar-level property (NOT an
entry inside the evidence array), so it can be queried cheaply. Phase 10
emits a worklist report listing every sidecar carrying the flag; future
deep-trace work consumes the worklist and promotes protos to Gold first,
then Platinum on a later pass.

Phase 9 defines the flag and the worklist contract. Phase 10 is the first
producer. Phase 11+ are the consumers.

---

## Evidence Types

Seven evidence types are defined (four from the v1.0 design, two legacy
types retained for backward compatibility with pre-Phase-9 Gold sidecars,
and one new Phase 9 type):

### `apk_static`

**Source.** Static analysis of decompiled Android Auto APKs (currently 15.9,
16.1, 16.2, 16.4).

**What it provides.** Proto structure, field names, enum values, string
constants, call graphs, type relationships.

**Method tags.** Open vocabulary. Suggested values include `bfs_trace`,
`enum_match`, `string_const`, `proto_access`, `call_graph`, `switch_map`.
Regardless of method tag, all `apk_static` entries count as **one** evidence
type for promotion purposes.

### `dhu_observation`

**Source.** Runtime observation from Google's Desktop Head Unit test harness
(DHU 2.1).

**What it provides.** Message flow, sensor processing pipelines, runtime
behavior, channel lifecycle.

**Limitations.** The DHU is a test environment. Its behavior may diverge
from production OEM head units. For this reason, `dhu_observation` is valid
for Bronze and Silver but **never sufficient for Gold or Platinum**.

### `cross_version`

**Source.** Same proto structure confirmed across multiple APK versions
(e.g., 15.9, 16.1, 16.2, 16.4).

**What it provides.** Structural stability evidence. A field or message type
that persists unchanged across versions is more likely to be part of the
stable protocol surface. Phase 8's walker is the primary producer.

**Independence.** `cross_version` counts as a **separate type** from
`apk_static`. Even though both derive from APK analysis, cross-version
stability is a distinct signal from any single-version static analysis
finding.

### `deep_trace` and `apk_deep_trace` (legacy Gold-tier types)

**Source.** Handler-level trace through the APK that pins an obfuscated
class to a proto identity (e.g., `ied.java m20258P` → `VideoFocusRequest`).

**What it provides.** Unambiguous proto identification for protos that
cannot be verified by enum-fingerprint matching alone. Existing Gold
sidecars use these types; Phase 9 retains both `deep_trace` and
`apk_deep_trace` in the schema's evidence type enum for backward
compatibility.

**Usage going forward.** New Gold-tier work should use `apk_static` with a
method tag like `handler_trace` or `deep_trace`. The two dedicated evidence
types are kept in the enum to avoid a mass rewrite of 32 existing Gold
sidecars.

### `platinum_evidence` (new in Phase 9)

**Source.** OEM wire capture (e.g., the VW MIB3 OI capture at
`captures/oem-vw-mib3oi-2026-04-06/`).

**What it provides.** Production-verified confirmation that a proto is
actually exchanged between a phone and an OEM head unit in the field. Each
`platinum_evidence` entry carries 10 scope fields: `capture_path`,
`vehicle_metadata`, `msg_seq`, `ts_ms`, `message_completeness`,
`attribution_method`, `oem_scope`, `applicability`, an optional `fields`
list, and `match_rules` (closed enum of `MATCH-*` IDs). See
[03-verification-procedures.md](03-verification-procedures.md) for the
platinum_evidence authoring procedure.

**Uses.** Platinum promotion. Cannot appear on sidecars below Gold — the
schema enforces the ladder.

### `oem_capture` (deprecated, still in the enum)

**Source.** The pre-Phase-9 name for OEM wire capture evidence. Phase 9
does NOT remove this enum value to avoid cascading changes, but new
OEM-derived evidence should use `platinum_evidence` (with its 10 scope
fields) rather than the bare `oem_capture` type. A later cleanup phase may
remove `oem_capture` from the enum.

---

## Promotion Logic

Tier assignment is mostly deterministic. Given a set of evidence entries for
a claim, the tier is computed as follows:

```text
if any evidence.type == "platinum_evidence" AND confidence_was_gold:
    tier = platinum                # Phase 10 responsibility
elif has_deep_trace AND has_cross_version:
    tier = gold
elif count(distinct evidence.type values) >= 2:
    tier = silver
elif count(evidence) >= 1:
    tier = bronze
else:
    tier = unverified
```

**Platinum promotion is NOT automatic** — Phase 10's walker explicitly checks
that the proto is already Gold before adding a `platinum_evidence` entry. A
Silver proto that matches in the OEM capture receives
`oem_match_pending_gold: true` instead.

### Combinations Table

| Evidence Combination | Tier |
|----------------------|------|
| *(none)* | Unverified |
| `apk_static` alone | Bronze |
| `apk_static` + `cross_version` | Silver |
| `apk_static` + `cross_version` + `deep_trace` | Gold |
| Gold sidecar + `platinum_evidence` (with `platinum_scope: single_oem`) | Platinum / single-OEM |
| Previously promoted sidecar, now invalidated | Retracted |

---

## For Head Unit Developers

- **Platinum / single-OEM** — Verified on ONE OEM. Safe to depend on for a
  head unit targeting that specific OEM's usage patterns. Treat as "strong
  evidence this is how AA works on OEM X" but not yet "strong evidence this
  is how AA works on all OEMs." Check for MOEM-01 (multi-OEM corroboration)
  in a future milestone before assuming universality.
- **Platinum / multi-OEM** — Verified across multiple OEMs. Stronger than
  single-OEM by virtue of independent corroboration. v2+ state.
- **Gold** — Verified via deep-trace APK analysis + cross-version
  consistency. Very high confidence at the proto-definition level, but NOT
  yet confirmed against any real wire capture. Edge cases may exist on the
  wire that a capture would reveal.
- **Silver** — Two distinct static evidence types agree. High confidence
  from independent analyses; production behavior still untested.
- **Bronze** — Directionally correct, use as a starting point but verify
  independently before shipping.
- **Unverified** — Known to exist but not yet examined. Do your own
  verification first.
- **Retracted** — Do not use. The sidecar records WHAT was wrong and is
  kept as documentation of the re-examination.

When in doubt, check the evidence entries for the specific claim. Every
verified field links back to its evidence trail (see
[02-audit-trail-format.md](02-audit-trail-format.md)).
