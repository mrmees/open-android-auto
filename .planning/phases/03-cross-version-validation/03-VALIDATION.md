---
phase: 3
slug: cross-version-validation
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-03
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | none — use pytest defaults |
| **Quick run command** | `python3 -m pytest analysis/tools/cross_version/tests/ -x -q` |
| **Full suite command** | `python3 -m pytest analysis/ -x -q` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest analysis/tools/cross_version/tests/ -x -q`
- **After every plan wave:** Run `python3 -m pytest analysis/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-00 | 01 | 1 | TOOL-02 | scaffold | `ls analysis/tools/cross_version/tests/test_*.py` | ✅ | ✅ green |
| 03-01-01 | 01 | 1 | PROTO-03 | unit | `python3 -m pytest analysis/tools/cross_version/tests/test_tables.py -x` | ✅ | ✅ green |
| 03-01-02 | 01 | 1 | PROTO-03 | integration | `python3 -m pytest analysis/tools/cross_version/tests/test_published_outputs.py -x` | ✅ | ✅ green |
| 03-02-01 | 02 | 1 | TOOL-02 | unit | `python3 -m pytest analysis/tools/cross_version/tests/test_compare.py -x` | ✅ | ✅ green |
| 03-02-02 | 02 | 1 | TOOL-02 | unit | `python3 -m pytest analysis/tools/cross_version/tests/test_promote.py -x` | ✅ | ✅ green |
| 03-02-03 | 02 | 1 | TOOL-02 | integration | `python3 -m pytest analysis/tools/cross_version/tests/test_promoted_sidecars.py -x` | ✅ | ✅ green |
| 03-02-04 | 02 | 1 | TOOL-02 | integration | `python3 -m pytest analysis/tools/cross_version/tests/test_silver_annotations.py -x` | ✅ | ✅ green |
| 03-02-05 | 02 | 1 | TOOL-02 | unit | `python3 -m pytest analysis/tools/cross_version/tests/test_enum_fallback.py -x` | ✅ | ✅ green |
| 03-02-06 | 02 | 1 | TOOL-02 | integration | `python3 -m pytest analysis/tools/cross_version/tests/test_report.py -x` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `analysis/tools/cross_version/tests/test_compare.py` — comparison engine (4 tests)
- [x] `analysis/tools/cross_version/tests/test_promote.py` — promotion logic (3 tests)
- [x] `analysis/tools/cross_version/tests/test_tables.py` — table generation (2 tests)
- [x] `analysis/tools/cross_version/tests/test_report.py` — report structure (2 tests)
- [x] `analysis/tools/cross_version/tests/conftest.py` — shared fixtures

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

**Approval:** validated 2026-03-03

---

## Validation Audit 2026-03-03

| Metric | Count |
|--------|-------|
| Gaps found | 4 |
| Resolved | 4 |
| Escalated | 0 |

Tests added:
- `test_published_outputs.py` — 8 integration tests verifying docs/cross-version/ tables exist with version columns
- `test_promoted_sidecars.py` — 431 parametric tests validating all 143 silver sidecars against schema + cross_version evidence
- `test_silver_annotations.py` — 431 parametric tests verifying silver proto annotations match sidecars
- `test_enum_fallback.py` — 6 unit tests for enum-class comparison fallback path

Total: 887 tests passing (11 pre-existing + 876 new)
