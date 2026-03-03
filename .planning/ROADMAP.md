# Roadmap: Open Android Auto Protocol Reference

## Overview

This project transforms ~236 existing proto class mappings and scattered reverse-engineering notes into a systematically verified, compilable protocol reference. The work flows naturally: establish the verification methodology first, then import and verify existing findings against it, build cross-version confidence, and finally produce channel-specific protocol documentation that any head unit implementer can trust.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Verification Framework** - Establish the methodology, evidence types, confidence tiers, and audit trail that all subsequent work depends on
- [ ] **Phase 2: Seed Import & Proto Foundation** - Migrate existing mappings into the audit system and produce the first compilable, annotated .proto files
- [ ] **Phase 3: Cross-Version Validation** - Build cross-version mapping tables and automated consistency checking across 15.9, 16.1, 16.2
- [ ] **Phase 4: Connection Lifecycle** - Document the full connection lifecycle from USB/WiFi setup through session teardown
- [ ] **Phase 5: Feature Channel Documentation** - Document media, navigation, and phone/dialer channels with verified proto references

## Phase Details

### Phase 1: Verification Framework
**Goal**: Anyone can understand how evidence is gathered, how confidence is assigned, and how findings are audited
**Depends on**: Nothing (first phase)
**Requirements**: VERI-01, VERI-02, VERI-03, VERI-04
**Success Criteria** (what must be TRUE):
  1. A reader can look up any proto field and see what evidence type(s) support it and at what confidence level
  2. The audit trail format is documented with a worked example showing a field progressing from unverified to Bronze to Silver
  3. Step-by-step verification procedures exist for each evidence type (APK analysis, DHU testing, OEM capture, cross-version comparison)
  4. Source provenance rules are published and unambiguous -- a contributor knows exactly which sources are valid
**Plans:** 2 plans

Plans:
- [x] 01-01-PLAN.md — Confidence tiers, evidence types, and source provenance rules
- [ ] 01-02-PLAN.md — Audit trail format with JSON Schema and verification procedures

### Phase 2: Seed Import & Proto Foundation
**Goal**: Existing reverse-engineering work is captured in the audit system and the first compilable .proto files exist with field-level confidence annotations
**Depends on**: Phase 1
**Requirements**: TOOL-01, PROTO-01, PROTO-02
**Success Criteria** (what must be TRUE):
  1. All ~236 existing proto class mappings are imported as unverified entries in the audit trail
  2. At least one channel's .proto files compile successfully with protoc
  3. Every proto field in published .proto files carries a confidence annotation referencing the verification framework
  4. A new contributor can clone the repo, run protoc, and get zero errors on published .proto files
**Plans**: TBD

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD

### Phase 3: Cross-Version Validation
**Goal**: Proto definitions are validated across APK versions with automated tooling, and obfuscated-to-canonical name mappings exist for all three available versions
**Depends on**: Phase 2
**Requirements**: PROTO-03, TOOL-02
**Success Criteria** (what must be TRUE):
  1. Cross-version mapping tables exist showing obfuscated class names to canonical names for 15.9, 16.1, and 16.2
  2. An automated checker can compare proto structures across versions and flag additions, removals, or type changes
  3. Running the consistency checker against the published .proto files produces a report with zero unexplained discrepancies
**Plans**: TBD

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD

### Phase 4: Connection Lifecycle
**Goal**: A head unit implementer can read the connection lifecycle documentation and understand every step from physical connection to session teardown
**Depends on**: Phase 2
**Requirements**: DOCS-01
**Success Criteria** (what must be TRUE):
  1. Documentation covers the full sequence: USB/WiFi setup, version negotiation, channel opening, and session teardown
  2. Each protocol step references specific proto messages from the compiled .proto files
  3. A head unit developer reading only this document could implement the connection handshake
**Plans**: TBD

Plans:
- [ ] 04-01: TBD

### Phase 5: Feature Channel Documentation
**Goal**: Media, navigation, and phone channels are documented with verified proto references so implementers can build feature-complete head units
**Depends on**: Phase 4
**Requirements**: DOCS-02, DOCS-03, DOCS-04
**Success Criteria** (what must be TRUE):
  1. Media channel docs cover audio focus, ducking, playback control, and MediaBrowserService interaction with proto message references
  2. Navigation channel docs cover turn events, cluster data, maneuver types, and step distance/time with proto message references
  3. Phone channel docs cover call state, DTMF, and contact sync with proto message references
  4. Each documented message type references its confidence tier from the verification framework
**Plans**: TBD

Plans:
- [ ] 05-01: TBD
- [ ] 05-02: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5
Note: Phases 3 and 4 both depend on Phase 2 and could theoretically run in parallel.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Verification Framework | 1/2 | In progress | - |
| 2. Seed Import & Proto Foundation | 0/? | Not started | - |
| 3. Cross-Version Validation | 0/? | Not started | - |
| 4. Connection Lifecycle | 0/? | Not started | - |
| 5. Feature Channel Documentation | 0/? | Not started | - |
