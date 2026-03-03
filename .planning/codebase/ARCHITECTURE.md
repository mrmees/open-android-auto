# Architecture

**Analysis Date:** 2026-03-02

## Pattern Overview

**Overall:** Protocol Reference & Reverse Engineering Repository

This is a multi-layered repository serving as the canonical protocol definition library for the Android Auto protocol. It contains:

1. **Protocol Definitions Layer** — 164 `.proto` files organized into 13 service categories
2. **Documentation Layer** — Protocol overviews, implementation guides, and cross-reference docs
3. **Analysis Tooling Layer** — Python-based APK indexing and proto validation against recorded captures
4. **Research Archive Layer** — Reverse-engineering source material and firmware decompilation analysis

**Key Characteristics:**
- Protobuf-centric (proto2/proto3 syntax)
- Multi-package namespace organization (messages, data, enums, ids)
- APK-driven reverse engineering (jadx decompiled sources, SQLite indexing)
- Verification-first workflow (baseline capture validation, schema regression testing)
- Non-executable reference library (consumed by OpenAuto Prodigy head unit implementation)

## Layers

**Protocol Definition Layer:**
- Purpose: Define the Android Auto wire protocol in portable protobuf format
- Location: `oaa/`
- Contains: 164 `.proto` files across 13 categories (control, audio, video, input, sensor, navigation, etc.)
- Depends on: Protobuf compiler (protoc 3.x+)
- Used by: OpenAuto Prodigy C++ implementation, validation tools, documentation generators

**APK Analysis & Indexing Layer:**
- Purpose: Extract protocol-relevant signals from decompiled Android Auto APK binaries to validate proto definitions
- Location: `analysis/tools/apk_indexer/`, `analysis/tools/proto_triage/`
- Contains: Python indexing scripts, SQLite schema definitions, static signal extractors
- Depends on: Decompiled APK source (jadx), Python 3.x, SQLite
- Used by: Proto triage scoring, class mapping validation, cross-version regression detection

**Proto Validation & Testing Layer:**
- Purpose: Validate proto schema changes against recorded wireless captures
- Location: `analysis/tools/proto_stream_validator/`
- Contains: Capture format parsers, baseline comparison logic, explicit blessing system
- Depends on: Pre-recorded capture logs, protobuf definitions
- Used by: CI/CD verification, schema regression prevention

**Documentation Layer:**
- Purpose: Explain the AA protocol to implementers with implementation guidance
- Location: `docs/`
- Contains: Protocol overviews, channel maps, implementation guides, troubleshooting, decompiled firmware analysis
- Depends on: Proto definitions (for cross-references), capture findings
- Used by: Head unit implementers, reverse engineers, protocol researchers

**Research Archive Layer:**
- Purpose: Preserve reverse-engineering source material and analytical artifacts
- Location: `research/archive/`, analysis/reports/
- Contains: APK deep-dive docs, proto validation milestones, capture findings, vendor firmware analysis
- Depends on: Historical decompilation data, capture sessions, proto triage outputs
- Used by: Future researchers, audit trail, historical context

## Data Flow

**Proto Definition Workflow:**

1. Reverse engineer Android Auto APK (jadx decompilation)
2. Extract protocol signals via `apk_indexer` → SQLite + JSON indexes
3. Triage unknown classes via `proto_triage` using BFS/hub/package/structural signals
4. Map obfuscated classes to wire-relevant proto messages via class mappings
5. Write proto files with APK class cross-references and field-level annotations
6. Validate against recorded captures via `proto_stream_validator`
7. Commit proto definitions + bless any schema changes in docs/session-handoffs.md

**Verification Workflow:**

1. User modifies `.proto` files or tools
2. Runs verification commands (protoc compilation, proto_stream_validator against baselines)
3. Records verification evidence in docs/session-handoffs.md
4. Commits with handoff entry documenting what changed, why, and verification results

**State Management:**
- Proto definitions are versioned in git and consumed as immutable by downstream projects
- Analysis results (SQLite indexes, reports) are generated and cached locally (not committed to main repo)
- Capture baselines (`analysis/baselines/`) are committed for regression validation
- Class mappings (`class_mapping.yaml`) are maintained separately to track obfuscation → proto bindings

## Key Abstractions

**Proto Package System:**
- Purpose: Organize message definitions by namespace and reusability
- Examples: `oaa.proto.messages`, `oaa.proto.data`, `oaa.proto.enums`, `oaa.proto.ids`
- Pattern: File suffixes map to package:
  - `*Message.proto` → `oaa.proto.messages` (request/response/indication messages)
  - `*Data.proto` → `oaa.proto.data` (structured data types and payloads)
  - `*Enum.proto` → `oaa.proto.enums` (enumeration definitions)
  - `*IdsEnum.proto` → `oaa.proto.ids` (channel-specific message ID enums)

**Channel Architecture:**
- Purpose: Multiplex different AA services (video, audio, sensors, input) over single TCP connection
- Examples: Channel 0 (control), Channel 1 (video), Channel 4 (media audio), Channel 7 (input), Channel 19 (sensors)
- Pattern: Each channel has lifecycle (open → setup → start → data exchange → stop → close) and specific message ID ranges (e.g., radio = 0x801A–0x8023)

**APK Analysis Indexes:**
- Purpose: Bridge obfuscated APK classes to protocol definitions
- Examples:
  - `proto_accesses` table: file, line, accessor method (which field is being read/written)
  - `enum_maps` table: class name, int value, human name (switch-statement mappings)
  - `call_edges` table: caller → callee method chains (dependency tracing)
- Pattern: Regex-based static extraction from decompiled Java source

**Verification Baseline System:**
- Purpose: Detect proto schema regressions against historical captures
- Examples: `analysis/baselines/` contains locked capture files
- Pattern: Record capture → parse with current protos → lock baseline → future runs compare against locked baseline
- Explicit "bless" mechanism allows intentional schema changes with documented reason

## Entry Points

**Proto Compilation (Library User):**
- Location: `oaa/` proto files
- Triggers: Include in CMake/cargo/gradle build; compile with protoc
- Responsibilities: Define wire protocol contracts for language-specific code generation

**APK Analysis Pipeline (Reverse Engineer):**
- Location: `analysis/tools/apk_indexer/run_indexer.py`
- Triggers: Manual or CI when APK version changes
- Responsibilities:
  - Decompile APK with jadx
  - Index signals (UUIDs, constants, enum maps, switch maps, proto accesses, call edges)
  - Write SQLite + JSON outputs for triage tools

**Proto Triage Scoring (Class Mapper):**
- Location: `analysis/tools/proto_triage/run.py`
- Triggers: After apk_indexer completes, feeds into class_mapping.yaml updates
- Responsibilities:
  - Load seeds (known mapped classes)
  - Score unmapped classes using 4-signal BFS/hub/package/structural scoring
  - Generate markdown report with candidates for manual review

**Proto Validation (CI/Gatekeeper):**
- Location: `analysis/tools/proto_stream_validator/` (not currently in CI)
- Triggers: Proto file changes, capture updates
- Responsibilities:
  - Load baseline captures
  - Decode with current proto definitions
  - Compare against locked baseline output
  - Report regressions or accept with explicit bless

**Documentation Entry Points:**
- `docs/protocol-overview.md`: High-level protocol architecture for implementers
- `docs/channel-map.md`: Channel ID, message type, and data flow table
- `docs/protocol-reference.md`: Auto-generated message catalog (80 messages, 8 enums)
- `docs/interactions/`: Detailed step-by-step session lifecycle and message sequences
- `docs/field-notes.md`: Implementation gotchas and hard-won knowledge

## Error Handling

**Strategy:** Defensive against unknown/future protocol changes

**Patterns:**
- Unknown protobuf fields are silently ignored by proto3 (forward compatibility)
- Out-of-range enum values are treated as unrecognized
- Missing optional fields default to zero/empty (no errors thrown)
- Capture validation uses baseline locking + explicit blessing for intentional deviations
- APK indexing extracts conservative signals; ambiguous matches are marked as "low confidence"

## Cross-Cutting Concerns

**Logging:** Capture findings documented in `docs/session-handoffs.md` (append-only session continuity log)

**Validation:** Verification commands recorded in session handoff before claiming completion (protoc compilation, pytest, proto_stream_validator runs)

**Authentication:** Not applicable (reference library, no runtime execution)

**Version Management:** APK versions tracked in analysis folder naming (e.g., `android_auto_16.1.660414-release_161660414`)

---

*Architecture analysis: 2026-03-02*
