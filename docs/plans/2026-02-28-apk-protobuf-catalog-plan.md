# APK Protobuf Catalog Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an evidence-backed protobuf definition catalog for Android Auto APK `v16.1`, with strict confidence gating and a separate unknown queue.

**Architecture:** Keep the existing `apk_indexer` extraction pipeline as the signal source, then add a catalog derivation stage that classifies candidates into accepted vs unknown using explicit rules. Persist catalog/evidence/unknown outputs in SQLite and JSON, and expose query templates for future protobuf-structure work. Use TDD for each pipeline increment and protect reproducibility with deterministic output checks.

**Tech Stack:** Python 3, `pytest`, SQLite (`sqlite3`), Markdown docs, SQL query templates, existing `analysis/tools/apk_indexer` modules.

---

### Task 1: Extend SQLite Contract for Catalog/Evidence/Unknown Outputs

**Skills:** `@test-driven-development` `@verification-before-completion`

**Files:**
- Modify: `analysis/tools/apk_indexer/tests/test_writers.py`
- Modify: `analysis/tools/apk_indexer/write_sqlite.py`

**Step 1: Write the failing schema test**

Add expected tables to `test_sqlite_schema_created`:

```python
assert "proto_catalog" in tables
assert "proto_evidence" in tables
assert "proto_unknowns" in tables
assert "run_metadata" in tables
```

**Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/apk_indexer/tests/test_writers.py::test_sqlite_schema_created -v
```

Expected: `FAIL` because new tables do not exist.

**Step 3: Write minimal schema implementation**

Add table DDL to `_create_schema`:

```sql
CREATE TABLE IF NOT EXISTS proto_catalog (...);
CREATE TABLE IF NOT EXISTS proto_evidence (...);
CREATE TABLE IF NOT EXISTS proto_unknowns (...);
CREATE TABLE IF NOT EXISTS run_metadata (...);
```

Add `DELETE FROM ...` calls for new tables in `write_sqlite`.

**Step 4: Run test to verify it passes**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/apk_indexer/tests/test_writers.py::test_sqlite_schema_created -v
```

Expected: `PASS`.

**Step 5: Commit**

```bash
git add analysis/tools/apk_indexer/tests/test_writers.py analysis/tools/apk_indexer/write_sqlite.py
git commit -m "feat(apk-indexer): add sqlite schema tables for proto catalog outputs"
```

---

### Task 2: Add Confidence Gate Classifier (Accepted vs Unknown)

**Skills:** `@test-driven-development`

**Files:**
- Create: `analysis/tools/apk_indexer/confidence.py`
- Create: `analysis/tools/apk_indexer/tests/test_confidence.py`

**Step 1: Write failing classifier tests**

Create tests for three scenarios: high-confidence accept, low-confidence unknown, and borderline unknown:

```python
def test_classify_accepts_high_confidence():
    accepted, unknown = classify_candidates([{
        "class_name": "vvh",
        "evidence_sources": ["descriptor", "field_decls", "proto_writes"],
    }])
    assert len(accepted) == 1
    assert len(unknown) == 0
```

```python
def test_classify_routes_low_confidence_to_unknown():
    accepted, unknown = classify_candidates([{
        "class_name": "x1a",
        "evidence_sources": ["proto_writes"],
    }])
    assert len(accepted) == 0
    assert unknown[0]["reason"] == "insufficient_evidence"
```

**Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/apk_indexer/tests/test_confidence.py -v
```

Expected: `FAIL` (`ModuleNotFoundError` or missing function).

**Step 3: Implement minimal classifier**

In `confidence.py`:

```python
def classify_candidates(candidates):
    accepted = []
    unknown = []
    for row in candidates:
        sources = set(row.get("evidence_sources", []))
        if len(sources) >= 2 and "descriptor" in sources:
            accepted.append({**row, "confidence": "high"})
        else:
            unknown.append({**row, "reason": "insufficient_evidence"})
    return accepted, unknown
```

**Step 4: Run tests to verify pass**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/apk_indexer/tests/test_confidence.py -v
```

Expected: `PASS`.

**Step 5: Commit**

```bash
git add analysis/tools/apk_indexer/confidence.py analysis/tools/apk_indexer/tests/test_confidence.py
git commit -m "feat(apk-indexer): add confidence classifier for proto definition candidates"
```

---

### Task 3: Build Catalog Derivation Stage and Persist Outputs

**Skills:** `@test-driven-development`

**Files:**
- Create: `analysis/tools/apk_indexer/catalog.py`
- Create: `analysis/tools/apk_indexer/tests/test_catalog.py`
- Modify: `analysis/tools/apk_indexer/run_indexer.py`
- Modify: `analysis/tools/apk_indexer/write_sqlite.py`
- Modify: `analysis/tools/apk_indexer/tests/test_run_indexer.py`
- Modify: `analysis/tools/apk_indexer/tests/test_writers.py`

**Step 1: Write failing catalog derivation tests**

Create `test_catalog.py`:

```python
def test_build_catalog_splits_accepted_and_unknown():
    signals = {
        "proto_classes": [{"class_name": "vvh", "descriptor": "....", "field_count": 3}],
        "proto_writes": [{"target": "vvhVar.b", "op": "|=", "value": "16"}],
    }
    out = build_catalog(signals, apk_version="16.1")
    assert len(out["proto_catalog"]) == 1
    assert len(out["proto_unknowns"]) == 0
```

Add a second case with weak evidence that must appear in `proto_unknowns`.

**Step 2: Run tests to verify failure**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/apk_indexer/tests/test_catalog.py -v
```

Expected: `FAIL` (missing module/function).

**Step 3: Implement minimal catalog stage**

In `catalog.py`, derive candidates from `proto_classes`, gather evidence tags, call `classify_candidates`, then return:

```python
{
  "proto_catalog": [...],
  "proto_evidence": [...],
  "proto_unknowns": [...],
  "run_metadata": [...],
}
```

Wire it in `run_indexer.py` before writing outputs:

```python
catalog_outputs = build_catalog(signals, apk_version=version_name)
signals.update(catalog_outputs)
```

Add inserts for new signal keys in `write_sqlite.py`.

**Step 4: Run focused tests**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/apk_indexer/tests/test_catalog.py analysis/tools/apk_indexer/tests/test_run_indexer.py analysis/tools/apk_indexer/tests/test_writers.py -v
```

Expected: all selected tests `PASS`.

**Step 5: Commit**

```bash
git add analysis/tools/apk_indexer/catalog.py analysis/tools/apk_indexer/run_indexer.py analysis/tools/apk_indexer/write_sqlite.py analysis/tools/apk_indexer/tests/test_catalog.py analysis/tools/apk_indexer/tests/test_run_indexer.py analysis/tools/apk_indexer/tests/test_writers.py
git commit -m "feat(apk-indexer): derive and persist proto catalog, evidence, and unknown queues"
```

---

### Task 4: Add Query Pack and Report Sections for Catalog Review

**Files:**
- Create: `analysis/tools/apk_indexer/sql/01_catalog_overview.sql`
- Create: `analysis/tools/apk_indexer/sql/02_proto_field_matrix.sql`
- Create: `analysis/tools/apk_indexer/sql/03_unknown_queue.sql`
- Create: `analysis/tools/apk_indexer/QUERY_PACK.md`
- Modify: `analysis/tools/apk_indexer/report.py`
- Modify: `analysis/tools/apk_indexer/tests/test_report.py`

**Step 1: Write failing report test**

Extend `test_report.py` to assert new summary headings:

```python
assert "## Catalog Totals" in body
assert "## Unknown Queue Totals" in body
```

**Step 2: Run test to verify failure**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/apk_indexer/tests/test_report.py -v
```

Expected: `FAIL` because sections do not exist yet.

**Step 3: Implement report and query pack**

Add catalog sections in `report.py`, and add three SQL templates:

```sql
-- 01_catalog_overview.sql
select confidence, count(*) as n
from proto_catalog
group by confidence
order by n desc;
```

```sql
-- 03_unknown_queue.sql
select class_name, reason, evidence_count
from proto_unknowns
order by evidence_count desc, class_name;
```

Document usage in `QUERY_PACK.md` with copy-paste `sqlite3` commands.

**Step 4: Run tests**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/apk_indexer/tests/test_report.py -v
```

Expected: `PASS`.

**Step 5: Commit**

```bash
git add analysis/tools/apk_indexer/report.py analysis/tools/apk_indexer/tests/test_report.py analysis/tools/apk_indexer/sql/01_catalog_overview.sql analysis/tools/apk_indexer/sql/02_proto_field_matrix.sql analysis/tools/apk_indexer/sql/03_unknown_queue.sql analysis/tools/apk_indexer/QUERY_PACK.md
git commit -m "docs(apk-indexer): add catalog query pack and summary report sections"
```

---

### Task 5: Add Reproducibility + Benchmark Harness (E2E Wall-Clock Baseline)

**Skills:** `@verification-before-completion`

**Files:**
- Create: `analysis/tools/apk_indexer/benchmark.py`
- Create: `analysis/tools/apk_indexer/tests/test_benchmark.py`
- Modify: `analysis/tools/apk_indexer/README.md`
- Modify: `analysis/tools/apk_indexer/Makefile`

**Step 1: Write failing benchmark test**

Create a test that validates benchmark output shape:

```python
def test_benchmark_returns_wall_clock_metrics(tmp_path):
    result = benchmark_runs([0.8, 0.7, 0.9])
    assert result["runs"] == 3
    assert "mean_seconds" in result
    assert "p95_seconds" in result
```

**Step 2: Run to verify failure**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/apk_indexer/tests/test_benchmark.py -v
```

Expected: `FAIL` (missing benchmark module/function).

**Step 3: Implement minimal benchmark module + Make target**

In `benchmark.py` provide:

```python
def benchmark_runs(samples):
    ...
```

and CLI to run indexer N times and emit JSON to stdout or file.

Add Make target:

```make
.PHONY: benchmark
benchmark:
	cd ../../.. && PYTHONPATH=$(PYTHONPATH) python3 analysis/tools/apk_indexer/benchmark.py --source "$(SOURCE)" --analysis-root "$(ANALYSIS_ROOT)" --runs 3
```

Update README with benchmark usage and expected output fields.

**Step 4: Run tests**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/apk_indexer/tests/test_benchmark.py -v
```

Expected: `PASS`.

**Step 5: Commit**

```bash
git add analysis/tools/apk_indexer/benchmark.py analysis/tools/apk_indexer/tests/test_benchmark.py analysis/tools/apk_indexer/README.md analysis/tools/apk_indexer/Makefile
git commit -m "feat(apk-indexer): add e2e wall-clock benchmark harness"
```

---

### Task 6: Run Full Verification and Update Roadmap/Handoff

**Skills:** `@verification-before-completion`

**Files:**
- Modify: `docs/roadmap-current.md`
- Modify: `docs/session-handoffs.md`
- Verify: `analysis/tools/apk_indexer/*`

**Step 1: Run full test suite**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/apk_indexer/tests -v
```

Expected: all tests pass.

**Step 2: Run canonical indexer smoke command**

Run:

```bash
python3 analysis/tools/apk_indexer/run_indexer.py --source /home/matt/claude/personal/openautopro/firmware/android-auto-apk/decompiled --analysis-root analysis --scope all
```

Expected: versioned output directory with SQLite/JSON/report and no exceptions.

**Step 3: Update roadmap and session handoff**

Update `docs/roadmap-current.md` `Now` section to reflect:
- catalog contract freeze
- evidence-backed accepted catalog
- unknown queue triage

Append `docs/session-handoffs.md` entry with:
- what changed
- why
- status
- next 1-3 steps
- exact verification commands/results

**Step 4: Commit final integration state**

```bash
git add docs/roadmap-current.md docs/session-handoffs.md
git commit -m "docs: update roadmap and handoff for apk protobuf catalog phase"
```

