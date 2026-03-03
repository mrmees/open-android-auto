# 01 — Confidence Tiers

## Quick Reference

| Tier | Evidence Required | Meaning |
|------|-------------------|---------|
| **Gold** | OEM wire capture | Production-confirmed behavior |
| **Silver** | 2+ distinct evidence types | Corroborated from independent sources |
| **Bronze** | Any single piece of evidence | Supported by one source; directionally correct |
| **Unverified** | None yet | Known to exist but not yet confirmed |

See [04-source-provenance.md](04-source-provenance.md) for which sources are valid.

---

## Confidence Tiers

### Gold

Production-confirmed protocol behavior. A claim reaches Gold when it has been observed in an OEM wire capture from a production Android Auto head unit.

OEM capture alone is sufficient for Gold — it does not need to pass through Bronze or Silver first. This is the only tier that requires a specific evidence type.

DHU observations do NOT qualify for Gold. The Desktop Head Unit is Google's test harness, not a production environment. Its behavior may differ from production OEM implementations.

### Silver

Corroborated claim with independent evidence. A claim reaches Silver when it is supported by **two or more distinct evidence types**.

The key word is *types*. Two entries of the same evidence type do not constitute independent corroboration:

- `apk_static` + `apk_static` (different methods) = still one type = **Bronze**
- `apk_static` + `dhu_observation` = two types = **Silver**

Silver represents high confidence. The claim has been verified through independent methodologies that arrived at the same conclusion.

### Bronze

Single-source evidence. A claim reaches Bronze when it has **any single piece of evidence** from a valid source. One `apk_static` entry, one `dhu_observation`, one `cross_version` match — any of these moves the claim out of Unverified.

Bronze means the claim is directionally correct but has not yet been independently corroborated. It should be treated as a working assumption rather than established fact.

### Unverified

No evidence yet. All Phase 2 seed imports enter the system at this tier. Unverified is a valid state — it indicates a proto field or message type is known to exist (e.g., referenced in decompiled code) but no structured verification evidence has been recorded.

Unverified does not mean "wrong." It means "not yet examined."

---

## Evidence Types

Four evidence types are defined. Each represents a distinct methodology for gathering protocol evidence.

### `apk_static`

**Source:** Static analysis of decompiled Android Auto APKs (currently 15.9, 16.1, 16.2).

**What it provides:** Proto structure, field names, enum values, string constants, call graphs, type relationships.

**Method tags:** Each `apk_static` entry includes a method tag describing the specific analysis technique. Suggested values include:

- `bfs_trace` — Breadth-first search through class references
- `enum_match` — Enum value fingerprint matching across versions
- `string_const` — String constant extraction
- `proto_access` — Proto field access pattern analysis
- `call_graph` — Call graph / call edge analysis
- `switch_map` — Switch map analysis for enum dispatch

Method tags are **open vocabulary** — contributors may define new ones as analysis techniques evolve. However, regardless of method tag, all `apk_static` entries count as **one evidence type** for promotion purposes.

### `dhu_observation`

**Source:** Runtime observation from Google's Desktop Head Unit test harness (DHU 2.1).

**What it provides:** Message flow, sensor processing pipelines, runtime behavior, channel lifecycle.

**Limitations:** The DHU is a test environment. Its behavior may diverge from production OEM head units. For this reason, `dhu_observation` is valid for Bronze and Silver but **never sufficient for Gold**.

### `oem_capture`

**Source:** Wire capture from a production OEM Android Auto head unit.

**What it provides:** Actual production protocol behavior — the ground truth for what happens on the wire between a phone and a real head unit.

**Special status:** This is the only evidence type that can directly promote a claim to Gold. A single `oem_capture` entry is sufficient.

### `cross_version`

**Source:** Same proto structure confirmed across multiple APK versions (e.g., 15.9, 16.1, 16.2).

**What it provides:** Structural stability evidence. A field or message type that persists unchanged across versions is more likely to be part of the stable protocol surface.

**Independence:** `cross_version` counts as a **separate type** from `apk_static`. Even though both derive from APK analysis, cross-version stability is a distinct signal from any single-version static analysis finding.

---

## Promotion Logic

Tier assignment is deterministic. Given a set of evidence entries for a claim, the tier is computed as follows:

```
if any evidence.type == "oem_capture":
    tier = Gold
elif count(distinct evidence.type values) >= 2:
    tier = Silver
elif count(evidence) >= 1:
    tier = Bronze
else:
    tier = Unverified
```

Evaluation order matters: Gold check runs first (OEM capture overrides everything), then Silver, then Bronze.

### Combinations Table

| Evidence Combination | Distinct Types | Tier |
|----------------------|:-:|------|
| *(none)* | 0 | Unverified |
| `apk_static` | 1 | Bronze |
| `dhu_observation` | 1 | Bronze |
| `cross_version` | 1 | Bronze |
| `apk_static` + `apk_static` (different methods) | 1 | Bronze |
| `apk_static` + `dhu_observation` | 2 | Silver |
| `apk_static` + `cross_version` | 2 | Silver |
| `dhu_observation` + `cross_version` | 2 | Silver |
| `apk_static` + `dhu_observation` + `cross_version` | 3 | Silver |
| `oem_capture` | 1 | Gold |
| `oem_capture` + `apk_static` | 2 | Gold |
| `oem_capture` + `apk_static` + `dhu_observation` | 3 | Gold |

Note: Three distinct non-OEM evidence types still result in Silver. Gold requires OEM capture specifically — there is no "quantity beats quality" path.

---

## For Head Unit Developers

If you are building a head unit implementation and consuming this protocol reference:

- **Gold** — Safe to depend on. This behavior has been confirmed on production hardware. Build your implementation around it.
- **Silver** — High confidence. Multiple independent sources agree. Very unlikely to be wrong, but edge cases may exist that production captures would reveal.
- **Bronze** — Directionally correct. Use as a starting point but verify independently before shipping. The claim has support but has not been corroborated.
- **Unverified** — Known to exist but not yet examined. Do not build on these without doing your own verification first. The field or message type was found in decompiled code but no structured evidence has been recorded.

When in doubt, check the evidence entries for the specific claim. Every verified field links back to its evidence trail (see [02-audit-trail-format.md](02-audit-trail-format.md) when available).
