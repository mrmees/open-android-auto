---
phase: 4
slug: connection-lifecycle
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-04
validated: 2026-03-04
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + bash |
| **Config file** | `scripts/proto-check.sh` |
| **Quick run command** | `python3 -m pytest analysis/tools/interaction_docs/tests/test_phase04_validation.py -v` |
| **Full suite command** | `python3 -m pytest analysis/tools/interaction_docs/tests/ -v && bash scripts/proto-check.sh` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bash scripts/proto-check.sh`
- **After every plan wave:** Run phase 4 validation tests
- **Before `/gsd:verify-work`:** Full suite must be green + all 5 docs reviewed
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | DOCS-01 | smoke | `bash scripts/proto-check.sh` | Yes | ✅ green |
| 04-01-02 | 01 | 1 | DOCS-01 | integration | `pytest test_phase04_validation.py::test_interaction_doc_exists -v` | Yes | ✅ green |
| 04-01-03 | 01 | 1 | DOCS-01 | integration | `pytest test_phase04_validation.py::test_audit_yaml_links_resolve -v` | Yes | ✅ green |
| 04-01-04 | 01 | 1 | DOCS-01 | integration | `pytest test_phase04_validation.py::test_document_chain_link_exists -v` | Yes | ✅ green |
| 04-02-01 | 02 | 1 | DOCS-01 | integration | `pytest test_phase04_validation.py::test_minimum_viable_connection_is_section_heading -v` | Yes | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All requirements now covered by automated tests:

- **Doc existence:** 5 parametrized tests verify all interaction docs (01-05) exist
- **Audit YAML links:** 10 tests parse markdown links and verify referenced `.audit.yaml` files exist on disk (38 unique links verified)
- **Document chain:** 4 tests verify forward links between consecutive docs (01→02→03→04→05)
- **MVC checklist:** 2 tests verify MVC checklist exists as section heading in doc 04

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| New doc 05 follows established template | DOCS-01 | Template compliance is structural, not automatable | Compare section headings/structure against docs 01-04 |
| Confidence badges match audit YAML tiers | DOCS-01 | Requires cross-referencing prose tier text against YAML `tier` field | For each badge, verify tier matches `.audit.yaml` sidecar |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-03-04

---

## Validation Audit 2026-03-04

| Metric | Count |
|--------|-------|
| Gaps found | 4 |
| Resolved | 4 |
| Escalated | 0 |

Tests: `analysis/tools/interaction_docs/tests/test_phase04_validation.py` (21 tests, all green)
