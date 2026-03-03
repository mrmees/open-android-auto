# Codebase Structure

**Analysis Date:** 2026-03-02

## Directory Layout

```
open-android-auto/
├── oaa/                               # Proto definitions (164 files, 13 categories)
│   ├── audio/                         # Audio channel (7 files)
│   ├── av/                            # Audio/Video setup messages (15 files)
│   ├── bluetooth/                     # Bluetooth pairing/discovery (7 files)
│   ├── carcontrol/                    # Vehicle control channel (GAL) — new in 16.2
│   ├── common/                        # Shared enums, status codes, base types (11 files)
│   ├── control/                       # Session lifecycle: discovery, auth, channel open/close (20 files)
│   ├── generic/                       # Generic service messages
│   ├── input/                         # Input channel: touch, buttons, haptics (20 files)
│   ├── media/                         # Media playback status and metadata (3 files)
│   ├── navigation/                    # Navigation: turn events, lane guidance (14 files)
│   ├── notification/                  # Notifications (2 files)
│   ├── phone/                         # Phone status and voice session (5 files)
│   ├── radio/                         # Radio channel (GAL service 15) — new discovery
│   ├── sensor/                        # Sensors: GPS, HVAC, fuel, gear, night mode, EV (33 files)
│   ├── video/                         # Video channel: resolution, FPS, focus, display config (9 files)
│   └── wifi/                          # WiFi projection: security, handoff, versioning (18 files)
│
├── docs/                              # Implementation and protocol documentation (40+ files)
│   ├── protocol-overview.md           # High-level protocol architecture
│   ├── protocol-reference.md          # Auto-generated message catalog (36KB)
│   ├── protocol-cross-reference.md    # Phone-side APK ↔ wire protocol mapping (30KB)
│   ├── channel-map.md                 # Channel IDs, message types, data flow directions
│   ├── field-notes.md                 # Implementation gotchas and hard-won knowledge
│   ├── video-resolution.md            # Resolution negotiation and margin support
│   ├── display-rendering.md           # Rendering AA video on non-standard displays (13KB)
│   ├── wireless-bluetooth-setup.md    # Bluetooth discovery, SDP, WiFi handoff (12KB)
│   ├── phone-side-debug.md            # Debugging from phone perspective (31KB)
│   ├── troubleshooting.md             # Failure modes and diagnostics (17KB)
│   ├── roadmap-current.md             # Now/Next/Later priorities
│   ├── session-handoffs.md            # Append-only continuity log (42KB)
│   ├── interactions/                  # Detailed step-by-step sequences
│   │   ├── 01-transport-setup.md      # Bluetooth + WiFi + TCP + SSL
│   │   ├── 02-version-ssl-auth.md     # Version exchange, SSL handshake, authentication
│   │   ├── 03-service-discovery.md    # Service discovery request/response
│   │   └── 04-channel-lifecycle.md    # Channel open/setup/start/stop/close
│   ├── decompiled_headunit_firmware/  # Vendor-specific firmware analysis
│   │   ├── alpine-halo9.md
│   │   ├── alpine-ilx-w650bt.md
│   │   ├── kenwood-dnx.md
│   │   ├── pioneer-dmh.md
│   │   └── sony-xav.md
│   └── images/                        # Diagrams and protocol flow illustrations
│
├── analysis/                          # APK decompilation, indexing, validation (1.5GB+)
│   ├── tools/                         # Analysis tooling (Python)
│   │   ├── apk_indexer/               # Static signal extraction from decompiled APK
│   │   │   ├── run_indexer.py         # Main entry point
│   │   │   ├── extract.py             # File parser and regex-based extraction
│   │   │   ├── write_sqlite.py        # SQLite schema + write logic
│   │   │   ├── write_json.py          # JSON output
│   │   │   ├── catalog.py             # Catalog builder (UUID, constant lookup)
│   │   │   ├── confidence.py          # Confidence scoring for signals
│   │   │   ├── report.py              # Markdown report generation
│   │   │   ├── Makefile               # Build automation
│   │   │   ├── README.md              # Detailed usage and query examples
│   │   │   ├── sql/                   # SQLite schema definitions
│   │   │   └── tests/                 # Unit tests
│   │   ├── proto_triage/              # Class mapping scorer
│   │   │   ├── run.py                 # CLI entry point
│   │   │   ├── db.py                  # Database loaders
│   │   │   ├── signals.py             # 4-signal BFS/hub/package/structural scoring
│   │   │   ├── score.py               # Scoring aggregation and categorization
│   │   │   └── report.py              # Markdown report generator
│   │   ├── proto_stream_validator/    # Capture-based proto validation
│   │   │   ├── run.py                 # Capture decoder + baseline comparison
│   │   │   ├── validate.py            # Comparison logic and bless system
│   │   │   └── README.md              # Capture format and usage
│   │   └── proto_schema_validator/    # (Utility, light usage)
│   │
│   ├── baselines/                     # Locked capture baselines for regression testing
│   │
│   ├── captures/                      # Recorded session captures (aa-logcat tool output)
│   │   └── aa-capture_2026-03-01_14-02-27.* (JSON metadata + logcat)
│   │
│   ├── reports/                       # Generated analysis outputs
│   │   ├── proto-triage.md            # 98KB candidate scoring report
│   │   ├── validation-report.md       # Schema validation findings
│   │   └── validation-report-l1.md    # Level-1 validation summary
│   │
│   ├── aa-15.9/, aa-16.2/            # APK decompile outputs (jadx, 247–255MB each)
│   │   ├── jadx-output/
│   │   └── apkm-contents/
│   │
│   ├── android_auto_16.1.660414-release_161660414/     # Indexed APK v16.1
│   │   ├── apk-source/                # Relocated decompiled source
│   │   └── apk-index/
│   │       ├── sqlite/apk_index.db    # 155MB SQLite index
│   │       └── json/                  # JSON exports (uuids, constants, proto_accesses, etc.)
│   │
│   ├── android_auto_16.2.660604-release_162660604/     # Indexed APK v16.2
│   │   ├── apk-source/
│   │   └── apk-index/
│   │       ├── sqlite/apk_index.db    # 90MB SQLite index
│   │       └── json/
│   │
│   ├── database/                      # Legacy database (v16.1, 156MB)
│   │   └── apk_index.db
│   │
│   ├── gal-protocol-reference.md      # GAL (car control) channel deep-dive
│   │
│   └── README.md                      # Analysis tools overview
│
├── research/                          # Reverse-engineering source material archive
│   ├── archive/                       # Imported from openauto-prodigy + community repos
│   │   └── openauto-prodigy/          # Deep-dive docs, captures, tools (for reference)
│   ├── README.md                      # Archive navigation guide
│   └── provenance.md                  # Source snapshot and import scope
│
├── implementations/                   # Reference implementations
│   ├── qt/                            # Qt-based head unit example (stub)
│   └── README.md                      # Implementation guidance notes
│
├── captures/                          # Session capture outputs (aa-capture tool)
│   └── aa-capture_2026-03-01_14-02-27.* (Recent capture metadata)
│
├── .planning/                         # GSD planning metadata
│   └── codebase/                      # Codebase analysis documents
│       ├── ARCHITECTURE.md
│       └── STRUCTURE.md
│
├── .worktrees/                        # Git worktree checkouts (proto-stream-validator research branch)
│
├── temp/                              # Temporary working files
│
├── AGENTS.md                          # Workflow loop and verification rules
├── CONTRIBUTING.md                    # Contribution guidelines
├── README.md                          # Main repository overview
├── LICENSE                            # GPLv3
└── tools.yaml                         # Tool definitions (26KB)
```

## Directory Purposes

**oaa/ (Proto Definitions):**
- Purpose: Portable protocol buffer definitions for the Android Auto protocol
- Contains: 164 `.proto` files organized by channel/service type
- Key files: `oaa/control/ServiceDiscoveryRequestMessage.proto`, `oaa/sensor/SensorEventIndicationMessage.proto`
- Import style: `import "oaa/category/FileName.proto"` (category-based paths)

**docs/ (Implementation Documentation):**
- Purpose: Protocol explanation and implementation guidance for developers
- Contains: Protocol overview, implementation guides, cross-references, troubleshooting
- Key files: `protocol-overview.md` (architecture), `channel-map.md` (channel layout), `protocol-reference.md` (auto-generated catalog)
- Generated: `protocol-reference.md` comes from proto definitions

**analysis/tools/ (Python Analysis Tooling):**
- Purpose: Extract protocol signals from decompiled APK and validate proto definitions
- Contains: apk_indexer (decompile → SQLite indexing), proto_triage (scoring), proto_stream_validator (capture validation)
- Key scripts:
  - `apk_indexer/run_indexer.py`: Main indexing pipeline
  - `proto_triage/run.py`: Class mapping scorer (uses SQLite, outputs markdown report)
  - `proto_stream_validator/run.py`: Capture validator (baseline regression detection)

**analysis/baselines/ (Verification Data):**
- Purpose: Locked capture baselines for proto schema regression testing
- Contains: Pre-recorded captures that serve as golden truth
- Committed: Yes (part of CI/verification)

**analysis/reports/ (Analysis Outputs):**
- Purpose: Generated markdown reports from tools
- Contains: `proto-triage.md` (98KB candidate scoring), `validation-report.md` (schema validation findings)
- Generated: Not committed; regenerated per session

**analysis/ (APK Decompiles):**
- Purpose: Store decompiled APK sources and their indexed data
- Folders: `aa-15.9/`, `aa-16.2/` (jadx outputs), `android_auto_16.1.660414-release_161660414/` (indexed with SQLite)
- Not committed: Decompiles and large SQLite DBs are local artifacts only

**research/archive/ (Reverse-Engineering Context):**
- Purpose: Preserve historical reverse-engineering docs, proofs, and vendor analysis
- Contains: Imported openauto-prodigy docs and openauto-pro-community analysis
- Committed: Yes (reference material)

## Key File Locations

**Entry Points:**
- `oaa/` — Where to include proto definitions in your build
- `docs/protocol-overview.md` — Start here for protocol concepts
- `analysis/tools/apk_indexer/run_indexer.py` — Decompile → index pipeline
- `analysis/tools/proto_triage/run.py` — Class mapping scorer

**Configuration:**
- `AGENTS.md` — Workflow rules and verification requirements
- `CONTRIBUTING.md` — Contribution guidelines
- `tools.yaml` — Tool metadata and availability

**Core Logic:**
- `docs/interactions/` — Detailed message sequences (session lifecycle)
- `analysis/tools/apk_indexer/extract.py` — Signal extraction patterns
- `analysis/tools/proto_triage/signals.py` — BFS/hub/package/structural scoring

**Testing/Verification:**
- `analysis/baselines/` — Locked captures for regression testing
- `analysis/tools/apk_indexer/tests/` — Unit tests for indexer
- `analysis/reports/` — Generated validation outputs

**Decompiled Data (Local Only):**
- `analysis/android_auto_16.1.660414-release_161660414/apk-index/sqlite/apk_index.db` — 155MB SQLite v16.1
- `analysis/android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db` — 90MB SQLite v16.2

## Naming Conventions

**Proto Files:**
- `*Message.proto` → `ServiceDiscoveryRequestMessage.proto`, `ChannelOpenRequestMessage.proto`
  - Imports into: `oaa.proto.messages`
  - Use: Request/response/indication messages (active behavior)
- `*Data.proto` → `VideoConfigData.proto`, `GPSLocationData.proto`
  - Imports into: `oaa.proto.data`
  - Use: Structured data types (passive payloads)
- `*Enum.proto` → `StatusEnum.proto`, `ChannelTypeEnum.proto`
  - Imports into: `oaa.proto.enums`
  - Use: Enumeration definitions
- `*IdsEnum.proto` → `VideoMessageIdsEnum.proto`, `SensorMessageIdsEnum.proto`
  - Imports into: `oaa.proto.ids`
  - Use: Channel-specific message ID ranges

**Directories:**
- Category-based: `audio/`, `video/`, `input/`, `sensor/` etc. (correspond to AA channels)
- Tool directories: `tools/apk_indexer/`, `tools/proto_triage/` (snake_case)
- Analysis outputs: `analysis/reports/`, `analysis/baselines/` (plural)
- Version-keyed: `android_auto_16.1.660414-release_161660414/` (APK version code)

## Where to Add New Code

**New Proto Message:**
- Create in appropriate category: `oaa/video/MyNewMessage.proto` (or `oaa/sensor/` if sensor)
- Use correct suffix: `*Message.proto` for messages, `*Data.proto` for payloads
- Package: `package oaa.proto.messages;` (or `oaa.proto.data` for data types)
- Add imports at top of proto file with existing examples
- Add file path reference to documentation (README.md or protocol-reference.md)

**New Analysis Tool:**
- Create Python module: `analysis/tools/my_tool/run.py` (entry point)
- Include `README.md` with usage examples
- Add CLI args and help text (use argparse)
- Include unit tests in `tests/` subdirectory
- Register in `tools.yaml` if user-callable

**New Documentation:**
- Protocol/implementation guides: `docs/my-guide.md`
- Step-by-step sequences: `docs/interactions/05-my-sequence.md` (numbered)
- Session continuity: Append to `docs/session-handoffs.md` (append-only)
- Generated reference: Regenerate `protocol-reference.md` (auto-generated)

**Utilities/Helpers:**
- Shared Python utilities: `analysis/tools/` (can be used across tools)
- SQL queries: `analysis/tools/apk_indexer/sql/` (schema definitions)
- Test fixtures: `analysis/tools/*/tests/` (per-tool test data)

## Special Directories

**analysis/baselines/:**
- Purpose: Locked capture baselines for regression testing
- Generated: No (manually curated)
- Committed: Yes (critical for CI/verification)
- Usage: Proto stream validator compares decode output against these

**analysis/reports/:**
- Purpose: Generated outputs from analysis tools
- Generated: Yes (by apk_indexer, proto_triage, proto_stream_validator)
- Committed: No (regenerated per session)

**analysis/android_auto_X.Y.Z/ (Decompile Folders):**
- Purpose: Store versioned APK decompiles and their indexed data
- Generated: Yes (manually via jadx decompilation + indexer)
- Committed: No (too large for git; regenerate locally)

**research/archive/:**
- Purpose: Reference material imported from openauto-prodigy and community repos
- Generated: No (static import)
- Committed: Yes (historical context)

**.planning/codebase/:**
- Purpose: GSD codebase analysis documents (ARCHITECTURE.md, STRUCTURE.md, etc.)
- Generated: Yes (by gsd-map-codebase orchestrator)
- Committed: Yes (part of planning context)

---

*Structure analysis: 2026-03-02*
