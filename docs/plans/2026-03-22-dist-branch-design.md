# Dist Branch Design

Date: 2026-03-22
Status: Approved

## Goal

Provide a consumer-facing `dist` branch that contains only the Android Auto
protobuf deliverables needed by downstream projects, without the research
archive, docs planning artifacts, or analysis tooling carried on `main`.

## Problem

`main` is the canonical research branch. That is correct for this repository,
but downstream consumers such as `openauto-prodigy` only need the protobuf
definitions. Cloning `main` pulls a large amount of unrelated archive material,
which increases object count and makes the repository a worse dependency target.

## Scope

The `dist` branch will contain only:

- `oaa/**/*.proto`
- `README.md`
- `LICENSE`

The branch will explicitly exclude:

- `research/`
- `docs/plans/`
- `tools/`
- `analysis/`
- `.audit.yaml` sidecars under `oaa/`
- any other non-deliverable artifacts from `main`

## Options Considered

### 1. Orphan `dist` branch reconstructed from `main` on release tags

Pros:

- Cleanest clone target for consumers
- No history coupling to research artifacts
- Easy to reason about and re-create

Cons:

- Separate branch maintenance flow required

### 2. Filtered branch derived from `main` history

Pros:

- Preserves more visible lineage

Cons:

- More complex to maintain safely
- Easier to leak unwanted files/history
- Worse fit for a minimal distribution surface

### 3. Separate repository

Pros:

- Hardest possible separation boundary

Cons:

- Extra maintenance overhead
- Not necessary for the current goal

## Decision

Use option 1: a true orphan `dist` branch containing only consumable outputs.

## Branch Shape

`dist` root contents:

- `oaa/` with only `.proto` files preserved under their existing paths
- `README.md` if present on `main`
- `LICENSE` if present on `main`

No generated code, no research sources, no docs tree, and no audit sidecars.

## Sync Mechanism

Add `.github/workflows/publish-dist.yml` on `main`.

Behavior:

- Trigger on pushed tags matching `v*`
- Check out `main`
- Check out `dist` into a second path
- Replace `dist` contents with the allowed file set from `main`
- Commit only if the resulting tree changed
- Push `dist`

This makes `dist` a release-synced publishing branch rather than a hand-edited
working branch.

## Safety Notes

- Do not delete anything from `main`
- Build the branch from a clean worktree so existing uncommitted user edits on
  the active `main` checkout are untouched
- Preserve repo license/readme at branch root for downstream consumption

## Verification Plan

- Inspect `dist` tree contents to confirm only allowed files exist
- Confirm `find oaa -type f` on `dist` returns only `.proto`
- Verify representative protos compile from `dist`
- Compare shallow clone object counts for `main` vs `dist` to confirm material
  reduction
