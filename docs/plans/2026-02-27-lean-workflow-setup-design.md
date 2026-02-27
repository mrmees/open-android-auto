# Lean Workflow Setup Design

**Date:** 2026-02-27  
**Status:** Approved

## Goal

Adopt a lean, repeatable workflow in `open-android-auto` that mirrors the structure used in `openauto-prodigy`, while staying specific to this repository's protocol-reference scope.

## Scope

Add three workflow files:

1. `AGENTS.md` (repo root)
2. `docs/roadmap-current.md`
3. `docs/session-handoffs.md`

This design intentionally excludes the full management stack (`project-vision`, `wishlist`, etc.) to keep process overhead low.

## Workflow Architecture

### `AGENTS.md` (enforcement point)

Defines a mandatory loop for behavior-changing work:

1. Confirm alignment with this repository's protocol/reference mission.
2. Update `docs/roadmap-current.md` when priorities or sequencing change.
3. Run verification commands before claiming completion.
4. Append a structured handoff entry to `docs/session-handoffs.md`.

### `docs/roadmap-current.md` (priority source)

Captures active priorities in `Now / Next / Later` format so collaborators can quickly determine current focus without reading chat history.

### `docs/session-handoffs.md` (continuity log)

Append-only session record that captures what changed, why, current status, next steps, and verification evidence.

## Verification Model

Verification is adapted for a protocol/docs repository (not an app runtime repository):

- Proto compile validation for changed files:
  - `protoc --proto_path=proto --cpp_out=/tmp <changed-proto-files>`
- Docs/path sanity checks for changed documentation:
  - grep/search checks for stale file names or moved paths
- Tooling smoke checks when touching `analysis/tools/*`:
  - run the tool's own documented smoke command (from its README/Makefile)

## Error Handling Rules

- If verification fails, task status cannot be reported as complete.
- Verification failures must be recorded in the handoff entry with blocker details.
- If scope drifts beyond protocol/reference work, capture it as a future item instead of expanding current implementation scope.

## File Content Model

### `AGENTS.md`

- Purpose and scope note
- `Project Management Loop` section with required steps
- `Verification Baseline` section with command patterns
- `Completion Rule` requiring verification evidence before completion claims

### `docs/roadmap-current.md`

- `Now / Next / Later` sections
- `Focus Guardrails` to prevent app/runtime feature drift
- `Last Updated` field

### `docs/session-handoffs.md`

Append-only template fields:

- Date/session
- What changed
- Why
- Status
- Next 1-3 steps
- Verification commands/results

## Data Flow

Task start -> mission alignment check -> execute work -> update roadmap if priorities changed -> run verification -> append handoff with evidence -> handoff complete.

## Success Criteria

- A new contributor can understand current priorities by reading `docs/roadmap-current.md`.
- A new session can resume execution from `docs/session-handoffs.md` alone.
- Completion claims are supported by explicit verification command + result records.
