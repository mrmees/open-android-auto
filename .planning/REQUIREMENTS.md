# Requirements: Open Android Auto Protocol Reference

**Defined:** 2026-04-07
**Milestone:** v1.5 OEM Evidence & Gold-Tier Promotion
**Core Value:** Every published proto definition and protocol claim carries explicit verification evidence and confidence level

## v1.5 Requirements

Requirements for milestone v1.5. Each maps to a roadmap phase. Structural choices reflect review feedback from a Codex critique pass (2026-04-07) that sharpened the single-OEM trap, fragment-classification requirement, and coverage-scoping discipline.

### OEM — VW MIB3 OI Capture Analysis

- [x] **OEM-01**: VW capture is parsed into per-msg-type/per-direction tables with explicit fragment classification (`standalone`, `probable_first`, `continuation_or_garbage`, `reassembled`, `unattributed`). Naïve readers must not be able to mistake continuation fragments for standalone messages. — completed 2026-04-07 by 07-01 (`analysis/tools/oem_vw_parser/` + `analysis/reports/oem-vw/msg-type-classification.{md,json}`)
- [x] **OEM-02**: Real production values from VW SDP are documented — HeadUnitInfo/CarInfo identity fields **and** observed service descriptors, channel capabilities, and SDP-level configuration drawn from `sdp_request.bin` / `sdp_response.bin`.
- [x] **OEM-03**: Capture coverage manifest records which services/channels/features the 60s session actually exercised, including what was *not* observed. Provides the baseline against which TIER-04 coverage claims are scoped.
- [x] **OEM-04**: Divergence report compares VW SDP against DHU baselines with explicit version-alignment notes. VW is on AA 16.4; DHU baselines span older APKs — reported differences must distinguish version-related from OEM-related changes.
- [x] **OEM-05**: Candidate OEM-only msg_types (seen in VW but not in DHU baselines) are documented, filtered for fragment artifacts per OEM-01 classification, and labeled `candidate` until repeat observation or successful parse confirms them as real.

### XVER — 16.4 Cross-Version Validation

- [x] **XVER-01**: Cross-version consistency checker runs successfully against 15.9/16.1/16.2/16.4.
- [x] **XVER-02**: 16.4-specific protocol deltas (new/removed msg types, schema changes) are documented in the proto reference with sidecar evidence entries.
- [x] **XVER-03**: Audit sidecars are updated to include 16.4 evidence where applicable.
- [x] **XVER-04**: Bronze protos holding across 4 versions are promoted to Silver.
- [x] **XVER-05**: Reproducibility-gap documentation for the 5 manual-JADX salvaged classes (`rcn`, `rco`, `rcp`, `rdt`, `red` in `analysis/aa_apk_16.4.661034_apkm/manual-jadx/`) — explicit statement of what CAN'T be concluded because bulk JADX stubbed them and exact JADX argv for the recovered copies is unknown.

### TIER — OEM Evidence Schema & Gold Promotion

- [ ] **TIER-01**: Audit sidecar JSON Schema adds a `platinum_evidence` evidence type with scope fields: capture provenance (path, vehicle metadata, msg seq, ts_ms), message completeness (first-only / full / reassembled), service attribution method, OEM scope (single / multi), and field-level vs message-level applicability.
- [ ] **TIER-02**: Gold tier is split into a visible scope dimension — `Gold / single-OEM` and (future) `Gold / multi-OEM` — reflected in sidecar metadata and all rendered confidence badges, not just buried in prose. Methodology doc explains the dimension and the single-OEM trap.
- [ ] **TIER-03**: OEM match policy is defined in the methodology doc — explicit rules for what counts as a match for promotion (msg-level presence vs field-level confirmation vs enum value match vs repeat observation) and what does NOT count. TIER-04 promotions cite the specific rule that applied.
- [ ] **TIER-04**: Every Silver-tier proto **in services/channels observed by the VW capture** (per OEM-03 manifest) has been checked against the capture and marked promoted, retracted, or explicitly unmatched. Protos in services the VW session never exercised get no claim either way — they remain Silver.
- [ ] **TIER-05**: Non-claim boundary for OEM capture is documented centrally — the VW capture cannot validate outer frame header semantics, `channel_id`, or `flags` behavior (the on-phone hook lives inside the AA framing layer), and must not be cited as evidence for claims about those surfaces.

### ARCH — Channel Architecture Reference

- [ ] **ARCH-01**: Channel architecture doc exists and explains AA multiplexing, frame layout, channel IDs, fragmentation, direction semantics, and how existing per-channel docs fit into the larger model. Cross-linking from per-channel docs and main README is acceptance criteria.
- [ ] **ARCH-02**: Doc explains channel→service binding via SDP descriptors and service ID assignment rules.
- [ ] **ARCH-03**: Doc explains capability negotiation flow scoped to concrete examples from captures (version exchange, AVChannel field 9 ColorSchemeSupport, codec/resolution negotiation). Not an exhaustive capability survey — scoped to what's evidenced.
- [ ] **ARCH-04**: Doc includes concrete VW vs DHU comparison examples drawn from actual captures.

### REPORT — Audit Report Generator

- [ ] **REPORT-01**: Coverage dashboard tool reads audit sidecars and outputs Bronze/Silver/Gold counts per channel, evidence type breakdown per tier (static analysis / cross-version / DHU observation / OEM evidence), and a missing-sidecar list. Acknowledged as lower priority than OEM/XVER/TIER work — scope for a single compact feature, not a full reporting suite.

### HIST — Historical Bookkeeping

- [x] **HIST-01**: MILESTONES.md contains v1.1–v1.4 retroactive entries for post-v1.0 patch work (channel verification completion, SDP layer verification waves 1–9, validator decode-rate overhaul, nav image evidence cross-version matrix). Acknowledged bookkeeping, kept in-scope per user direction.

## v2 Requirements (Deferred)

Deferred to a future milestone. Tracked but not in the v1.5 roadmap.

### Multi-OEM Corroboration

- **MOEM-01**: Second OEM capture acquired from different manufacturer (non-VW)
- **MOEM-02**: Protos with `Gold / single-OEM` evidence are re-examined with second OEM — promoted to `Gold / multi-OEM` where confirmed, flagged as OEM-divergent where not
- **MOEM-03**: OEM divergence matrix documenting manufacturer-specific quirks

### Capture Pipeline Enhancements

- **CAP-01**: `channel_id` reconstruction in on-phone capture format (if media-stream analysis becomes a goal)
- **CAP-02**: Media-stream analysis (audio/video frame parsing, codec negotiation validation)
- **CAP-03**: Shizuku integration for aa-logcat tool (Android 13+ persistent logcat access)

## Out of Scope

Explicitly excluded for v1.5. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Multi-OEM corroboration | Only one OEM capture exists; moved to v2 |
| aa-capture-app development | Separate Android dev project (`/mnt/e/claude/personal/android-auto-dhu/`), not protocol-reference work |
| channel_id reconstruction in on-phone capture format | Limited cost for v1.5 verification goals; deferred to v2 CAP-01 |
| Media-stream analysis | Not protocol-reference focus; v1.0 already documented codec negotiation at the config level |
| Shizuku fix for aa-logcat | Sister repo concern; v2 CAP-03 |
| New OEM capture acquisition | We have one to analyze; getting more is its own effort |
| Second channel-doc pass | All 13 channel docs already exist from v1.x patch work |
| Protocol transport layer reimplementation | Out of project scope per PROJECT.md — this reference documents, it does not implement |

## Traceability

Which phases cover which requirements. Populated during roadmap creation by the gsd-roadmapper.

| Requirement | Phase | Status |
|-------------|-------|--------|
| HIST-01 | Phase 6 — Historical Bookkeeping | Complete |
| OEM-01 | Phase 7 — VW Capture Analysis | Complete |
| OEM-02 | Phase 7 — VW Capture Analysis | Complete |
| OEM-03 | Phase 7 — VW Capture Analysis | Complete |
| OEM-05 | Phase 7 — VW Capture Analysis | Complete |
| XVER-01 | Phase 8 — 16.4 Cross-Version Validation | Complete |
| XVER-02 | Phase 8 — 16.4 Cross-Version Validation | Complete |
| XVER-03 | Phase 8 — 16.4 Cross-Version Validation | Complete |
| XVER-04 | Phase 8 — 16.4 Cross-Version Validation | Complete |
| XVER-05 | Phase 8 — 16.4 Cross-Version Validation | Complete |
| TIER-01 | Phase 9 — OEM Methodology & Divergence Report | Pending |
| TIER-02 | Phase 9 — OEM Methodology & Divergence Report | Pending |
| TIER-03 | Phase 9 — OEM Methodology & Divergence Report | Pending |
| TIER-05 | Phase 9 — OEM Methodology & Divergence Report | Pending |
| OEM-04 | Phase 9 — OEM Methodology & Divergence Report | Complete |
| TIER-04 | Phase 10 — Gold-Tier Promotion Walk | Pending |
| ARCH-01 | Phase 11 — Channel Architecture Reference | Pending |
| ARCH-02 | Phase 11 — Channel Architecture Reference | Pending |
| ARCH-03 | Phase 11 — Channel Architecture Reference | Pending |
| ARCH-04 | Phase 11 — Channel Architecture Reference | Pending |
| REPORT-01 | Phase 12 — Audit Report Generator | Pending |

**Coverage:**
- v1.5 requirements: 21 total
- Mapped to phases: 21 (100%)
- Unmapped: 0

---
*Requirements defined: 2026-04-07 for milestone v1.5*
*Last updated: 2026-04-07 after v1.5 roadmap creation (7 phases, 12 plans)*
