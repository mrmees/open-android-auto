# External Integrations

**Analysis Date:** 2026-03-02

## APIs & External Services

**Android Auto Protocol:**
- Android Auto (AA) v16.1, v16.2, v15.9 APK analysis
  - Reverse-engineered via jadx decompilation
  - Protocol extracted: session control, audio/video streaming, input, sensors, navigation
  - No external API calls; protocol definitions only

**Original Sources:**
- f1x.studio aasdk (https://github.com/nicka-2/aasdk) - Foundation proto definitions
  - Upgraded from proto2 → proto3
  - Extended with field-level annotations from live captures

## Data Storage

**Databases:**
- SQLite (local file-based)
  - `analysis/database/apk_index.db` — v16.1 index (155MB)
  - `analysis/android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db` — v16.2 index (90MB)
  - Tables: uuids, constants, proto_accesses, proto_writes, enum_maps, switch_maps, call_edges, proto_classes, proto_evidence, proto_syntax
  - Python access: `sqlite3` standard library (wrapped in `analysis.tools.proto_triage.db`)

**File Storage:**
- Local filesystem only
  - Decompiled APK source: `analysis/aa-16.2/jadx-output/`
  - APK binaries: `analysis/*.apkm` files
  - Protobuf captures: `analysis/baselines/`, `captures/` (JSONL format)
  - Proto definitions: `oaa/` directory tree (164 `.proto` files)

**Caching:**
- Generated descriptor sets (protoc output) stored temporarily during test runs
- Pre-compiled descriptor sets not committed; generated on-demand via protoc

## Authentication & Identity

**Auth Provider:**
- Not applicable
- Repository is a protocol definition layer; no user authentication or service auth required

## Monitoring & Observability

**Error Tracking:**
- Not implemented
- Analysis tools emit text reports to stdout/stderr

**Logs:**
- pytest output for test runs
- Script stdout logs (analysis tools write JSON and Markdown reports)
- No persistent logging infrastructure

## CI/CD & Deployment

**Hosting:**
- GitHub repository (https://github.com/mrmees/open-android-auto)
- Repository serves as import source for downstream projects (OpenAuto Prodigy, etc.)

**CI Pipeline:**
- Not detected in this repository
- Assumes consumer projects (OpenAuto Prodigy) run their own CI with proto compilation

## Environment Configuration

**Required env vars:**
- None; repository is self-contained

**Secrets location:**
- No secrets stored
- APK binaries are public decompiled/reverse-engineered artifacts

## APK Decompilation Tooling

**Tools Used (External):**
- jadx 1.5.1 - Java decompiler (used to generate `analysis/aa-16.2/jadx-output/`)
- protoc - Protocol buffer compiler (called via subprocess in `analysis/tools/proto_stream_validator/descriptors.py`)

**Data Imported:**
- Android Auto APK v16.1.660414-release (155MB indexed DB)
- Android Auto APK v16.2.660604-release (90MB indexed DB + APKM file)
- Bluetooth UUIDs, service discovery info, channel definitions extracted from APK

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Analysis Data Dependencies

**Live Captures:**
- JSONL format protobuf stream logs (hex-encoded frames)
- Stored: `analysis/baselines/`, `captures/`
- Used for: Proto schema validation, message type mapping, regression testing

**Proto Mapping Database:**
- YAML mapping file (referenced in triage scoring)
- Maps APK obfuscated class names → proto message definitions
- Versioned across AA versions (16.1, 16.2, 15.9)

---

*Integration audit: 2026-03-02*
