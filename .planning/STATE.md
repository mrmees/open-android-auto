---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: OEM Evidence & Gold-Tier Promotion
status: in_progress
stopped_at: Completed 07-02-PLAN.md -- Phase 7 done (74 tests, 8 reports, OEM-01/02/03/05 satisfied)
last_updated: "2026-04-08T00:19:31.074Z"
last_activity: 2026-04-08 -- Phase 7 plan 02 complete (SDP decoder + attribution pipeline + coverage manifest + OEM-only candidate diff; 6 new reports + 21 files; 74 tests passing)
progress:
  total_phases: 7
  completed_phases: 2
  total_plans: 12
  completed_plans: 3
  percent: 25
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-07)

**Core value:** Every published proto definition and protocol claim carries explicit verification evidence and confidence level
**Current focus:** Phase 7 COMPLETE (OEM-01/02/03/05 all satisfied); Phase 8 (cross-version analysis) is the next critical path; Phase 8 and Phase 9 are the remaining v1.5 work

## Current Position

Phase: 7 (VW Capture Analysis) -- COMPLETE
Plan: 07-01 -- COMPLETE; 07-02 -- COMPLETE
Status: Phase 7 done. OEM-01 (fragment classification), OEM-02 (production SDP values), OEM-03 (coverage manifest), and OEM-05 (candidate OEM-only msg_types) all satisfied. 8 deliverables shipped under analysis/reports/oem-vw/. The capture README has been surgically fixed (direction table swap + Analysis Outputs section). Next actionable work is Phase 8 (cross-version analysis) which is independent of Phase 7 outputs.
Last activity: 2026-04-08 -- Phase 7 plan 02 complete (SDP decoder + attribution pipeline + coverage manifest + OEM-only candidate diff; 6 new reports + 21 files; 74 tests passing)

Progress: [███░░░░░░░] 25% (3/12 v1.5 plans complete)

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

Phase 7 plan 02 execution decisions (2026-04-08):
- Direction by decode (not by file name) — the SDP request/response direction resolver tries both proto types and picks the one that decodes non-trivially. Locks the corrected direction permanently; anyone who "fixes" the README and breaks the decoder fails test_direction_resolution.
- Pre-flight Prodigy range cross-check: all 4 hypotheses dropped for VW (radio + car_control inapplicable, sensor + navigation ambiguous due to per-channel namespace collisions). surviving_hints = []. Range matching is dormant for VW; SDP narrowing is the primary signal.
- Strict 5-row attribution taxonomy preserved despite making observed[] thin: most VW Tier B records get sdp_candidates (multiple shape predicates match) → service=None → not in observed[]. The records exist in per_msg_type with service=null. Documented as locked behavior, not a bug.
- Comparative gaps filter out service_type='control' as a universal service (every capture has it on channel_id 0; not a per-channel kind). Result: comparative gaps = ['vendor_extension'] only.
- _discover_dhu_files() handles both canonical (aa_messages.jsonl) and suffixed (aa_messages_<scenario>.jsonl) DHU baseline naming — only captures/general uses the canonical pair.
- _fix_capture_readme() uses defensive single+double-space variants for the swap literal — the plan snippet had double space but the actual README uses single space. Idempotent ('right variant already present' guard).
- test_oem_only_diff garbage check loosened to 'every key in diff has at least one non-garbage record' — the plan's strict check was contradictory (a single (msg_type, direction) key can map to both garbage and non-garbage classified records).
- Live coverage results: 5 observed channels (5 av_channels), 8 intrinsic gaps, 1 comparative gap (vendor_extension), 1 anomaly.unattributed (msg_type=0x8035 out, single record), 17 OEM-only candidates by msg_type, 1,061 per_msg_type entries, baseline_snapshot_hash=ffb074e4f1...

### Pending Todos

- Phase 8 (cross-version analysis) — independent of Phase 7, ready to start. Uses APK indexes for 16.1 vs 16.2 schema diffs, not the VW capture.
- Phase 9 (divergence report) — REQUIRES BOTH Phase 7 and Phase 8 outputs. Reads analysis/reports/oem-vw/coverage.json + sdp-values.json + candidate-oem-only-msg-types.json from Phase 7.
- Phase 10 (Gold promotion walk, TIER-04) — gated on Phase 9. Reads coverage.json.observed[] to scope which Silver protos can be promoted. Override mechanism enforced via coverage.validate_override().

### Blockers/Concerns

- aa-logcat tool has broken logcat capture on Android 13+ (Shizuku fix needed) — affects DHU observation evidence gathering, but not v1.5 critical path
- Single-OEM evidence only — Gold tier promotions off this capture are technically "VW MIB3 OI 2024 Gold," not generalized OEM Gold. Addressed in v1.5 via TIER-02 scope dimension; multi-OEM corroboration remains a v2 problem (MOEM-01..03)
- VW capture format has no `channel_id` (on-phone Frida hook lives inside AA framing layer) — addressed in v1.5 via TIER-05 non-claim boundary documentation
- VW runs AA 16.4, DHU baselines span older APKs — version-alignment required in OEM-04 divergence report (shaped the Phase 9 dependency on Phase 8)

## Session Continuity

Last session: 2026-04-08T00:19:31.071Z
Stopped at: Completed 07-02-PLAN.md
Resume file: None
