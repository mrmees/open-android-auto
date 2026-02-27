# Lean Workflow Setup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a lean, protocol-adapted workflow loop to this repository using `AGENTS.md`, `docs/roadmap-current.md`, and `docs/session-handoffs.md`.

**Architecture:** The workflow loop is enforced from `AGENTS.md` and backed by two operational docs: `roadmap-current` for priorities and `session-handoffs` for continuity. Verification is lightweight and repository-specific (proto/docs/tooling checks), with evidence captured in handoffs before any completion claim.

**Tech Stack:** Markdown docs, git, shell validation commands (`rg`, `protoc`, `git`).

---

### Task 1: Create `AGENTS.md` Workflow Loop

**Skills:** `@verification-before-completion`

**Files:**
- Create: `AGENTS.md`

**Step 1: Draft the workflow contract**

Write `AGENTS.md` with:
- scope note for protocol/reference repo
- 4-step project management loop
- verification baseline for proto/docs/tooling changes
- completion rule requiring verification evidence in handoffs

**Step 2: Validate required sections exist**

Run:

```bash
rg -n "Project Management Loop|Verification Baseline|Completion Rule" AGENTS.md
```

Expected: 3 matches (one for each section header).

**Step 3: Commit task**

```bash
git add AGENTS.md
git commit -m "docs: add AGENTS workflow loop for protocol repo"
```

---

### Task 2: Create `docs/roadmap-current.md`

**Files:**
- Create: `docs/roadmap-current.md`

**Step 1: Draft roadmap structure**

Write `docs/roadmap-current.md` with:
- `Now` section (active priorities)
- `Next` section (queued priorities)
- `Later` section (deferred priorities)
- `Focus Guardrails` section
- `Last Updated` line

Keep bullets concrete and scoped to protocol definitions, documentation quality, and analysis tooling.

**Step 2: Validate roadmap sections**

Run:

```bash
rg -n "^## (Now|Next|Later|Focus Guardrails)$|^Last Updated:" docs/roadmap-current.md
```

Expected: 5 matches.

**Step 3: Commit task**

```bash
git add docs/roadmap-current.md
git commit -m "docs: add current roadmap with now-next-later priorities"
```

---

### Task 3: Create `docs/session-handoffs.md` with Template and Initial Entry

**Files:**
- Create: `docs/session-handoffs.md`

**Step 1: Add handoff template**

Write an append-only template with these fields:
- Date / Session
- What Changed
- Why
- Status
- Next Steps (1-3)
- Verification

**Step 2: Add first real handoff entry**

Add an initial entry documenting the workflow setup:
- mention files added
- include why this governance was introduced
- include status and next steps
- include verification commands/results for docs-only change set

**Step 3: Validate template fields**

Run:

```bash
rg -n "^## |Date / Session|What Changed|Why|Status|Next Steps|Verification" docs/session-handoffs.md
```

Expected: template and initial entry headings are present.

**Step 4: Commit task**

```bash
git add docs/session-handoffs.md
git commit -m "docs: add session handoff log with template and initial entry"
```

---

### Task 4: Add Workflow Doc Discovery to `README.md`

**Files:**
- Modify: `README.md`

**Step 1: Add short workflow section**

Add a concise "Workflow" section near contribution/documentation guidance that points to:
- `AGENTS.md`
- `docs/roadmap-current.md`
- `docs/session-handoffs.md`

**Step 2: Verify links and references**

Run:

```bash
rg -n "AGENTS.md|docs/roadmap-current.md|docs/session-handoffs.md" README.md
```

Expected: all 3 paths are referenced.

**Step 3: Commit task**

```bash
git add README.md
git commit -m "docs: surface workflow files in README"
```

---

### Task 5: Final Verification and Consistency Pass

**Skills:** `@verification-before-completion`

**Files:**
- Verify: `AGENTS.md`
- Verify: `docs/roadmap-current.md`
- Verify: `docs/session-handoffs.md`
- Verify: `README.md`

**Step 1: Confirm files exist**

```bash
ls AGENTS.md docs/roadmap-current.md docs/session-handoffs.md
```

Expected: all files listed with exit code 0.

**Step 2: Run docs consistency checks**

```bash
rg -n "roadmap-current|session-handoffs|AGENTS.md" AGENTS.md README.md docs/roadmap-current.md docs/session-handoffs.md
```

Expected: cross-references are present and paths are correct.

**Step 3: Confirm clean git state**

```bash
git status --short
```

Expected: clean working tree.

**Step 4: Optional squash decision**

If you want a single commit for workflow bootstrap, squash now; otherwise keep granular history from Tasks 1-4.

