# Salvage Presync Corrections Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Recover only the valid presync fixes from `wip/root-main-presync-20260322` by landing the sensor-direction corrections and the nav distance-unit/baseline corrections on top of current `main`, without reintroducing stale docs or removing the dist publishing workflow.

**Architecture:** Treat the WIP branch as a source of candidate hunks, not as mergeable history. Apply two narrow slices onto a clean salvage branch, verify each slice against current repository truth, and update the handoff log with exactly what was recovered and why the broader WIP branch was rejected.

**Tech Stack:** git, protobuf/protoc, Markdown, JSON, bash

---

### Task 1: Recover sensor-direction corrections

**Files:**
- Modify: `oaa/sensor/SensorRequestMessage.proto`
- Modify: `oaa/sensor/SensorStartResponseMessage.proto`
- Modify: `oaa/sensor/SensorEventIndicationMessage.proto`
- Modify: `oaa/sensor/SensorErrorMessage.proto`
- Modify: `docs/channels/sensor.md`
- Modify: `docs/channel-map.md`
- Modify: `docs/interactions/04-channel-lifecycle.md`
- Modify: `docs/troubleshooting.md`

**Step 1: Write the failing verification**

Run:

```bash
rg -n "Sent by the head unit to request sensor data|Direction: HU -> Phone\\.|SensorRequest \\| HU -> Phone|SensorStartResponse \\| Phone -> HU|SensorEventIndication \\| Phone -> HU|SensorError \\| Phone -> HU|SensorStartRequest to subscribe" \
  oaa/sensor docs/channels/sensor.md docs/channel-map.md docs/interactions/04-channel-lifecycle.md docs/troubleshooting.md
```

Expected: matches present on current `main`, proving the stale direction claims still exist.

**Step 2: Apply only the sensor-direction fixes from the WIP branch**

Update the proto comments and docs so they consistently reflect:

- `SensorRequest`: Phone -> HU
- `SensorStartResponse`: HU -> Phone
- `SensorEventIndication`: HU -> Phone
- `SensorError`: HU -> Phone

Do not touch unrelated wording outside the sensor/video-focus corrections already identified.

**Step 3: Run verification to prove the stale claims are gone**

Run:

```bash
mkdir -p /tmp/oaa_sensor_verify
protoc --proto_path=. --cpp_out=/tmp/oaa_sensor_verify \
  oaa/sensor/SensorRequestMessage.proto \
  oaa/sensor/SensorStartResponseMessage.proto \
  oaa/sensor/SensorEventIndicationMessage.proto \
  oaa/sensor/SensorErrorMessage.proto
rg -n "Sent by the head unit to request sensor data|Direction: HU -> Phone\\.|SensorRequest \\| HU -> Phone|SensorStartResponse \\| Phone -> HU|SensorEventIndication \\| Phone -> HU|SensorError \\| Phone -> HU|SensorStartRequest to subscribe" \
  oaa/sensor docs/channels/sensor.md docs/channel-map.md docs/interactions/04-channel-lifecycle.md docs/troubleshooting.md
```

Expected: `protoc` exit 0; `rg` returns no matches.

**Step 4: Commit**

```bash
git add oaa/sensor docs/channels/sensor.md docs/channel-map.md docs/interactions/04-channel-lifecycle.md docs/troubleshooting.md
git commit -m "docs: correct sensor channel directions"
```

### Task 2: Recover nav distance-unit corrections

**Files:**
- Modify: `oaa/navigation/NavigationTurnEventMessage.proto`
- Modify: `oaa/navigation/InstrumentClusterMessages.proto`
- Modify: `docs/channels/nav.md`
- Modify: `analysis/baselines/non_media/active-navigation.normalized.json`
- Modify: `analysis/baselines/non_media/general.normalized.json`

**Step 1: Write the failing verification**

Run:

```bash
rg -n "DISTANCE_UNIT_UNKNOWN_6|7 values \\(0-6\\)" \
  oaa/navigation docs/channels/nav.md analysis/baselines/non_media/{active-navigation,general}.normalized.json
```

Expected: matches present on current `main`, proving the stale distance-unit labels remain.

**Step 2: Apply only the distance-unit fixes from the WIP branch**

Update the canonical enum/docs/baselines so they reflect:

- value `3` = `KILOMETERS_P1`
- value `5` = `MILES_P1`
- value `6` = `FEET`
- value `7` = `YARDS`

Also update the nav docs to describe the precision variants and the shared `0x8005` / `0x8007` unit coding accurately.

Do not pull in the WIP branch’s stale claim that 16.2 removed legacy `0x8004`.

**Step 3: Run verification to prove the corrections landed**

Run:

```bash
mkdir -p /tmp/oaa_nav_verify
protoc --proto_path=. --cpp_out=/tmp/oaa_nav_verify \
  oaa/navigation/NavigationTurnEventMessage.proto \
  oaa/navigation/InstrumentClusterMessages.proto
rg -n "DISTANCE_UNIT_UNKNOWN_6|7 values \\(0-6\\)" \
  oaa/navigation docs/channels/nav.md analysis/baselines/non_media/{active-navigation,general}.normalized.json
rg -n "KILOMETERS_P1|MILES_P1|DISTANCE_UNIT_FEET|DISTANCE_UNIT_YARDS" \
  oaa/navigation/NavigationTurnEventMessage.proto docs/channels/nav.md analysis/baselines/non_media/{active-navigation,general}.normalized.json
```

Expected: `protoc` exit 0; first `rg` returns no matches; second `rg` returns the corrected names.

**Step 4: Commit**

```bash
git add oaa/navigation docs/channels/nav.md analysis/baselines/non_media/{active-navigation,general}.normalized.json
git commit -m "docs: correct nav distance unit mapping"
```

### Task 3: Record salvage outcome and final verification

**Files:**
- Modify: `docs/session-handoffs.md`

**Step 1: Append the handoff entry**

Record:

- what was salvaged from `wip/root-main-presync-20260322`
- why the full WIP branch was rejected
- which slices were intentionally excluded
- verification commands/results

**Step 2: Run final verification**

Run:

```bash
git diff --check
git status --short
```

Expected: `git diff --check` clean; `git status --short` shows only the intended staged/committed changes for this salvage branch.

**Step 3: Commit**

```bash
git add docs/session-handoffs.md docs/plans/2026-03-22-salvage-presync-corrections.md
git commit -m "docs: record presync salvage outcome"
```
