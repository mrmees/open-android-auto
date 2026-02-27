# open-android-auto Repo Expansion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expand open-android-auto from proto-only into the canonical open-source Android Auto protocol reference with docs, firmware analysis, and APK tools.

**Architecture:** Copy documentation from openauto-prodigy into organized directories. Strip openauto-prodigy-specific references where needed. Add analysis tools with disclaimer. Rewrite README for expanded scope.

**Tech Stack:** Git, Markdown, Python (APK indexer), SQLite

---

### Task 1: Copy protocol documentation

**Files:**
- Create: `docs/protocol-reference.md`
- Create: `docs/video-resolution.md`
- Create: `docs/display-rendering.md`
- Create: `docs/phone-side-debug.md`
- Create: `docs/troubleshooting.md`
- Create: `docs/protocol-cross-reference.md`
- Create: `docs/wireless-bluetooth-setup.md`

**Step 1: Copy files from openauto-prodigy**

```bash
cd /home/matt/claude/personal/openautopro/open-android-auto

OAP=/home/matt/claude/personal/openautopro/openauto-prodigy/docs
ARCHIVE=$OAP/OpenAutoPro_archive_information

cp "$OAP/aa-protocol-reference.md"                    docs/protocol-reference.md
cp "$OAP/aa-video-resolution.md"                      docs/video-resolution.md
cp "$OAP/aa-display-rendering.md"                     docs/display-rendering.md
cp "$OAP/aa-phone-side-debug.md"                      docs/phone-side-debug.md
cp "$OAP/aa-troubleshooting-runbook.md"               docs/troubleshooting.md
cp "$OAP/android-auto-protocol-cross-reference.md"    docs/protocol-cross-reference.md
cp "$ARCHIVE/bluetooth-wireless-aa-setup.md"          docs/wireless-bluetooth-setup.md
```

**Step 2: Verify all 7 files landed**

Run: `ls -la docs/*.md | wc -l`
Expected: 10 (3 existing + 7 new)

**Step 3: Commit**

```bash
git add docs/
git commit -m "docs: add protocol reference, wireless BT setup, troubleshooting, and video docs"
```

---

### Task 2: Review and clean docs for standalone context

**Files:**
- Modify: All 7 new docs from Task 1

**Step 1: Review each doc for openauto-prodigy-specific references**

Scan all 7 files for references to:
- `openauto-prodigy` paths (e.g., `src/core/aa/`, `docs/skills/`)
- Internal cross-references that won't exist in this repo
- Pi-specific deployment instructions that belong in openauto-prodigy

For each reference found, decide:
- If it's a general AA protocol concept → keep it
- If it's an openauto-prodigy implementation detail → either generalize it or add a note like "Implementation-specific — see your project's docs"
- If it's a broken internal link → fix or remove

**Step 2: Make edits**

Apply minimal edits. The goal is NOT to rewrite — just fix broken references and remove project-specific paths that would confuse someone reading this standalone.

**Step 3: Commit**

```bash
git add docs/
git commit -m "docs: clean up openauto-prodigy-specific references for standalone use"
```

---

### Task 3: Add decompiled headunit firmware docs

**Files:**
- Create: `docs/decompiled_headunit_firmware/alpine-halo9.md`
- Create: `docs/decompiled_headunit_firmware/alpine-ilx-w650bt.md`
- Create: `docs/decompiled_headunit_firmware/kenwood-dnx.md`
- Create: `docs/decompiled_headunit_firmware/pioneer-dmh.md`
- Create: `docs/decompiled_headunit_firmware/sony-xav.md`

**Step 1: Create directory and copy files**

```bash
cd /home/matt/claude/personal/openautopro/open-android-auto
mkdir -p docs/decompiled_headunit_firmware

FIRMWARE=/home/matt/claude/personal/openautopro/openauto-prodigy/docs/OpenAutoPro_archive_information/firmware

cp "$FIRMWARE/alpine-halo9.md"      docs/decompiled_headunit_firmware/
cp "$FIRMWARE/alpine-ilx-w650bt.md" docs/decompiled_headunit_firmware/
cp "$FIRMWARE/kenwood-dnx.md"       docs/decompiled_headunit_firmware/
cp "$FIRMWARE/pioneer-dmh.md"       docs/decompiled_headunit_firmware/
cp "$FIRMWARE/sony-xav.md"          docs/decompiled_headunit_firmware/
```

**Step 2: Verify**

Run: `ls docs/decompiled_headunit_firmware/`
Expected: 5 .md files

**Step 3: Commit**

```bash
git add docs/decompiled_headunit_firmware/
git commit -m "docs: add decompiled headunit firmware analysis (Alpine, Kenwood, Pioneer, Sony)"
```

---

### Task 4: Add APK analysis tools and database

**Files:**
- Create: `analysis/README.md`
- Create: `analysis/tools/` (copy entire apk_indexer directory)
- Create: `analysis/database/apk_index.db`

**Step 1: Create analysis directory structure**

```bash
cd /home/matt/claude/personal/openautopro/open-android-auto
mkdir -p analysis/tools analysis/database
```

**Step 2: Copy APK indexer tools**

```bash
cp -r /home/matt/claude/personal/openautopro/openauto-prodigy/analysis/tools/apk_indexer analysis/tools/
```

**Step 3: Copy SQLite database**

```bash
cp /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-index/sqlite/apk_index.db analysis/database/
```

**Step 4: Write disclaimer README**

Create `analysis/README.md` with content:

```markdown
# Analysis Tools

These tools are included for personal development reference and have no current functionality as standalone utilities. They were used during reverse engineering of the Android Auto protocol and are provided as-is.

## Contents

### tools/apk_indexer/

Python scripts used to extract and index protocol-relevant data from the Android Auto APK (v16.1). Extracts UUIDs, constants, protobuf field accesses, enum mappings, switch maps, and call edges.

See `tools/apk_indexer/README.md` for usage details.

### database/apk_index.db

Pre-built SQLite database containing indexed data from Android Auto APK v16.1.660414-release. Key tables:

- `uuids` — Service and characteristic UUIDs
- `constants` — Named constants and their values
- `proto_accesses` — Protobuf field read/write locations
- `proto_writes` — Protobuf message construction sites
- `enum_maps` — Enum value mappings
- `switch_maps` — Switch statement case mappings
- `call_edges` — Method call graph edges

Query example:
\`\`\`sql
SELECT * FROM constants WHERE name LIKE '%CHANNEL%';
\`\`\`
```

**Step 5: Verify**

Run: `ls -la analysis/database/apk_index.db && ls analysis/tools/apk_indexer/*.py | wc -l`
Expected: DB file exists (~156MB), 8+ Python files

**Step 6: Check if Git LFS is needed for the 156MB database**

Run: `git lfs version 2>/dev/null || echo "no LFS"`

If LFS is available, track the .db file:
```bash
git lfs track "analysis/database/*.db"
git add .gitattributes
```

If LFS is NOT available, check GitHub's file size limit (100MB). If the DB exceeds it, either:
- Install git-lfs (`sudo apt install git-lfs && git lfs install`)
- Or compress: `gzip -k analysis/database/apk_index.db` and commit the .gz instead

**Step 7: Commit**

```bash
git add analysis/
git commit -m "analysis: add APK indexer tools and pre-built SQLite database"
```

---

### Task 5: Rewrite README.md

**Files:**
- Modify: `README.md`

**Step 1: Rewrite README for expanded scope**

The README should cover:
- What this repo is (canonical AA protocol reference)
- Quick links to key docs (protocol reference, wireless BT setup, channel map, troubleshooting)
- Proto file overview (164 files, 13 categories, how to use as submodule)
- Analysis tools section (with disclaimer)
- Decompiled firmware section
- Contributing link
- License (GPLv3)

**Step 2: Verify links**

Check that all relative links in the README point to files that actually exist.

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README for expanded protocol reference scope"
```

---

### Task 6: Push and verify

**Step 1: Push to GitHub**

```bash
git push origin main
```

**Step 2: Verify on GitHub**

Check https://github.com/mrmees/open-android-auto to confirm:
- README renders correctly
- All docs are accessible
- Database file uploaded (or LFS pointer if using LFS)
- No broken links in README
