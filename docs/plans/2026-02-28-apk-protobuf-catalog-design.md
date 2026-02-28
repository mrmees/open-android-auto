# APK Protobuf Catalog Design (2-Week Reset)

**Date:** 2026-02-28  
**Status:** Approved

## Goal

Within 2 weeks, adequately explore Android Auto APK `v16.1` and produce a high-confidence protobuf definition catalog that is useful for future protobuf processing work.

## Locked Decisions

- Time horizon: 2 weeks
- Canonical source: APK `v16.1`
- Version strategy: canonical single-version ingest now, with compatibility hooks for future versions
- Priority: completeness first
- Review style: moderate-to-heavy manual review
- Confidence policy: uncertain definitions are excluded from final catalog
- Correction policy: correction discoveries are report-only until validated

## Acceptance Criteria

1. Master catalog of protobuf definitions for APK `v16.1`
2. Evidence/provenance attached to every accepted definition
3. Separate unknown/follow-up queue for low-confidence findings
4. Reproducible extraction workflow for canonical source
5. Query layer/templates for protobuf structure analysis

## Architecture

### Components

1. **Extractor and index builder**  
   Existing entrypoint: `analysis/tools/apk_indexer/run_indexer.py`  
   Existing extract/write layers: `extract.py`, `write_sqlite.py`, `write_json.py`

2. **Canonical schema and evidence model**  
   Backed by SQLite outputs in `analysis/android_auto_<version>/apk-index/sqlite/apk_index.db` and extended with explicit confidence/evidence fields for protobuf definitions.

3. **Definition catalog view**  
   A curated, high-confidence output derived from indexed signals, used as the source of truth for downstream proto work.

4. **Unknown queue**  
   Separate output for candidates that fail confidence gates, including follow-up notes.

5. **Query pack**  
   Ready-to-run SQL templates and short usage docs for exploring message/field/enum relationships.

### Data Flow

1. Run canonical extraction/indexing for `v16.1`
2. Generate raw signals (proto classes, writes, accesses, enum/switch mappings, call edges, references)
3. Apply confidence/evidence rules to candidate definitions
4. Split outputs:
   - high-confidence definitions -> final catalog
   - low-confidence definitions -> unknown queue
5. Run query templates against catalog/evidence outputs
6. Produce summary report for completeness status and follow-up backlog

## Operating Rules

### Confidence Gate

- Only high-confidence definitions are admitted to final catalog.
- Anything below threshold goes to unknown queue.

### Correction Handling

- If extraction suggests current assumptions are wrong, emit candidate correction reports.
- Candidate corrections do not auto-update final catalog.
- Promotion requires explicit validation.

### Scope Discipline

- Target `v16.1` as canonical in this window.
- Build extension points for future versions, but do not implement full multi-version ingest now.

## Delivery Plan (2 Weeks)

### Week 1 (Contract Freeze)

- Finalize schema and catalog contract
- Finalize evidence model and confidence rubric
- Finalize unknown queue format
- Confirm canonical reproducible run path for `v16.1`

### Week 2 (Operationalization)

- Populate high-confidence catalog from canonical run
- Populate unknown queue and manual follow-up list
- Deliver query pack and quick-start usage guide
- Record baseline end-to-end runtime for future `>=2x` improvement work

## Error Handling

- Extraction failures: fail fast with actionable run context (source path, phase, exception)
- Partial/inconsistent evidence: mark unknown; never silently promote to catalog
- Schema drift risks: enforce schema contract checks in tests before accepting writes

## Testing Strategy

1. Unit tests for extraction and writer behavior (existing `analysis/tools/apk_indexer/tests/*`)
2. Contract tests for schema fields and catalog/unknown split behavior
3. Reproducibility checks on canonical source:
   - rerun extraction and verify stable output structure
4. Query smoke tests for provided analysis templates

## Out of Scope (This Window)

- Full multi-version ingestion and diffing
- Auto-applying correction discoveries
- Throughput optimization as primary objective

## Success Signal

At the end of this 2-week phase, collaborators can:

1. Run the canonical pipeline for `v16.1`
2. Inspect an evidence-backed final protobuf catalog
3. See all uncertain items in a separate unknown queue with follow-up notes
4. Use query templates immediately for protobuf-structure analysis
