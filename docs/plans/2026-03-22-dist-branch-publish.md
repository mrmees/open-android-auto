# Dist Branch Publish Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create and publish a minimal `dist` branch that ships only consumable `oaa/**/*.proto` files plus root `README.md` and `LICENSE`, and add a tag-triggered GitHub Actions workflow that keeps `dist` synchronized from `main`.

**Architecture:** Build `dist` as an orphan branch so consumers get a minimal tree with no research-history baggage. Maintain the branch from `main` through a release-triggered workflow that reconstructs the allowed file set in a separate checkout and only pushes when the tree changed.

**Tech Stack:** git, GitHub Actions, bash, protoc

---

### Task 1: Capture planning context

**Files:**
- Create: `docs/plans/2026-03-22-dist-branch-design.md`
- Create: `docs/plans/2026-03-22-dist-branch-publish.md`

**Step 1: Save the approved design**

Write the approved dist-branch design to:

- `docs/plans/2026-03-22-dist-branch-design.md`

**Step 2: Save the execution plan**

Write this implementation plan to:

- `docs/plans/2026-03-22-dist-branch-publish.md`

**Step 3: Verify docs exist**

Run:

```bash
test -f docs/plans/2026-03-22-dist-branch-design.md && \
test -f docs/plans/2026-03-22-dist-branch-publish.md
```

Expected: exit 0

### Task 2: Create the distribution branch

**Files:**
- Create: orphan branch `dist`
- Add: `oaa/**/*.proto`
- Add: `README.md`
- Add: `LICENSE`

**Step 1: Create a fresh orphan branch**

Run:

```bash
git switch --orphan dist
```

Expected: orphan branch created with no commits checked out.

**Step 2: Remove inherited tracked files from the index/worktree**

Run:

```bash
git rm -rf --cached .
find . -mindepth 1 -maxdepth 1 \
  ! -name .git \
  ! -name .github \
  -exec rm -rf {} +
```

Expected: empty worktree except git metadata.

**Step 3: Restore only allowed files from `feat/dist-publish`**

Run:

```bash
git checkout feat/dist-publish -- README.md LICENSE
mkdir -p oaa
find ../feat-dist-publish/oaa -name '*.proto' -print
```

Then copy only `.proto` files into the orphan tree, preserving directories.

Expected: `oaa/` contains only `.proto`; root contains optional `README.md` and
`LICENSE`.

**Step 4: Commit the dist branch**

Run:

```bash
git add README.md LICENSE oaa
git commit -m "dist: publish consumable proto definitions"
```

Expected: first commit on `dist` contains only the distribution payload.

**Step 5: Push the branch**

Run:

```bash
git push -u origin dist
```

Expected: remote `dist` branch created or updated.

### Task 3: Add automated dist publishing

**Files:**
- Create: `.github/workflows/publish-dist.yml`

**Step 1: Write the workflow**

Create a workflow that:

- triggers on tags `v*`
- checks out `main`
- checks out `dist` into a second path
- replaces dist contents with `README.md`, `LICENSE`, and `oaa/**/*.proto`
- commits only when `git diff --cached --quiet` reports changes
- pushes `dist`

**Step 2: Verify workflow syntax at a sanity level**

Run:

```bash
sed -n '1,240p' .github/workflows/publish-dist.yml
```

Expected: workflow includes both checkouts, filtered copy, conditional commit,
and push.

**Step 3: Commit the workflow on the feature branch**

Run:

```bash
git add .github/workflows/publish-dist.yml docs/plans/2026-03-22-dist-branch-*.md
git commit -m "ci: publish dist branch from release tags"
```

Expected: feature branch contains workflow and planning docs.

### Task 4: Update durable project context

**Files:**
- Modify: `docs/roadmap-current.md`
- Modify: `docs/session-handoffs.md`

**Step 1: Update roadmap sequencing if needed**

Add a note that distribution/publishing cleanup was completed as part of the
current documentation-and-consumer cleanup track.

**Step 2: Append a session handoff**

Record:

- what changed
- why
- status
- next steps
- verification command results

Expected: handoff reflects both the `dist` branch publication and the workflow
added on `main`.

### Task 5: Verify the deliverable

**Files:**
- Verify: branch `dist`
- Verify: `.github/workflows/publish-dist.yml`

**Step 1: Verify dist contents**

Run:

```bash
git ls-tree -r --name-only dist
find oaa -type f ! -name '*.proto'
```

Expected: no non-proto files under `oaa`; no research/docs/tools trees.

**Step 2: Verify representative proto compilation**

Run:

```bash
mkdir -p /tmp/oaa_dist_verify
protoc --proto_path=. --cpp_out=/tmp/oaa_dist_verify \
  oaa/control/ServiceDiscoveryRequestMessage.proto \
  oaa/navigation/NavigationTurnEventMessage.proto \
  oaa/sensor/SensorEventIndicationMessage.proto
```

Expected: exit 0.

**Step 3: Verify shallow clone reduction**

Run:

```bash
tmpdir=$(mktemp -d)
git clone --depth 1 -b main https://github.com/mrmees/open-android-auto.git "$tmpdir/main"
git clone --depth 1 -b dist https://github.com/mrmees/open-android-auto.git "$tmpdir/dist"
git -C "$tmpdir/main/.git" count-objects -v
git -C "$tmpdir/dist/.git" count-objects -v
```

Expected: `dist` clone reports materially fewer loose/packed objects than
`main`.
