# Open Android Auto Protocol Reference

## What This Is

A proto-first, systematically verified public reference for the Android Auto protocol — the definitive resource for anyone building head units, proxies, or tools that communicate with the official Android Auto APK. Compilable .proto definitions are the primary artifact, backed by tiered verification evidence and companion documentation covering connection lifecycle, feature negotiation, audio handling, and real-world interaction patterns.

## Core Value

Every published proto definition and protocol claim carries explicit verification evidence and confidence level — this is what distinguishes this from scattered reverse-engineering notes.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Verification methodology with defined evidence types and tiered confidence levels
- [ ] Audit trail system tracking how each proto field/message was verified
- [ ] Compilable .proto files for verified AA message types
- [ ] Connection lifecycle documentation (version negotiation through teardown)
- [ ] Channel architecture reference (multiplexing, service discovery, capability negotiation)
- [ ] Sensor channel documentation (types, message formats, delivery patterns)
- [ ] Media channel documentation (audio focus, ducking, playback control)
- [ ] Navigation channel documentation (turn events, cluster data, maneuver types)
- [ ] Head-unit-focused interaction guides (practical "how to implement X" recipes)
- [ ] Import pipeline for existing ~236 proto class mappings as unverified seeds
- [ ] Verification tooling (capture parsers, audit scripts) in tools/ subdirectory
- [ ] Cross-version consistency checks (15.9, 16.1, 16.2 APK comparison)
- [ ] OEM wire capture workflow and tooling

### Out of Scope

- Documentation site / web frontend — Git repo with markdown is sufficient for now
- Custom AA app development guidance — this is car-side (head unit) focused
- DHU setup tutorials — DHU is a verification tool, not the subject matter
- Reimplementation of AA transport layer — document it, don't build it here

## Context

### Existing Work (Seed Corpus)

Significant reverse-engineering has already been done in this repo and adjacent projects:

- **236 proto class mappings** across 16.1 and 16.2 APKs via multi-signal triage (BFS, hub-file, package, structural)
- **Sensor channel**: 26 types identified (IDs 1-26), messages 0x8001-0x8004, night mode pipeline fully traced
- **Radio channel** (Service 15): 10 message types with proto schemas documented
- **Car Control channel** (Service 19): 7 message types covering HVAC, doors, mirrors
- **DHU 2.1 observations**: Cluster nav data, media metadata, touchpad behavior, multi-display layering
- **APK analysis tooling**: SQLite index DB (90MB for 16.2), jadx decompilation, proto class triage tool

All of this enters the new system as **unverified seeds** to be run through the verification methodology.

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
| Tiered confidence (not binary) | Allows publishing useful-but-not-gold-standard findings while being transparent about evidence level | — Pending |
| Proto-first output | Compilable .proto files are unambiguous and machine-consumable; markdown wraps them with semantics | — Pending |
| All existing work enters as unverified | Prevents false confidence from pre-methodology findings; everything must earn its confidence tier | — Pending |
| OEM wire captures = gold standard | Production head units show real protocol behavior, not test harness behavior | — Pending |
| Monorepo with tools/ subdirectory | Keeps verification tooling close to the data it produces, single repo to manage | — Pending |

---
*Last updated: 2026-03-02 after initialization*
