# Navigation Image Evidence Investigation Design

**Date:** 2026-03-13
**Status:** Approved
**Scope:** Protocol/evidence work only

## Goal

Determine exactly which navigation visuals are serialized over the native Android Auto navigation channel in APK 16.1 and 16.2, with special attention to turn-image, lane-image, and junction-image delivery. The output of this work is evidence strong enough to justify canonical repo doc/proto updates without relying on stale assumptions or earlier summaries.

## Decision

Use an APK-source-first, version-paired investigation.

- **Primary truth:** Decompiled APK Java source for 16.1 and 16.2
- **Secondary support:** APK index sqlite databases for discovery and cross-checking
- **Tertiary only:** Existing repo docs, comments, and prior handoffs

This avoids circular reasoning where the repo "confirms" itself.

## Ground Truth Sources

### 16.2 primary source

- `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/`
- `analysis/android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db`

### 16.1 primary source

The full 16.1 decompiled source is not stored in this repository. The source-backed evidence path lives in the sibling workspace:

- `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/`
- `analysis/android_auto_16.1.660414-release_161660414/apk-index/sqlite/apk_index.db`

### Canonical repo files that may change later

- `docs/channels/nav.md`
- `oaa/navigation/NavigationTurnEventMessage.proto`
- `oaa/navigation/NavigationNotificationMessage.proto`
- `oaa/navigation/InstrumentClusterMessages.proto`
- `oaa/navigation/NavigationTypeEnum.proto`
- `oaa/navigation/NavigationImageOptionsData.proto`

## Current Evidence Snapshot

These claims are already source-backed enough to shape the plan:

1. **16.1 sends both rich semantic nav and image-bearing legacy nav from the same `NavigationState` input.**
   - Rich path: `hkx.h(...)` builds `vzo`/`vzu` and sends `32774`.
   - Legacy path: the same method reads `NavigationStep.c` image bytes and feeds them into `n(...)`, which builds `vzm` and sends `32772`.
2. **16.1 can synthesize turn-image bytes locally if the app does not provide them.**
   - `hkx.n(...)` falls back to `hwl` resource-generated turn art before serializing `vzm`.
3. **16.2 keeps the rich semantic sender path but removes old `0x8004` as a native wire message.**
   - `hlj.mo18762h(...)` builds `vza`/`vzg` and sends semantic nav.
   - The 16.2 `vzm` class is no longer the old image-bearing nav message.
4. **16.2 still retains upstream image-bearing app/UI models.**
   - `NavigationStep.turnImage`
   - AndroidX `Maneuver.icon`
   - AndroidX `Step.lanesImage`
   - AndroidX `RoutingInfo.junctionImage`

The open question is whether any 16.2 native nav transport path still serializes image content under a new message, new gate, or `NavigationType.NEXT_TURN_IMAGE`-controlled mode.

## Evidence Ledger

| ID | Question | Status | Closing Evidence Required |
|----|----------|--------|---------------------------|
| Q1 | Does 16.1 send both `32774` semantic nav and `32772` image-bearing legacy nav from one `NavigationState` input? | Confirmed | Sender code + message class evidence |
| Q2 | Does 16.1 synthesize fallback turn images when app-side bytes are absent? | Confirmed | Sender code showing resource fallback |
| Q3 | Does 16.2 still send a rich semantic native nav message? | Confirmed | Sender code + message class evidence |
| Q4 | Does 16.2 have a native image-bearing successor to 16.1 `32772` / old `0x8004`? | Open | Sender or receiver path with exact message class |
| Q5 | Is `NavigationType.NEXT_TURN_IMAGE` reachable from a real 16.2 sender/receiver path? | Open | Capability gate + transport use site |
| Q6 | Are `junctionImage` or `lanesImage` ever serialized on the 16.2 native nav wire? | Open | Sender path or explicit exclusion evidence |
| Q7 | Which 16.1/16.2 capability checks decide whether a HU gets rich semantic nav, legacy nav, or both? | Open | PDK/config gates at sender boundary |
| Q8 | Which repo docs/proto comments must change once the investigation closes? | Open | Cross-version delta matrix + exact source citations |

Allowed statuses:

- `Open`
- `Confirmed`
- `Rejected`
- `Needs better evidence`

## Chosen Approach

### Recommended approach: APK-source-first, version-paired evidence plan

Work one claim at a time, with each claim proven or rejected from source before moving on. Keep 16.1 and 16.2 in lockstep so renamed or removed paths do not get misread as contradictions.

### Rejected alternatives

- **Proto-shape-first:** too biased toward existing repo assumptions
- **Capability-gate-first:** useful later, but too indirect for finding actual payloads

## Phases

### Phase 1: Scope and evidence ledger

Define the exact investigation questions, evidence thresholds, and crash-recovery rules. This phase is complete when the current plan and handoff docs can resume cold after a crash.

### Phase 2: 16.1 sender-path reconstruction

Trace `NavigationState` and `NavigationStep` through the real 16.1 sender stack until the following are fully explained:

- semantic `32774` path
- legacy image-bearing `32772` path
- image-byte origin and fallback generation
- gating conditions for which path a HU receives

### Phase 3: 16.2 sender-path reconstruction

Trace the 16.2 equivalent sender stack and determine:

- what replaced or removed the old 16.1 image-bearing wire path
- whether any hidden image path still exists
- whether `NEXT_TURN_IMAGE` is dead, gated, or active

### Phase 4: Cross-version delta map

Produce a matrix covering:

- message IDs
- payload shapes
- sender entrypoints
- image-byte sources
- gates/capability checks
- projected-UI-only image assets versus native-wire payloads

### Phase 5: Canonical repo updates

Update repo docs and proto comments only after claims are source-backed.

## Evidence Acceptance Rules

1. APK source beats repo docs.
2. SQLite index evidence is discovery support, not sufficient by itself for strong claims when full source exists.
3. A claim is only `Confirmed` when we can cite at least one of:
   - sender code building the payload
   - receiver code parsing/using the payload
   - generated message class proving the field shape
4. Negative claims need explicit exhausted-search notes, not silence.
5. Hypotheses stay labeled as hypotheses until closed.

## Crash-Recovery Protocol

The plan must survive compaction failures and session crashes without relying on chat memory.

### Required checkpoint outputs after each meaningful task

- Update the `Evidence Ledger` status for any question advanced
- Add or refresh a `Resume Here` block in the execution plan
- Append a `docs/session-handoffs.md` entry with:
  - last verified claim
  - exact file paths and line references
  - commands run
  - next unanswered question

### Required `Resume Here` block format

```markdown
## Resume Here

- Last completed task: `Task N`
- Last verified claim: `...`
- Evidence files:
  - `path:line`
  - `path:line`
- Next unanswered question: `...`
- Next command to run: `...`
```

### Recovery rule

After any crash, the next session must resume from the last written checkpoint in repo files. Do not rebuild context from memory first.

## Artifacts

This investigation should produce:

- `docs/plans/2026-03-13-nav-image-evidence-design.md`
- `docs/plans/2026-03-13-nav-image-evidence-plan.md`
- incremental entries in `docs/session-handoffs.md`

It may later update:

- `docs/channels/nav.md`
- relevant `oaa/navigation/*.proto` comments and confidence notes

## Success Criteria

The work is successful when:

1. The 16.1 image-bearing native nav path is fully explained from source.
2. The 16.2 native nav sender graph is fully explained from source.
3. `NEXT_TURN_IMAGE` is either confirmed, rejected, or sharply bounded as an unresolved hypothesis.
4. The repo has a crash-tolerant handoff trail that can restart the investigation after a session failure.
5. Canonical docs/proto comments reflect only source-backed claims.
