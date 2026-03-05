# Open Android Auto Protocol Reference

## What This Is

A proto-first, systematically verified public reference for the Android Auto protocol — the definitive resource for anyone building head units, proxies, or tools that communicate with the official Android Auto APK. Compilable .proto definitions are the primary artifact, backed by tiered verification evidence (Bronze/Silver/Gold) and companion documentation covering connection lifecycle, audio/media, navigation, and phone channels.

## Core Value

Every published proto definition and protocol claim carries explicit verification evidence and confidence level — this is what distinguishes this from scattered reverse-engineering notes.

## Requirements

### Validated

- ✓ Verification methodology with defined evidence types and tiered confidence levels — v1.0
- ✓ Audit trail system tracking how each proto field/message was verified — v1.0
- ✓ Compilable .proto files for verified AA message types — v1.0
- ✓ Field-level confidence annotations on each proto field — v1.0
- ✓ Cross-version mapping tables (15.9, 16.1, 16.2) — v1.0
- ✓ Connection lifecycle documentation (USB/WiFi → version negotiation → channel open → session teardown) — v1.0
- ✓ Media/audio channel documentation (audio focus, ducking, playback control) — v1.0
- ✓ Navigation channel documentation (turn events, cluster data, maneuver types) — v1.0
- ✓ Phone/dialer channel documentation (call state, evidence gaps documented) — v1.0
- ✓ Import pipeline for existing ~236 proto class mappings as unverified seeds — v1.0
- ✓ Cross-version consistency checker for automated proto comparison — v1.0
- ✓ Step-by-step verification procedures for each evidence type — v1.0
- ✓ Source provenance rules (APK, DHU, OEM captures, official Google docs only) — v1.0

### Active

- [ ] Channel architecture reference (multiplexing, service IDs, capability negotiation)
- [ ] Sensor channel documentation (26 types, message formats, delivery patterns)
- [ ] Radio channel documentation (Service 15, 10 message types)
- [ ] Car Control channel documentation (Service 19, HVAC, doors, mirrors)
- [ ] OEM wire capture workflow and tooling
- [ ] Audit report generator (coverage dashboard from audit trail)

### Out of Scope

- Documentation site / web frontend — Git repo with markdown is sufficient for now
- Third-party RE sources — clean-room integrity requires only APK, DHU, OEM captures, official Google docs
- Custom AA app development guidance — this is car-side (head unit) focused
- DHU setup tutorials — DHU is a verification tool, not the subject matter
- Reimplementation of AA transport layer — document it, don't build it here
- AA proxy/bridge tools — separate project concern (e.g., aa-proxy-rs)

## Context

Shipped v1.0 with ~20K LOC proto files (223 files, 156 audit sidecars) and ~15K LOC documentation.
Tech stack: protobuf, Python (analysis tools), YAML (audit sidecars), JSON Schema (validation).
143 of 220 eligible sidecars promoted to Silver tier via cross-version validation.
8 tech debt items carried forward — mostly empty SUMMARY frontmatter and honestly documented evidence gaps (DTMF, contact sync, some Unverified protos).

### Verification Environment

- **APK versions available**: 15.9, 16.1, 16.2 (decompiled, indexed)
- **DHU**: 2.1 on MINIMEES, phone via USB AOA, logcat via wireless ADB
- **OEM captures**: Hardware available, systematic capture workflow needed
- **Phone**: Samsung S24 Ultra, Android 16 (SDK 36)
- **aa-logcat tool**: Exists but logcat capture broken on Android 13+ (Shizuku fix needed)

## Constraints

- **Evidence-based only**: Nothing published without at least one verification method documented
- **Proto-first**: .proto files are the canonical source of truth; docs derive from and reference them
- **Incremental**: Start with highest-confidence findings, expand coverage over time
- **Clean-room friendly**: Documentation must be usable by clean-room implementations (like openauto-prodigy) without legal risk

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Tiered confidence (not binary) | Allows publishing useful-but-not-gold-standard findings while being transparent about evidence level | ✓ Good — enables incremental publishing |
| Proto-first output | Compilable .proto files are unambiguous and machine-consumable; markdown wraps them with semantics | ✓ Good — proto compilation catches errors |
| All existing work enters as unverified | Prevents false confidence from pre-methodology findings; everything must earn its confidence tier | ✓ Good — 143 seeds earned Silver via cross-version |
| OEM wire captures = gold standard | Production head units show real protocol behavior, not test harness behavior | — Pending (no OEM captures done yet) |
| Monorepo with tools/ subdirectory | Keeps verification tooling close to the data it produces, single repo to manage | ✓ Good |
| YAML sidecar audit convention | Co-locates evidence with proto files; machine-readable for tooling | ✓ Good — 156 sidecars serving tooling |
| DHU observations excluded from Gold tier | Test harness may diverge from production behavior | ✓ Good — honest about evidence quality |
| Enum values not individually annotated | Only enum declarations get confidence comments; reduces noise | ✓ Good |
| Cross-version as independent evidence type | Structural consistency across versions is evidence distinct from single-version static analysis | ✓ Good — enabled Silver promotion |
| Evidence gaps documented transparently | DTMF, contact sync, some sub-messages documented as protocol boundary gaps, not failures | ✓ Good — honest documentation |

---
*Last updated: 2026-03-04 after v1.0 milestone*
