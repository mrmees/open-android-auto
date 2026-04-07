---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: OEM Evidence & Gold-Tier Promotion
status: in_progress
stopped_at: Phase 7 plan 01 complete -- OEM-01 satisfied
last_updated: "2026-04-07T23:50:00Z"
last_activity: 2026-04-07 -- Phase 7 plan 01 complete (OEM-01 satisfied)
progress:
  total_phases: 7
  completed_phases: 1
  total_plans: 12
  completed_plans: 2
  percent: 17
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-07)

**Core value:** Every published proto definition and protocol claim carries explicit verification evidence and confidence level
**Current focus:** Phase 7 plan 01 complete (OEM-01 satisfied); Phase 7 plan 02 (OEM-02, OEM-03, OEM-05) is next

## Current Position

Phase: 7 (VW Capture Analysis) -- IN PROGRESS
Plan: 07-01 -- COMPLETE; 07-02 -- PENDING
Status: Phase 7 plan 01 done. OEM-01 (fragment classification) satisfied. Plan 07-02 (SDP values, coverage manifest, candidate OEM-only msg_types) is the next actionable work.
Last activity: 2026-04-07 -- Phase 7 plan 01 complete (oem_vw_parser package + msg-type-classification reports under analysis/reports/oem-vw/)

Progress: [██░░░░░░░░] 17% (2/12 v1.5 plans complete)

## Accumulated Context

### Decisions

All v1.0 decisions logged in PROJECT.md Key Decisions table (10 entries with outcomes evaluated).

v1.5 framing decisions (2026-04-07):
- Versioned as v1.5 (minor) not v2.0 — framed as continuation of protocol reference work, not a new capability era
- VW MIB3 OI capture analysis is Phase 7 — analysis-only scope; tooling decisions deferred until analysis tells us what's needed
- Post-v1.0 ad-hoc work (channel verification, SDP layer verification, validator overhaul, nav image evidence) recorded retroactively as v1.1–v1.4 patch entries rather than folded into v1.5 scope

v1.5 roadmap decisions (2026-04-07):
- Phase numbering continues from v1.0 — Phases 6 through 12 (v1.0 shipped Phases 1-5)
- Gold promotion walk (Phase 10, TIER-04) is the milestone's headline deliverable; all other phases support or run alongside it
- TIER-04 is gated on OEM-03 coverage manifest — "every Silver proto checked" means "every Silver proto in services the VW capture actually observed"
- OEM-05 candidate novel msg_types are filtered through OEM-01 fragment classification before being labeled novel (avoids the continuation-fragment trap)
- Gold tier gets a visible scope dimension (`Gold / single-OEM` vs `Gold / multi-OEM`) via TIER-02 rather than a buried prose caveat — addresses the single-OEM trap head-on
- Phase 7 and Phase 8 operate on independent evidence sources and could run in parallel if capacity allows, but Phase 9 requires both
- HIST-01 (v1.1–v1.4 retroactive entries) is Phase 6 warmup — independent, bookkeeping, clears ledger debt before real work begins
- Phase 12 (REPORT-01) is intentionally last — running a coverage dashboard before the promotion walk would just show pre-walk Silver counts

Phase 6 execution decisions (2026-04-07):
- v1.5 milestone ledger is now accurate — MILESTONES.md jumps cleanly from v1.0 → v1.1 → v1.2 → v1.3 → v1.4, then v1.5 work begins
- Mar 7 same-day work split between v1.2 (SDP) and v1.3 (validator) by commit-subject prefix to preserve distinct headline metrics
- Mar 22 dist-branch CI + late corrections folded into v1.4 rather than spawning a v1.4.1 (ROADMAP only enumerates v1.1–v1.4)
- Material You theming placed in v1.4 alongside nav image evidence (it's a discovery, not a channel verification) per ROADMAP success criteria
- Grouping proposal preserved at .planning/phases/06-historical-bookkeeping/grouping-proposal.md as decision trail

Phase 7 plan 01 execution decisions (2026-04-07):
- msg_type=0 demotion fires on payload-size signal alone (>32 bytes), not the freq>=100 backstop, because the size signal is already decisive — a non-empty msg_type=0 record cannot be ServiceDiscoveryFeatureA regardless of how many times it appears
- Frequency threshold knee detection scans from N=3 instead of N=2 because freq=1 is the noise floor (1,032 distinct singletons on the live capture); the 1→2 drop is dominated by garbage and is not the real signaling boundary
- Wire walker treats `field_num==0` during tag decoding as a clean padding-bail sentinel rather than a wire-walk failure (verified on real PingRequest seq=58 from the VW capture: `000b08e7c9dccace6a100000`)
- `build_descriptor_bundle` is called with explicit `repo_root` + `out_dir` arguments in conftest.py to match the existing `proto_stream_validator/tests/test_decode.py` shape (the plan's no-arg snippet was wrong about the actual signature)
- Histogram snapshot test allows ±1 absolute slack on Tier B (and ±1% on Tier A/C) to tolerate descriptor-map edge boundary cases without false-failing on legitimate ±1 record drift
- Live capture results: 7,954 records → A=267, B=3,890, C=3,797; standalone=4,147, probable_first=3, continuation_or_garbage=3,804; reassembled=0, unattributed=0; msg_type=0 demoted=2,751; empirical freq threshold=3

### Pending Todos

- Phase 7 plan 02 (OEM-02 SDP values, OEM-03 coverage manifest, OEM-05 candidate OEM-only msg_types). Reusable assets from 07-01: the oem_vw_parser package, all test fixtures, the descriptor bundle pattern, and the classification reports under analysis/reports/oem-vw/. 07-02 extends run.py and adds sdp_decode.py, coverage.py, and candidates.py as siblings.

### Blockers/Concerns

- aa-logcat tool has broken logcat capture on Android 13+ (Shizuku fix needed) — affects DHU observation evidence gathering, but not v1.5 critical path
- Single-OEM evidence only — Gold tier promotions off this capture are technically "VW MIB3 OI 2024 Gold," not generalized OEM Gold. Addressed in v1.5 via TIER-02 scope dimension; multi-OEM corroboration remains a v2 problem (MOEM-01..03)
- VW capture format has no `channel_id` (on-phone Frida hook lives inside AA framing layer) — addressed in v1.5 via TIER-05 non-claim boundary documentation
- VW runs AA 16.4, DHU baselines span older APKs — version-alignment required in OEM-04 divergence report (shaped the Phase 9 dependency on Phase 8)

## Session Continuity

Last session: 2026-04-07T23:50:00Z
Stopped at: Phase 7 plan 01 complete -- 50 tests passing, msg-type-classification.md/json on disk, OEM-01 satisfied
Resume file: .planning/phases/07-vw-capture-analysis/07-02-PLAN.md
