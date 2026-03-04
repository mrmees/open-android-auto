---
phase: 01
slug: verification-framework
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-04
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (ad-hoc, no project-wide config) |
| **Config file** | none |
| **Quick run command** | `python3 -m pytest analysis/tools/seed_import/tests/ -v` |
| **Full suite command** | `python3 -m pytest analysis/tools/seed_import/tests/ -v` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest analysis/tools/seed_import/tests/ -v`
- **After every plan wave:** Run `python3 -m pytest analysis/tools/seed_import/tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | VERI-01 | integration | `python3 -m pytest analysis/tools/seed_import/tests/test_audit_yaml_schema_validation.py -v` | ✅ | ✅ green |
| 01-01-02 | 01 | 1 | VERI-04 | grep | Plan verify (grep checks for clean-room, aasdk, GPL, Excluded) | ✅ | ✅ green |
| 01-02-01 | 02 | 2 | VERI-02 | integration | `python3 -m pytest analysis/tools/seed_import/tests/test_audit_yaml_schema_validation.py -v` | ✅ | ✅ green |
| 01-02-02 | 02 | 2 | VERI-03 | grep | Plan verify (grep checks for all 4 evidence types + bfs_trace) | ✅ | ✅ green |
| 01-cross | — | — | VERI-01 | unit+integration | `python3 -m pytest analysis/tools/seed_import/tests/test_audit_yaml_tier_consistency.py -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 2s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-04

## Validation Audit 2026-03-04

| Metric | Count |
|--------|-------|
| Gaps found | 2 |
| Resolved | 2 |
| Escalated | 0 |
