# Navigation Image Evidence Investigation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a crash-tolerant, source-backed evidence trail proving which navigation visuals are serialized over native Android Auto nav channels in 16.1 and 16.2.

**Architecture:** Start from the real app-side navigation models, trace the 16.1 and 16.2 sender paths into transport messages, and record every confirmed or rejected claim in repo docs before updating canonical protocol references. The plan is checkpoint-driven: every meaningful task ends with a handoff entry and a refreshed `Resume Here` block so work can resume cold after a crash.

**Tech Stack:** Decompiled Java source, sqlite3 APK indexes, Markdown docs, bash (`rg`, `sed`, `grep`, `sqlite3`)

---

## Key Evidence Paths

| Resource | Path |
|----------|------|
| 16.2 source | `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/` |
| 16.2 sqlite index | `analysis/android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db` |
| 16.1 source | `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/` |
| 16.1 sqlite index | `analysis/android_auto_16.1.660414-release_161660414/apk-index/sqlite/apk_index.db` |
| Design doc | `docs/plans/2026-03-13-nav-image-evidence-design.md` |
| Handoff log | `docs/session-handoffs.md` |
| Canonical nav doc | `docs/channels/nav.md` |

## Execution Rules

1. **APK source first.** Do not upgrade a claim based only on repo docs or prior handoffs.
2. **One claim per checkpoint.** Close one narrow question, then write it down.
3. **Label uncertainty plainly.** Use `Open`, `Confirmed`, `Rejected`, or `Needs better evidence`.
4. **No silent negative claims.** If a sender path is not found, document which files and symbols were searched.
5. **Keep scope protocol/evidence only.** Do not drift into HU implementation advice.
6. **Commit narrowly if the tree is dirty.** Stage only the files touched by the task.

## Evidence Ledger

| ID | Question | Status | Notes |
|----|----------|--------|-------|
| Q1 | 16.1 sends both semantic `32774` and image-bearing `32772` from `NavigationState` | Confirmed | Reconfirmed from 16.1 source: semantic `32774` path runs under `y(r)`, builds `vzu` step entries and `vze` destinations, then emits `this.k.k(32774, ...)` (`hkx.java:304-308`, `hkx.java:313-487`, `hkx.java:497-578`); `vzo` only carries repeated `vzu` + `vze` entries (`vzo.java:7-30`), and `vzu` only exposes maneuver/text/lanes/road-info fields (`vzu.java:7-30`). Legacy/image path: `NavigationStep` stores app turn-image bytes in `byte[] c` and parcels them as field `5` (`NavigationStep.java:8`, `NavigationStep.java:24`, `NavigationStep.java:59-66`); `hkx` passes `navigationStep2.c` or fallback `bArr` into `n(...)` (`hkx.java:748-756`); `n(...)` writes non-null bytes into `vzm.f` and sends `32772` (`hkx.java:1023-1033`; `vzm.java:13-15`, `vzm.java:33-34`). |
| Q2 | 16.1 synthesizes fallback turn images locally | Confirmed | Fallback input is now bounded from source: when a step lacks `NavigationStep.c`, the legacy path substitutes `bArr` before serializing bytes into `vzm.f` (`hkx.java:748-750`, `hkx.java:1023-1031`; `vzm.java:13-15`, `vzm.java:33-34`). Exact local synthesis of `bArr` is rechecked in Task 3. |
| Q3 | 16.2 rich native nav sender is semantic-only | Confirmed | Re-verify with exact citations during execution |
| Q4 | 16.2 has a native image-bearing successor path | Open | |
| Q5 | `NEXT_TURN_IMAGE` is reachable in 16.2 | Open | |
| Q6 | `junctionImage` or `lanesImage` reach native nav transport in 16.2 | Open | |
| Q7 | Cross-version capability gates controlling nav image delivery are understood | Open | |
| Q8 | Canonical repo docs are updated only after claims close | Open | |

## Resume Here

- Last completed task: `Task 2 - 16.1 legacy 32772 path consumes app turn-image bytes`
- Last verified claim: `16.1 legacy nav sender reads NavigationStep.c, falls back to bArr when missing, serializes bytes into vzm.f, and emits channel 32772`
- Evidence files:
  - `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/com/google/android/gms/car/navigation/NavigationStep.java`
  - `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java`
  - `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/vzm.java`
  - `docs/session-handoffs.md`
- Next unanswered question: `How does hkx.n(...) synthesize fallback turn-image bytes locally when the legacy sender has no app-provided image bytes?`
- Next command to run: `sed -n '838,1035p' /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java`

---

### Task 1: Reconfirm the 16.1 dual-send structure from real source

**Files:**
- Verify: `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java`
- Verify: `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/vzo.java`
- Verify: `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/vzu.java`
- Modify: `docs/plans/2026-03-13-nav-image-evidence-plan.md`
- Modify: `docs/session-handoffs.md`

**Step 1: Confirm the semantic sender exists**

Run:
```bash
sed -n '290,585p' /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java
```

Expected: `hkx.h(...)` builds `vzo`/`vzu` and sends `this.k.k(32774, ...)`.

**Step 2: Confirm the semantic payload shape**

Run:
```bash
sed -n '1,70p' /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/vzo.java
sed -n '1,70p' /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/vzu.java
```

Expected: `vzo` has repeated steps + destinations only; `vzu` has maneuver/text/lanes/road-info fields, not raw image bytes.

**Step 3: Update the Evidence Ledger**

Mark `Q1` as reconfirmed with exact line references in the notes column.

**Step 4: Refresh `Resume Here`**

Point it at Task 2 with the next unanswered question about app-side image bytes.

**Step 5: Append a handoff checkpoint**

Add a `docs/session-handoffs.md` entry that records:
- last verified claim
- `hkx.java`, `vzo.java`, `vzu.java` evidence lines
- the next unanswered question

**Step 6: Commit**

```bash
git add docs/plans/2026-03-13-nav-image-evidence-plan.md docs/session-handoffs.md
git commit -m "docs(nav): checkpoint 16.1 semantic nav sender evidence"
```

---

### Task 2: Reconfirm the 16.1 image-bearing legacy path and app-side turn-image bytes

**Files:**
- Verify: `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/com/google/android/gms/car/navigation/NavigationStep.java`
- Verify: `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java`
- Verify: `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/vzm.java`
- Modify: `docs/plans/2026-03-13-nav-image-evidence-plan.md`
- Modify: `docs/session-handoffs.md`

**Step 1: Confirm app-side `turnImage` bytes exist**

Run:
```bash
sed -n '1,80p' /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/com/google/android/gms/car/navigation/NavigationStep.java
```

Expected: `NavigationStep` contains `byte[] c` and writes it to parcel field `5`.

**Step 2: Confirm the legacy sender consumes those bytes**

Run:
```bash
sed -n '740,795p' /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java
```

Expected: `navigationStep2.c` is passed into `n(...)`.

**Step 3: Confirm the wire message has a bytes field**

Run:
```bash
sed -n '1,80p' /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/vzm.java
```

Expected: `vzm` has a `zxq` bytes field in its 6-field descriptor.

**Step 4: Update the Evidence Ledger**

Mark `Q1` and `Q2` with exact citations covering image-byte origin and serialization.

**Step 5: Refresh `Resume Here`**

Point it at Task 3 and the fallback-image question.

**Step 6: Append a handoff checkpoint**

Record the exact `NavigationStep.java`, `hkx.java`, and `vzm.java` evidence lines.

**Step 7: Commit**

```bash
git add docs/plans/2026-03-13-nav-image-evidence-plan.md docs/session-handoffs.md
git commit -m "docs(nav): checkpoint 16.1 legacy image-bearing nav path"
```

---

### Task 3: Close the 16.1 fallback image-generation question

**Files:**
- Verify: `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java`
- Modify: `docs/plans/2026-03-13-nav-image-evidence-plan.md`
- Modify: `docs/session-handoffs.md`

**Step 1: Trace fallback generation in the legacy sender**

Run:
```bash
sed -n '838,1035p' /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java
```

Expected: when incoming `bArr` is null, `hkx.n(...)` uses `hwl` resource helpers (`da_turn_*`) to synthesize image bytes before building `vzm`.

**Step 2: Update the Evidence Ledger**

Mark `Q2` as `Confirmed` with the specific fallback mechanism.

**Step 3: Refresh `Resume Here`**

Point it at Task 4 and the 16.1 capability-gate question.

**Step 4: Append a handoff checkpoint**

Record the image-fallback evidence and the next gate to trace.

**Step 5: Commit**

```bash
git add docs/plans/2026-03-13-nav-image-evidence-plan.md docs/session-handoffs.md
git commit -m "docs(nav): checkpoint 16.1 fallback turn-image generation"
```

---

### Task 4: Trace 16.1 capability gates that choose semantic vs legacy delivery

**Files:**
- Verify: `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java`
- Verify: `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hzy.java`
- Modify: `docs/plans/2026-03-13-nav-image-evidence-plan.md`
- Modify: `docs/session-handoffs.md`

**Step 1: Identify the gate controlling semantic rich-path emission**

Run:
```bash
grep -n "if (y(r))" /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java
```

Expected: the semantic `32774` send is guarded by `y(r)`.

**Step 2: Identify the gate controlling legacy/image path emission**

Run:
```bash
grep -n "if (z(carInfo))" /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java
```

Expected: the legacy/image-bearing path is guarded by `z(carInfo)`.

**Step 3: Capture any evidence available about what these gates mean**

Run:
```bash
rg -n "boolean y\\(|boolean z\\(|CarInfo" /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java -g '*.java'
```

Expected: enough surrounding context to document which HU capability/PDK threshold selects each path, or a clearly bounded open question if helper methods remain opaque.

**Step 4: Update the Evidence Ledger**

Advance `Q7` to `Confirmed` or `Needs better evidence`, but do not overstate.

**Step 5: Refresh `Resume Here`, append handoff, commit**

```bash
git add docs/plans/2026-03-13-nav-image-evidence-plan.md docs/session-handoffs.md
git commit -m "docs(nav): checkpoint 16.1 nav delivery gates"
```

---

### Task 5: Reconfirm the 16.2 semantic native sender and message shape

**Files:**
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java`
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/vza.java`
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/vzg.java`
- Modify: `docs/plans/2026-03-13-nav-image-evidence-plan.md`
- Modify: `docs/session-handoffs.md`

**Step 1: Confirm the semantic sender exists in 16.2**

Run:
```bash
sed -n '360,620p' analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java
```

Expected: `hlj.mo18762h(...)` builds `vza`/`vzg` and sends `32774`.

**Step 2: Confirm the semantic payload shape is image-free**

Run:
```bash
sed -n '1,220p' analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/vza.java
sed -n '1,220p' analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/vzg.java
```

Expected: only repeated steps/destinations and maneuver/text/lanes/road-info fields, with no raw image bytes.

**Step 3: Update the Evidence Ledger**

Mark `Q3` as reconfirmed with exact citations.

**Step 4: Refresh `Resume Here`, append handoff, commit**

```bash
git add docs/plans/2026-03-13-nav-image-evidence-plan.md docs/session-handoffs.md
git commit -m "docs(nav): checkpoint 16.2 semantic nav sender evidence"
```

---

### Task 6: Determine whether 16.2 still feeds image bytes into any native sender

**Files:**
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/com/google/android/gms/car/navigation/NavigationStep.java`
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java`
- Modify: `docs/plans/2026-03-13-nav-image-evidence-plan.md`
- Modify: `docs/session-handoffs.md`

**Step 1: Confirm app-side `turnImage` bytes still exist in 16.2**

Run:
```bash
sed -n '1,90p' analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/com/google/android/gms/car/navigation/NavigationStep.java
```

Expected: `byte[] f20729c` still exists and is parcelled.

**Step 2: Confirm whether the 16.2 native sender serializes those bytes on the rich path**

Run:
```bash
sed -n '360,545p' analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java
```

Expected: the `32774` sender copies maneuver/lanes/text/road info only, not `f20729c`.

**Step 3: Confirm whether the bytes are still consumed on any legacy path**

Run:
```bash
sed -n '790,815p' analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java
```

Expected: `navigationStep2.f20729c` is still passed into `mo18767n(...)`; document this as evidence of a still-existing internal legacy image input, not proof of an active modern wire path.

**Step 4: Update the Evidence Ledger**

Advance `Q4` to `Needs better evidence` or `Rejected` only if the sender graph is sufficiently closed.

**Step 5: Refresh `Resume Here`, append handoff, commit**

```bash
git add docs/plans/2026-03-13-nav-image-evidence-plan.md docs/session-handoffs.md
git commit -m "docs(nav): checkpoint 16.2 app-side turn-image path"
```

---

### Task 7: Hunt the 16.2 `NEXT_TURN_IMAGE` / image-negotiation path

**Files:**
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java`
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/ian.java`
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/*.java` (search only)
- Verify: `oaa/navigation/NavigationTypeEnum.proto`
- Verify: `oaa/navigation/NavigationImageOptionsData.proto`
- Modify: `docs/plans/2026-03-13-nav-image-evidence-plan.md`
- Modify: `docs/session-handoffs.md`

**Step 1: Search for `NEXT_TURN_IMAGE` and image-option transport references**

Run:
```bash
rg -n "NEXT_TURN_IMAGE|NavigationImageOptions|colour_depth|turnImage|nextTurnImage" analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000 -g '*.java'
```

Expected: either a reachable transport/config path or a sharply bounded set of dead-end references.

**Step 2: Search for nav-channel message IDs beyond the documented semantic path**

Run:
```bash
rg -n "32772|32773|32774|32775|32776|0x8004|0x8005|0x8006|0x8007|0x8008" analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000 -g '*.java'
```

Expected: enough evidence to say whether a hidden image-bearing sender is still reachable.

**Step 3: Document exhausted search paths**

If no sender is found, record the exact files/symbols searched before leaving the question open.

**Step 4: Update the Evidence Ledger**

Advance `Q4` and `Q5` only as far as the evidence allows.

**Step 5: Refresh `Resume Here`, append handoff, commit**

```bash
git add docs/plans/2026-03-13-nav-image-evidence-plan.md docs/session-handoffs.md
git commit -m "docs(nav): checkpoint 16.2 NEXT_TURN_IMAGE search"
```

---

### Task 8: Separate projected-UI image assets from native-wire payloads in 16.2

**Files:**
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/Maneuver.java`
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/Step.java`
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/RoutingInfo.java`
- Verify: `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/jbl.java`
- Modify: `docs/plans/2026-03-13-nav-image-evidence-plan.md`
- Modify: `docs/session-handoffs.md`

**Step 1: Confirm projected model image fields**

Run:
```bash
sed -n '55,120p' analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/Maneuver.java
sed -n '1,90p' analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/Step.java
sed -n '1,80p' analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/RoutingInfo.java
```

Expected: `Maneuver.icon`, `Step.lanesImage`, and `RoutingInfo.junctionImage` are present as `CarIcon` fields.

**Step 2: Confirm projected UI consumption**

Run:
```bash
sed -n '540,600p' analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/jbl.java
```

Expected: UI code consumes `junctionImage`, `lanesImage`, and `maneuver.getIcon()`.

**Step 3: Record the distinction**

Update the ledger notes for `Q6` with whether this is projected-only evidence or native-wire evidence.

**Step 4: Refresh `Resume Here`, append handoff, commit**

```bash
git add docs/plans/2026-03-13-nav-image-evidence-plan.md docs/session-handoffs.md
git commit -m "docs(nav): checkpoint projected-ui image assets vs native wire"
```

---

### Task 9: Build the 16.1 vs 16.2 delta map and close open questions

**Files:**
- Modify: `docs/plans/2026-03-13-nav-image-evidence-plan.md`
- Modify: `docs/session-handoffs.md`

**Step 1: Add a cross-version matrix to this plan**

Include rows for:
- app-side `NavigationStep.turnImage`
- semantic rich sender
- legacy image-bearing sender
- local fallback image generation
- `NEXT_TURN_IMAGE`
- projected-only `CarIcon` assets
- native-wire lane/junction/turn image payloads

**Step 2: Set final statuses for `Q1` through `Q8`**

Do not force closure on anything still weakly evidenced.

**Step 3: Refresh `Resume Here`**

Point it at Task 10 if canonical repo docs now need updates, or state that execution is complete if no repo changes are warranted.

**Step 4: Append a handoff checkpoint and commit**

```bash
git add docs/plans/2026-03-13-nav-image-evidence-plan.md docs/session-handoffs.md
git commit -m "docs(nav): add cross-version nav image evidence matrix"
```

---

### Task 10: Update canonical repo docs only after claims are closed

**Files:**
- Modify: `docs/channels/nav.md`
- Modify: `oaa/navigation/NavigationTurnEventMessage.proto`
- Modify: `oaa/navigation/NavigationNotificationMessage.proto`
- Modify: `oaa/navigation/InstrumentClusterMessages.proto`
- Modify: `docs/session-handoffs.md`

**Step 1: Identify only source-backed claim changes**

Run:
```bash
rg -n "NEXT_TURN_IMAGE|turn_icon|junctionImage|lanesImage|Visual Payloads" docs/channels/nav.md oaa/navigation
```

Expected: a bounded list of places where the canonical docs/comments need updates.

**Step 2: Apply minimal doc/comment changes**

Only update claims that the execution evidence closed.

**Step 3: Run documentation verification**

Run:
```bash
git diff --check
rg -n "NEXT_TURN_IMAGE|turn_icon|junctionImage|lanesImage|32772|32774" docs/channels/nav.md oaa/navigation
```

Expected: no diff-format errors and updated claims present.

**Step 4: Append the final handoff checkpoint**

Record:
- what changed
- why
- final status of open questions
- follow-up work, if any

**Step 5: Commit**

```bash
git add docs/channels/nav.md oaa/navigation/NavigationTurnEventMessage.proto \
        oaa/navigation/NavigationNotificationMessage.proto \
        oaa/navigation/InstrumentClusterMessages.proto \
        docs/session-handoffs.md
git commit -m "docs(nav): update canonical nav image evidence claims"
```
