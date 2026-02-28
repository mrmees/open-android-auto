# Obfuscation Chain Resolution Design

**Date:** 2026-02-28  
**Status:** Approved

## Goal

Reduce manual "daisy-chaining" through obfuscated APK sources by adding systematic
reference-graph traversal that recovers canonical protobuf naming evidence.

## Problem Statement

Current extraction can identify many protobuf-relevant signals, but recovering
meaningful names across obfuscation layers still requires manual chain-following.
That manual step is slow, inconsistent, and hard to reproduce.

## Scope

### In Scope

1. Build a reference graph from decompiled source relationships.
2. Detect naming anchors (stable semantic nodes) used for recovery.
3. Resolve obfuscated chains from candidate nodes to naming anchors.
4. Persist chain evidence and confidence for each proposed recovery.
5. Keep unresolved and low-confidence mappings in a separate queue.

### Out of Scope

1. Full semantic inference for every unknown class in this phase.
2. Auto-promoting uncertain mappings into the final catalog.
3. Full multi-version APK ingestion beyond canonical `v16.1`.

## Architecture

### 1) Reference Graph Builder

Build an explicit graph with nodes and directed edges from extracted signals:

- class -> class references
- method -> call target
- field access -> field owner
- switch case -> dispatch target
- proto write target -> proto-class candidate

Output is a queryable graph model suitable for bounded traversal.

### 2) Anchor Detector

Mark nodes with stable semantic value ("anchors"), for example:

- enum constant labels
- descriptor-derived field labels
- existing known `oaa` proto/entity names
- known message/channel ID semantics

Anchors are weighted by reliability and source type.

### 3) Chain Resolver

For each obfuscated candidate:

1. Start at candidate node.
2. Traverse graph edges with depth and cycle limits.
3. Stop when anchor criteria are met or traversal budget is exhausted.
4. Emit proposed canonical mapping, chain path, confidence, and stop reason.

### 4) Evidence Store

Persist:

- proposed canonical mappings
- chain paths used to derive each proposal
- anchor evidence details
- unresolved queue entries with reasons

Storage is emitted in both SQLite and JSON-compatible output for query/report
workflows.

## Data Flow

1. Existing extraction/indexing runs.
2. Graph builder assembles reference graph from extracted signals.
3. Anchor detector marks semantic anchor nodes.
4. Chain resolver attempts recovery for obfuscated candidates.
5. Results split:
   - high-confidence mappings -> recovered-name catalog
   - medium/low confidence -> unresolved queue
6. Query/report surfaces recovered mappings and unresolved follow-up.

## Confidence Model

### Levels

1. **High**: strong anchor reachability with consistent path evidence.
2. **Medium**: partial anchor support or mild ambiguity.
3. **Low**: weak or no anchor support.

### Promotion Policy

- Only **High** confidence mappings are promotable.
- **Medium/Low** remain report-only in unresolved queue.
- Ambiguous candidates are recorded, never auto-selected.

## Failure Handling

1. Bounded traversal depth and time budgets prevent runaway resolution.
2. Cycle detection records looped paths and terminates safely.
3. Resolver failures do not block base extraction outputs.
4. Stop reasons are explicit (`cycle_detected`, `depth_limit`, `no_anchor`, etc.).

## Rollout Plan

### Phase A: Shadow Mode

- Resolver enabled in report-only mode.
- No catalog promotion; gather evidence quality and unresolved patterns.

### Phase B: High-Confidence Promotion

- Promote only high-confidence mappings with full evidence trails.
- Keep medium/low in unresolved queue.

### Phase C: Heuristic Tightening

- Refine anchor weights and traversal priorities based on unresolved-queue analysis.
- Expand fixture coverage for newly solved chain patterns.

## Testing Strategy

1. Unit tests for graph construction and traversal mechanics.
2. Fixture tests for known obfuscated chains to expected canonical names.
3. Regression tests for unresolved/ambiguous behaviors.
4. End-to-end tests ensuring base extractor outputs remain stable.

## Success Criteria

1. Manual naming work shifts from ad-hoc chain hunting to reviewing unresolved queue.
2. Recovered-name proposals include reproducible chain evidence.
3. High-confidence recovered mappings are consistent across reruns.
4. Base extraction remains reliable while chain resolution iterates.
