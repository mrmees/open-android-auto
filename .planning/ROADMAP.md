# Roadmap: Open Android Auto Protocol Reference

## Overview

v1.0 shipped the verification framework, seed import, cross-version tooling (15.9/16.1/16.2), connection lifecycle docs, and feature channel docs. v1.x patch work (retroactively logged as v1.1–v1.4) completed all 14 GAL channel verifications (196 Gold), SDP layer verification across 9 waves (112 Gold SDP), and pushed the validator decode rate to 100%.

**v1.5's single most important outcome:** the VW MIB3 OI 2024 capture — the project's first OEM evidence source — moves a meaningful number of Silver protos to `Gold / single-OEM` status, rigorously scoped to the services the capture actually exercised, with no overclaim. Everything else in this milestone supports or runs alongside that goal.

The shape of the work flows naturally from that: retire the v1.x bookkeeping debt, analyze the VW capture on its own terms, fold APK 16.4 into the cross-version matrix so the Silver pool is as large as possible before promotion, land the schema/tier/policy/boundary groundwork that makes promotion honest, then walk every eligible Silver proto against the capture. A channel architecture reference and an audit report generator ride alongside once the Gold counts are nonzero.

## Milestones

- ✅ **v1.0 Protocol Reference MVP** — Phases 1-5 (shipped 2026-03-04) — [archive](milestones/v1.0-ROADMAP.md)
- ⏳ **v1.5 OEM Evidence & Gold-Tier Promotion** — Phases 6-12 (in progress)

## Phase Numbering

- Integer phases (6, 7, 8, …): Planned v1.5 milestone work
- Decimal phases (e.g., 7.1): Reserved for urgent insertions discovered mid-milestone

Phase numbering continues from v1.0 (which shipped Phases 1-5). Decimal phases appear between their surrounding integers in numeric order.

## Phases

<details>
<summary>✅ v1.0 Protocol Reference MVP (Phases 1-5) — SHIPPED 2026-03-04</summary>

- [x] Phase 1: Verification Framework (2/2 plans) — completed 2026-03-03
- [x] Phase 2: Seed Import & Proto Foundation (2/2 plans) — completed 2026-03-03
- [x] Phase 3: Cross-Version Validation (2/2 plans) — completed 2026-03-03
- [x] Phase 4: Connection Lifecycle (2/2 plans) — completed 2026-03-04
- [x] Phase 5: Feature Channel Documentation (2/2 plans) — completed 2026-03-04

</details>

**v1.5 OEM Evidence & Gold-Tier Promotion:**

- [x] **Phase 6: Historical Bookkeeping** — Retroactively log v1.1–v1.4 patch work in MILESTONES.md so the ledger reflects reality before the milestone proper begins (completed 2026-04-07)
- [x] **Phase 7: VW Capture Analysis** (2/2 plans complete) — Parse the VW capture into per-msg-type / per-direction tables with fragment classification, extract production SDP values, build the coverage manifest that scopes later promotion work, and flag candidate OEM-only msg_types — completed 2026-04-08
- [x] **Phase 8: 16.4 Cross-Version Validation** — Extend the consistency checker to 4 APK versions, fold 16.4 into sidecars, promote Bronze-across-4 to Silver, and document the manual-JADX reproducibility gap (completed 2026-04-08)
- [ ] **Phase 9: OEM Methodology & Divergence Report** — Extend audit sidecar schema for `oem_evidence`, split Gold into a visible scope dimension, publish the OEM match policy, document the VW capture's non-claim boundary, and produce the VW-vs-DHU divergence report
- [ ] **Phase 10: Gold-Tier Promotion Walk** — Walk every Silver proto in services observed by the VW capture, promote/retract/mark-unmatched per the match policy, and leave unobserved-service Silver protos untouched
- [ ] **Phase 11: Channel Architecture Reference** — Publish the multiplexing/framing/service-binding/capability-negotiation reference doc with concrete VW vs DHU examples drawn from actual captures
- [ ] **Phase 12: Audit Report Generator** — Coverage dashboard tool reading the audit trail, surfacing Bronze/Silver/Gold counts per channel, evidence-type breakdowns, and missing-sidecar lists

## Phase Details

### Phase 6: Historical Bookkeeping
**Goal**: The MILESTONES.md ledger reflects reality — v1.1 through v1.4 patch work is recorded retroactively so v1.5 can be tracked against a truthful baseline
**Depends on**: v1.0 archived
**Requirements**: HIST-01
**Success Criteria** (what must be TRUE):
  1. MILESTONES.md contains a v1.1 entry covering channel verification completion (14 channels, 196 Gold messages) with commit span and date range
  2. MILESTONES.md contains a v1.2 entry covering SDP layer verification (Waves 1-9, 112 Gold SDP protos)
  3. MILESTONES.md contains a v1.3 entry covering validator capture pipeline overhaul (8% → 100% proto decode rate)
  4. MILESTONES.md contains a v1.4 entry covering nav image evidence cross-version matrix and Material You theming discovery
  5. Each retroactive entry follows the same format as the v1.0 entry (phase count, timeline, commits, deliverables, accomplishments, tech debt)
**Plans:** 1/1 plans complete

Plans:
- [x] 06-01-PLAN.md — Retroactive v1.1–v1.4 MILESTONES.md entries

### Phase 7: VW Capture Analysis
**Goal**: The VW MIB3 OI capture is broken down into evidence artifacts that downstream phases can cite — classified per-msg-type tables, production SDP values, a coverage manifest that scopes TIER-04, and a candidate-OEM-only msg_type list filtered through fragment classification
**Depends on**: Phase 6
**Requirements**: OEM-01, OEM-02, OEM-03, OEM-05
**Success Criteria** (what must be TRUE):
  1. Per-msg-type / per-direction table exists with each entry classified as `standalone`, `probable_first`, `continuation_or_garbage`, `reassembled`, or `unattributed` — a naïve reader cannot mistake continuation fragments for real standalone messages
  2. Production values from `sdp_request.bin` / `sdp_response.bin` are extracted and documented: HeadUnitInfo/CarInfo identity fields, observed service descriptors, channel capabilities, and SDP-level configuration
  3. Coverage manifest exists listing which services, channels, and features the 60s VW session actually exercised — and explicitly, which it did NOT — so Phase 10 can scope promotion claims honestly
  4. Candidate OEM-only msg_types list exists (msg_types seen in VW but not in DHU baselines), with every entry filtered through OEM-01 fragment classification and labeled `candidate` until repeat observation or successful parse confirms them
  5. All outputs live under `analysis/reports/oem-vw/` (or equivalent) and are referenced from the main capture README
**Plans:** 2/2 plans complete

Plans:
- [x] 07-01-PLAN.md — VW capture parser, per-msg-type tables, fragment classification (OEM-01) — completed 2026-04-07
- [x] 07-02-PLAN.md — Production SDP values, coverage manifest, candidate OEM-only msg_types (OEM-02, OEM-03, OEM-05) — completed 2026-04-08

### Phase 8: 16.4 Cross-Version Validation
**Goal**: APK 16.4 joins the cross-version consistency matrix as a first-class version, 16.4-specific deltas are documented in sidecars, Bronze-across-4-versions gets promoted to Silver (growing the pool Phase 10 will walk), and the manual-JADX reproducibility gap is stated explicitly so no one overclaims off salvaged classes
**Depends on**: Phase 6 (independent of Phase 7 — different evidence sources; can run in parallel with Phase 7 if desired, but must complete before Phase 10)
**Requirements**: XVER-01, XVER-02, XVER-03, XVER-04, XVER-05
**Success Criteria** (what must be TRUE):
  1. Cross-version consistency checker runs successfully against all four versions (15.9, 16.1, 16.2, 16.4) and produces a clean report with any discrepancies explicitly explained
  2. 16.4-specific protocol deltas (new msg types, removed msg types, schema changes) are documented in the proto reference with matching sidecar evidence entries
  3. Audit sidecars are updated to include 16.4 evidence where the proto holds across the new version
  4. Every Bronze proto that holds structurally across 4 versions has been promoted to Silver in its sidecar
  5. Reproducibility-gap documentation exists for the 5 manual-JADX salvaged classes (`rcn`, `rco`, `rcp`, `rdt`, `red`) — explicit statement of what CANNOT be concluded because bulk JADX stubbed them and the exact JADX argv is unknown
**Plans:** 2/2 plans complete

Plans:
- [x] 08-01-PLAN.md — Consistency checker 16.4 extension, delta report, reproducibility-gap doc (XVER-01, XVER-02, XVER-05) — completed 2026-04-08
- [ ] 08-02-PLAN.md — Sidecar 16.4 evidence updates and Bronze→Silver promotion walk (XVER-03, XVER-04)

### Phase 9: OEM Methodology & Divergence Report
**Goal**: The methodology surface required for honest OEM-evidence promotion exists — sidecar schema knows about `oem_evidence`, the Gold tier has a visible scope dimension rather than a buried caveat, the match policy is published, the VW capture's non-claim boundary is documented, and the VW-vs-DHU divergence report (with version-alignment notes) exists as a first-class artifact
**Depends on**: Phase 7 (needs OEM-01..OEM-03 outputs for divergence scoping), Phase 8 (needs 16.4 context for version-alignment notes)
**Requirements**: TIER-01, TIER-02, TIER-03, TIER-05, OEM-04
**Success Criteria** (what must be TRUE):
  1. Audit sidecar JSON Schema has an `oem_evidence` evidence type with scope fields: capture provenance (path, vehicle metadata, msg seq, ts_ms), message completeness (`first-only` / `full` / `reassembled`), service attribution method, OEM scope (`single` / `multi`), and field-level vs message-level applicability — schema validates, example sidecar passes
  2. Gold tier is split into a visible scope dimension — `Gold / single-OEM` and (future) `Gold / multi-OEM` — reflected in sidecar metadata and all rendered confidence badges, not just buried in prose. Methodology doc explains the dimension and the single-OEM trap by name
  3. OEM match policy is published in the methodology doc with explicit rules for what counts as a match (msg-level presence vs field-level confirmation vs enum value match vs repeat observation) and what does NOT count. Phase 10 promotions will cite these rule IDs
  4. Non-claim boundary for the VW capture is documented centrally — the on-phone hook lives inside the AA framing layer, so the capture cannot validate outer frame header semantics, `channel_id`, or `flags` behavior. Anywhere those surfaces are discussed, the boundary is cross-linked
  5. VW-vs-DHU SDP divergence report exists with version-alignment notes distinguishing 16.4-vs-older-APK differences from OEM-vs-DHU differences
**Plans:** 2 plans

Plans:
- [ ] 09-01-PLAN.md — `oem_evidence` schema, Gold scope dimension, match policy, non-claim boundary (TIER-01, TIER-02, TIER-03, TIER-05)
- [ ] 09-02-PLAN.md — VW-vs-DHU SDP divergence report with version-alignment notes (OEM-04)

### Phase 10: Gold-Tier Promotion Walk
**Goal**: Every Silver-tier proto in services the VW capture observed has been checked against the capture and marked `promoted` / `retracted` / `explicitly unmatched`, using the TIER-03 match policy and scoped by the OEM-03 coverage manifest. Protos in unobserved services stay Silver, untouched. This is the milestone's headline deliverable.
**Depends on**: Phase 7 (coverage manifest, classified tables), Phase 8 (final Silver pool), Phase 9 (schema, policy, scope dimension, non-claim boundary)
**Requirements**: TIER-04
**Success Criteria** (what must be TRUE):
  1. A promotion walk report exists listing every Silver proto in services/channels from the OEM-03 coverage manifest, with an explicit verdict for each: `promoted to Gold / single-OEM`, `retracted`, or `explicitly unmatched` (and why)
  2. Each promotion entry cites the specific TIER-03 match policy rule that applied (msg-level presence, field confirmation, enum match, repeat observation)
  3. Sidecars for every promoted proto have been updated with `oem_evidence` entries per the TIER-01 schema and their confidence badge reflects `Gold / single-OEM` per TIER-02
  4. Silver protos in services the VW session never exercised appear in the report under a clearly-marked "unobserved — no claim either way" section and have NOT had their sidecars modified
  5. A Gold-counts delta exists before/after the walk, broken down by channel, so the milestone's headline outcome is measurable
**Plans:** 2 plans

Plans:
- [ ] 10-01-PLAN.md — Promotion walk execution against observed-services Silver pool (TIER-04 walk)
- [ ] 10-02-PLAN.md — Sidecar updates, Gold-count delta report, unmatched/unobserved reconciliation (TIER-04 wrap)

### Phase 11: Channel Architecture Reference
**Goal**: A reader who has never touched the AA protocol can read one document and understand multiplexing, framing, fragmentation, direction semantics, channel→service binding via SDP, and capability negotiation — illustrated with concrete VW-vs-DHU examples drawn from real captures, not hand-waved theory
**Depends on**: Phase 7 (needs VW capture artifacts for examples), Phase 10 (ARCH-04 examples are richer once Gold counts are nonzero and divergence has been catalogued)
**Requirements**: ARCH-01, ARCH-02, ARCH-03, ARCH-04
**Success Criteria** (what must be TRUE):
  1. Channel architecture doc exists at `docs/channels/architecture.md` (or equivalent) covering AA multiplexing, the `[channel][flags][length][payload]` frame layout, channel ID assignments, fragmentation rules, and direction semantics — with cross-links from every existing per-channel doc and the main README
  2. Doc explains channel→service binding via SDP descriptors and how service IDs are assigned (the 14-channel SDP model from v1.x)
  3. Capability negotiation flow is explained and scoped to concrete evidenced examples (version exchange, AVChannel field 9 `ColorSchemeSupport`, codec/resolution negotiation) — not an exhaustive capability survey
  4. Doc includes concrete VW vs DHU comparison examples pulled from real captures (SDP differences, channel advertisement differences, any observed capability drift)
  5. Every claim in the doc cites either an existing verification report, a sidecar, or a specific capture message by seq/ts — nothing hand-waved
**Plans:** 2 plans

Plans:
- [ ] 11-01-PLAN.md — Core architecture doc: multiplexing, framing, service binding, capability negotiation (ARCH-01, ARCH-02, ARCH-03)
- [ ] 11-02-PLAN.md — VW-vs-DHU comparison examples integration and cross-linking (ARCH-04)

### Phase 12: Audit Report Generator
**Goal**: A single compact tool reads the audit trail and produces a coverage dashboard so the Bronze/Silver/Gold story can be told at a glance — scoped deliberately small, since OEM/XVER/TIER work is higher priority
**Depends on**: Phase 10 (running it before the promotion walk would just show pre-walk Silver counts — the whole point is visualizing the new Gold distribution)
**Requirements**: REPORT-01
**Success Criteria** (what must be TRUE):
  1. Coverage dashboard tool reads all audit sidecars and outputs a per-channel Bronze/Silver/Gold count table (plus `Gold / single-OEM` vs `Gold / multi-OEM` split where applicable)
  2. Tool breaks down evidence types per tier — static analysis, cross-version, DHU observation, OEM evidence — so the reader can see WHAT is driving each tier's population
  3. Tool surfaces a missing-sidecar list (proto files with no corresponding sidecar) so coverage gaps are visible
  4. Tool runs from the CLI with a single command and writes both machine-readable (JSON) and human-readable (Markdown) output
**Plans:** 1 plan

Plans:
- [ ] 12-01-PLAN.md — Coverage dashboard tool (REPORT-01)

## Progress

**Execution Order:**
- v1.0 phases (1-5) are complete and archived
- v1.5 phases execute in numeric order: 6 → 7 → 8 → 9 → 10 → 11 → 12
- Phase 7 and Phase 8 operate on independent evidence sources (VW capture vs APK 16.4) and could run in parallel after Phase 6 if capacity allows; both must complete before Phase 9
- Phase 10 is the critical-path dependency for Phases 11 and 12

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Verification Framework | v1.0 | 2/2 | Complete | 2026-03-03 |
| 2. Seed Import & Proto Foundation | v1.0 | 2/2 | Complete | 2026-03-03 |
| 3. Cross-Version Validation | v1.0 | 2/2 | Complete | 2026-03-03 |
| 4. Connection Lifecycle | v1.0 | 2/2 | Complete | 2026-03-04 |
| 5. Feature Channel Documentation | v1.0 | 2/2 | Complete | 2026-03-04 |
| 6. Historical Bookkeeping | v1.5 | 1/1 | Complete | 2026-04-07 |
| 7. VW Capture Analysis | v1.5 | 2/2 | Complete | 2026-04-08 |
| 8. 16.4 Cross-Version Validation | 2/2 | Complete   | 2026-04-08 | — |
| 9. OEM Methodology & Divergence Report | v1.5 | 0/2 | Not started | — |
| 10. Gold-Tier Promotion Walk | v1.5 | 0/2 | Not started | — |
| 11. Channel Architecture Reference | v1.5 | 0/2 | Not started | — |
| 12. Audit Report Generator | v1.5 | 0/1 | Not started | — |
