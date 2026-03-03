# Requirements: Open Android Auto Protocol Reference

**Defined:** 2026-03-02
**Core Value:** Every published proto definition and protocol claim carries explicit verification evidence and confidence level

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Verification Framework

- [x] **VERI-01**: Tiered confidence system with defined evidence types (APK static analysis, DHU observation, OEM wire capture, cross-version consistency) and confidence levels (Bronze/Silver/Gold)
- [x] **VERI-02**: Audit trail format recording how each proto field/message was verified, with evidence references and timestamps
- [x] **VERI-03**: Step-by-step verification procedures for each evidence type (APK analysis, DHU testing, OEM capture, cross-version comparison)
- [x] **VERI-04**: Source provenance rules — only APK, DHU, OEM captures, and official Google documentation are valid sources

### Proto Definitions

- [x] **PROTO-01**: Compilable .proto files for verified AA message types
- [x] **PROTO-02**: Field-level confidence annotations on each proto field indicating evidence tier
- [ ] **PROTO-03**: Cross-version mapping tables (obfuscated class names → canonical names across 15.9, 16.1, 16.2)

### Protocol Documentation

- [ ] **DOCS-01**: Connection lifecycle documentation (USB/WiFi setup → version negotiation → channel open → session teardown)
- [ ] **DOCS-02**: Media/audio channel documentation (audio focus, ducking, playback control, MediaBrowserService interaction)
- [ ] **DOCS-03**: Navigation channel documentation (turn events, cluster data, maneuver types, step distance/time)
- [ ] **DOCS-04**: Phone/dialer channel documentation (call state, DTMF, contact sync)

### Tooling

- [x] **TOOL-01**: Seed import pipeline to migrate existing ~236 proto class mappings into the audit trail as unverified entries
- [x] **TOOL-02**: Cross-version consistency checker for automated proto structure comparison across APK versions

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Channel Documentation

- **CHAN-01**: Channel architecture reference (multiplexing, service IDs, capability negotiation)
- **CHAN-02**: Sensor channel documentation (26 types, message formats, delivery patterns)
- **CHAN-03**: Radio channel documentation (Service 15, 10 message types)
- **CHAN-04**: Car Control channel documentation (Service 19, HVAC, doors, mirrors)

### Tooling

- **TOOL-03**: OEM wire capture workflow and tooling
- **TOOL-04**: Audit report generator (coverage dashboard from audit trail)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Documentation website / web frontend | Git repo with markdown is sufficient; adds maintenance burden |
| Third-party RE sources | Clean-room integrity — only APK, DHU, OEM captures, official Google docs |
| AA app development guidance | This is car-side (head unit) focused, not phone-app focused |
| DHU setup tutorials | DHU is a verification tool, not the subject matter |
| Transport layer reimplementation | Document the protocol, don't rebuild it here |
| AA proxy/bridge tools | Separate project concern (e.g., aa-proxy-rs) |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| VERI-01 | Phase 1 | Complete |
| VERI-02 | Phase 1 | Complete |
| VERI-03 | Phase 1 | Complete |
| VERI-04 | Phase 1 | Complete |
| PROTO-01 | Phase 2 | Complete |
| PROTO-02 | Phase 2 | Complete |
| PROTO-03 | Phase 3 | Pending |
| DOCS-01 | Phase 4 | Pending |
| DOCS-02 | Phase 5 | Pending |
| DOCS-03 | Phase 5 | Pending |
| DOCS-04 | Phase 5 | Pending |
| TOOL-01 | Phase 2 | Complete |
| TOOL-02 | Phase 3 | Complete |

**Coverage:**
- v1 requirements: 13 total
- Mapped to phases: 13
- Unmapped: 0

---
*Requirements defined: 2026-03-02*
*Last updated: 2026-03-02 after roadmap creation*
