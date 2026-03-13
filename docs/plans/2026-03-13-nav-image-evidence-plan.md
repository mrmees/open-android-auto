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
| Q2 | 16.1 synthesizes fallback turn images locally | Confirmed | Reconfirmed from `hkx.n(...)`: if image delivery is disabled, incoming `bArr` is cleared (`hkx.java:843-845`); when bytes are still null and `this.l` (`hwl`) is present, the legacy path synthesizes fallback bytes from named `da_turn_*` assets via `hwl.a(...)`, `hwl.c.a(...)`, or generic `hwl.b()` fallback, including roundabout angle-specific assets, before serializing the result into `vzm.f` and sending `32772` (`hkx.java:846-967`, `hkx.java:1023-1033`). |
| Q3 | 16.2 rich native nav sender is semantic-only | Confirmed | Reconfirmed from 16.2 source: semantic `32774` path runs under `m18758y(mo19019r)` and builds `vza` step + destination entries before `this.f34217k.m20106k(32774, ...)` (`hlj.java:361-365`, `hlj.java:372-635`); `vza` only carries repeated `vzg` + `vyq` entries (`vza.java:12-16`, `vza.java:38-39`); `vzg` only exposes maneuver `vyw`, text `vyz`, repeated lane entries `vyv`, and road-info `vyo`, with no raw image-bytes field (`vzg.java:13-25`, `vzg.java:44-45`). |
| Q4 | 16.2 has a native image-bearing successor path | Confirmed | 16.2 keeps app-side `turnImage` bytes on `NavigationStep.f20729c` and parcels them as field `5` (`NavigationStep.java:25`, `NavigationStep.java:45`, `NavigationStep.java:82-88`); the semantic `32774` builder still ignores that field and only copies maneuver/text/lanes/road-info data into `vzg` (`hlj.java:361-545`), but post-plan fallback JADX over `classes.dex` recovered `hlj.mo18767n(...)` and showed that the legacy `m18759z(carInfo)` branch still clears bytes when `!this.g.bp()`, synthesizes `da_turn_*` fallback assets via `hwy`, builds deprecated `vyy`, writes optional image bytes into `vyy.f`, and sends native `32772` / `0x8004` (caller boundary `hlj.java:805-813`; `vyy.java:13-35`, `vyy.java:54-56`; binder interface `prt.java:72-80`; exact JADX command/result recorded in the 2026-03-13 follow-up handoff entry). |
| Q5 | `NEXT_TURN_IMAGE` is reachable in 16.2 | Rejected | Task 7 source search over 16.2 `p000/*.java` found no `NEXT_TURN_IMAGE`, `NavigationImageOptions`, or `colour_depth` references at all; the only matching terms were projected-UI `turnImage` / `nextTurnImage` names in `ggf.java:4-60`, `ggj.java:4-64`, and `ggo.java:71-77`. Post-plan fallback JADX later recovered the opaque legacy sender and showed it still uses deprecated `32772` / `0x8004` via `vyy`, not any named `NEXT_TURN_IMAGE` successor path (see the 2026-03-13 follow-up handoff entry for the exact JADX command/result). Repo proto placeholders still define `NEXT_TURN_IMAGE = 2` and `NavigationImageOptions`, but no 16.2 sender path that uses them has been found. |
| Q6 | `junctionImage` or `lanesImage` reach native nav transport in 16.2 | Rejected | In 16.2 projected navigation models, `Maneuver` stores a `CarIcon mIcon` (`Maneuver.java:60-70`, `Maneuver.java:100-101`), `Step` stores `CarIcon mLanesImage` (`Step.java:15-27`, `Step.java:49-54`), and `RoutingInfo` stores `CarIcon mJunctionImage` (`RoutingInfo.java:13-17`, `RoutingInfo.java:47-56`). Projected UI renderer `jbl` consumes those assets directly via `routingInfo.getJunctionImage()`, `currentStep.getManeuver().getIcon()`, `currentStep.getLanesImage()`, and `nextStep.getManeuver().getIcon()` (`jbl.java:548-606`). No native 16.2 sender path consumes these `CarIcon` fields: semantic `32774` stays image-free (`hlj.java:361-635`; `vzg.java:13-25`, `vzg.java:44-45`), and recovered legacy helper `mo18767n(...)` only builds `vyy` with one optional bytes field for a turn image rather than lane/junction assets (`vyy.java:13-35`, `vyy.java:54-56`; exact JADX command/result recorded in the 2026-03-13 follow-up handoff entry). |
| Q7 | Cross-version capability gates controlling nav image delivery are understood | Needs better evidence | 16.1 sender gating is source-backed: `CarInfo.e` / `f` are `headUnitProtocolMajorVersionNumber` / `headUnitProtocolMinorVersionNumber` (`ijk.java:59`); `hkx.x(carInfo)` treats HU protocol `>= 1.6` as modern (`hkx.java:47-53`); semantic `32774` uses `y(carInfo) = this.e || x(carInfo)` (`hkx.java:55-57`, `hkx.java:304-308`); legacy/image-bearing `32772` uses `z(carInfo) = !x(carInfo)` (`hkx.java:59-60`, `hkx.java:586-592`). `this.e` is injected from clustersim vendor-extension bit `poe.b` (`iny.java:323-333`, `hlw.java:8-37`). 16.2 mirrors the same threshold shape: `m18757x(carInfo)` still treats HU protocol `>= 1.6` as modern, `m18758y(carInfo) = this.f34211e || m18757x(carInfo)`, and `m18759z(carInfo) = !m18757x(carInfo)` (`hlj.java:96-110`, `hlj.java:361-365`, `hlj.java:643-645`). The unresolved piece is the exact semantic meaning/provenance of the 16.2 override bit `f34211e`, so the cross-version gate story is bounded but not fully closed. |
| Q8 | Canonical repo docs are updated only after claims close | Confirmed | Tasks 1-9 only updated the execution plan and handoff log while closing or bounding source-backed claims. Canonical repo docs/proto comments remain untouched and explicitly deferred to Task 10, where the narrowed set of now-closed claim changes can be applied minimally. |

## Resume Here

- Last completed task: `Task 10 plus post-plan fallback JADX recovery of 16.2 mo18767n(...)`
- Last verified claim: `Fallback JADX over 16.2 classes.dex recovered hlj.mo18767n(...), confirming that 16.2 still synthesizes optional legacy turn-image bytes and sends deprecated vyy on native 32772 / 0x8004 under the z(carInfo) gate`
- Evidence files:
  - `/home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java`
  - `/home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/com/google/android/gms/car/navigation/NavigationStep.java`
  - `/home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/jbl.java`
  - `/home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java`
  - `/home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/resources/classes.dex`
  - `/home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/vyy.java`
  - `/home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/prt.java`
  - `docs/session-handoffs.md`
- Next unanswered question: `What exactly does the 16.2 override bit f34211e mean, now that the legacy 32772 path itself is confirmed?`
- Next command to run: `rg -n "f34211e|poe|vendor extension|clustersim" /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000 /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage -g '*.java'`

## Cross-Version Matrix

| Topic | 16.1 | 16.2 | Notes |
|-------|------|------|-------|
| App-side `NavigationStep.turnImage` | Confirmed: `byte[] c`, parcel field `5` | Confirmed: `byte[] f20729c`, parcel field `5` | App model still retains turn-image bytes in both versions. |
| Semantic rich sender | Confirmed: `32774`, image-free `vzo` / `vzu` payload | Confirmed: `32774`, image-free `vza` / `vzg` payload | Both rich senders carry maneuver/text/lane-state/road-info data, not raw image bytes. |
| Legacy image-bearing sender | Confirmed: `32772`; `hkx.n(...)` writes bytes into `vzm.f` | Confirmed: recovered `hlj.mo18767n(...)` builds `vyy` and sends `32772` / `0x8004` | 16.2 retains the deprecated native image-bearing path behind the legacy gate. |
| Local fallback image generation | Confirmed: `hkx.n(...)` synthesizes `da_turn_*` assets locally | Confirmed: recovered `hlj.mo18767n(...)` synthesizes `da_turn_*` assets via `hwy` before building `vyy` | Both versions keep local fallback image generation on the legacy path. |
| `NEXT_TURN_IMAGE` | No source-backed 16.1 claim gathered in this batch | Rejected: no sender/config refs, only projected-UI leftovers | Repo proto placeholders exist, but no APK-backed 16.2 sender usage was found. |
| Projected-only `CarIcon` assets | Not traced in 16.1 scope | Confirmed: `Maneuver.icon`, `Step.lanesImage`, `RoutingInfo.junctionImage` feed `jbl` UI | Projected template evidence is distinct from native nav transport evidence. |
| Native-wire lane/junction/turn image payloads | Turn-image bytes confirmed on `32772`; no lane/junction payload evidence | Turn-image bytes confirmed on `32772`; no lane/junction payload evidence | Distinguishes native-wire turn images from projected UI assets. |

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
