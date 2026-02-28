# Proto Stream Validation Design

**Date:** 2026-02-28  
**Status:** Approved

## Goal

Add a deterministic protobuf-change validation gate based on recorded Android Auto stream traffic, so `.proto` updates are blocked if they regress real non-media message decoding.

## Scope (Phase 1)

- Validate **non-media** traffic only.
- Exclude high-volume AV payload messages to keep signal high and noise low.
- Run in `open-android-auto` as protocol-owned validation tooling.

## Locked Decisions

- Validation source: **recorded captures**, not live sessions.
- Gate policy: **no-regression diff** against committed baseline.
- Baseline updates: **strict lock** (`validate` never writes baseline; explicit `--bless` required with rationale).
- Initial integration target: `open-android-auto`.

## Alternatives Considered

1. **Capture-diff validator (selected)**
- Re-decode recorded frames with current protos and diff against baseline.
- Best fidelity to real AA traffic semantics.

2. **Descriptor-only compatibility checks**
- Useful but insufficient alone for runtime decode correctness.

3. **Hybrid (capture diff + descriptor checks)**
- Deferred. Phase 1 keeps scope tight with capture-diff only.

## Architecture

### Inputs

- Capture file: `analysis/captures/non_media/<capture-name>.jsonl`
- Baseline file: `analysis/baselines/non_media/<capture-name>.normalized.json`
- Current repo protobuf definitions under `oaa/`

### Core Pipeline

1. Load capture frames.
2. Filter/accept only non-media frames.
3. Resolve `(direction, channel_id, message_id)` to protobuf message type.
4. Decode payload bytes using current protobuf schema.
5. Normalize decoded output into stable JSON representation.
6. Compare normalized results to baseline.
7. Exit non-zero on any diff.

### Outputs

- Pass/fail status code.
- Human-readable diff report with frame index and field-path differences.

## Capture Contract

Capture format is JSONL, one frame per line:

- `ts_ms`
- `direction` (`Phone->HU` or `HU->Phone`)
- `channel_id`
- `message_id`
- `message_name`
- `payload_hex` (full payload for phase-1-eligible frames)

Phase 1 deliberately excludes AV media payload entries.

## Commands

Validate (read-only):

```bash
PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py \
  --capture analysis/captures/non_media/session_a.jsonl \
  --baseline analysis/baselines/non_media/session_a.normalized.json
```

Bless (explicit baseline update):

```bash
PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py \
  --capture analysis/captures/non_media/session_a.jsonl \
  --baseline analysis/baselines/non_media/session_a.normalized.json \
  --bless \
  --reason "intentional proto schema update for <message>"
```

## Guardrails

- Normal validate path never mutates baseline artifacts.
- `--bless` is required to update baseline.
- `--reason` is required with `--bless`.
- Bless activity must be recorded in `docs/session-handoffs.md` with rationale and verification evidence.

## Error Handling

- Unmapped frame tuple `(direction, channel_id, message_id)` -> fail as `unmapped`.
- Decode failure for mapped frame -> fail with frame index and payload context.
- Baseline missing decoded frame -> fail.
- Baseline contains extra rows no longer emitted -> fail.

## Determinism Rules

- Preserve stable frame order and frame index.
- Normalize output with deterministic key ordering.
- Strip volatile fields only if explicitly required (none in phase 1 by default).

## Testing Strategy

1. Unit tests for media/non-media filtering.
2. Unit tests for mapping-table coverage and `unmapped` failure path.
3. Unit tests for decode + normalization behavior across field types.
4. Golden test: fixed capture + baseline passes.
5. Regression test: intentional schema mismatch fails with actionable diff.

## Rollout Plan

1. Add capture-export mode in `openauto-prodigy` logger to emit full non-media payload bytes.
2. Add validator tooling in `open-android-auto` under `analysis/tools/proto_stream_validator/`.
3. Commit first canonical non-media capture and baseline artifacts.
4. Add developer commands (`validate`/`bless`) in docs and local automation.
5. Expand capture set and message-map coverage incrementally.

## Out of Scope (Phase 1)

- AV media payload validation.
- Live-session validation mode.
- Automatic baseline updates without explicit bless.
- Multi-version compatibility diffing.

## Success Criteria

- Proto changes are evaluated against real captured non-media traffic.
- Any decode/output regression fails validation by default.
- Intentional protocol changes require explicit, auditable bless updates.
