# Technology Stack

**Analysis Date:** 2026-03-02

## Languages

**Primary:**
- Protocol Buffers (proto3, proto2) - Protocol definitions for Android Auto communication
- Python 3 - Analysis and validation tools
- Markdown - Documentation and protocol reference

**Secondary:**
- Java - Target for decompilation analysis (Android Auto APK)
- Bash - Build and utility scripts

## Runtime

**Environment:**
- Python 3.x (interpreter for analysis tools)
- protoc (Protocol Buffer compiler)

**Package Manager:**
- pip (Python package management)
- No lockfile committed (tools use standard library + google-protobuf)

## Frameworks

**Core:**
- Protocol Buffers (protoc compiler) - Message serialization and schema definition

**Testing:**
- pytest - Unit testing framework for analysis tools
- Located: `analysis/tools/proto_stream_validator/tests/`, `analysis/tools/proto_schema_validator/tests/`

**Build/Dev:**
- protoc - Protocol buffer compiler for C++, Python, Go code generation
- CMake support provided for C++ integration (see README.md examples)

## Key Dependencies

**Critical:**
- `google.protobuf` - Python runtime for protobuf descriptor pool and message decoding
  - Used in: `analysis/tools/proto_stream_validator/descriptors.py`
  - Loaded dynamically with fallback error messaging
- `protoc` (system binary) - Required for compiling `.proto` files to descriptor sets

**Infrastructure:**
- sqlite3 - Standard library, used for APK analysis database queries
  - Database: `analysis/database/apk_index.db` (155MB, v16.1)
  - Database: `analysis/android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db` (90MB, v16.2)

## Configuration

**Environment:**
- No .env files required
- Repository assumes local protoc installation (`shutil.which("protoc")` check in `descriptors.py`)
- APK databases are pre-built and committed (no runtime generation)

**Build:**
- proto path configuration: repository root (e.g., `protoc --proto_path=. oaa/...`)
- descriptor set output: temporary directory (e.g., `/tmp` in tests, configurable via CLI)
- C++ compile example: `protoc --proto_path=. --cpp_out=/tmp oaa/<category>/File.proto`

## Platform Requirements

**Development:**
- Python 3.x installed
- protoc (Protocol Buffer compiler) in PATH
- sqlite3 (standard library)
- bash

**Production:**
- Repository serves as protocol definition layer for implementations
- Consuming projects (e.g., OpenAuto Prodigy) will compile protos for their target language/platform
- Pre-built SQLite indexes available for analysis without runtime setup

## Data Sources & Formats

**Proto Files:**
- 164 `.proto` files across 13 categories under `oaa/`
- Organized by service domain: common, control, av, video, audio, input, sensor, bluetooth, wifi, navigation, phone, media, notification
- Package namespaces: `oaa.proto.messages`, `oaa.proto.data`, `oaa.proto.enums`, `oaa.proto.ids`

**APK Analysis Artifacts:**
- Decompiled APK: `analysis/aa-16.2/jadx-output/` (decompiled via jadx 1.5.1)
- Indexed databases: SQLite with signal extraction (UUIDs, constants, proto accesses, enum maps, switch maps, call edges)
- Captures: JSONL format with hex-encoded protobuf frames (stored in `analysis/baselines/` and `captures/`)

**Documentation:**
- Protocol reference: `docs/protocol-reference.md` (auto-generated from proto analysis)
- Cross-reference: `docs/protocol-cross-reference.md` (APK ↔ firmware mapping)
- Implementation guides: `docs/*.md` (Bluetooth, video, resolution, rendering, debugging)

---

*Stack analysis: 2026-03-02*
