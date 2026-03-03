# Codebase Concerns

**Analysis Date:** 2026-03-02

## Tech Debt

**Missing Python Package Configuration:**
- Issue: No `pyproject.toml`, `requirements.txt`, or `setup.py` at repository root
- Files: `analysis/tools/proto_stream_validator/`, `analysis/tools/proto_schema_validator/`
- Impact: Analysis tools have undocumented dependencies; difficult to reproduce environment or set up locally
- Fix approach: Create `pyproject.toml` with `[build-system]` and `[project]` sections listing dependencies (protobuf, pytest, etc.)

**Unreliable Phone Reconnection After HU Restart:**
- Issue: Phone doesn't cleanly reconnect after head unit app restart; user must manually cycle BT/WiFi
- Files: `docs/troubleshooting.md:277` (TODO marker)
- Impact: Blocks automation of test scenarios; requires manual intervention during capture/validation workflows
- Fix approach: Investigate phone-side AA graceful disconnect sequence; possibly send explicit SHUTDOWN_REQUEST or detect connection teardown more reliably

**Post-Handshake Authorization Stall (aasdk era — unvalidated):**
- Issue: Under old aasdk stack, phone completed full handshake but entered `STATE_WAITING_FOR_USER_AUTHORIZATION` and never progressed
- Files: `docs/troubleshooting.md:162,408-429`
- Impact: Session stalls indefinitely; user consent dialog never appears
- Status: Marked as "known blocker" but unvalidated under open-androidauto — needs retest
- Fix approach: Retest under current open-androidauto stack; if reproduces, investigate whether it's a cert/identity issue, SERVICE_DISCOVERY_RESPONSE completeness, or Android version-specific behavior

## Known Bugs

**Video Pixel Format Mismatch (Device-Dependent):**
- Symptoms: Black screen despite active AA session with pings flowing
- Files: `docs/troubleshooting.md:190-192`
- Trigger: Some phones output `AV_PIX_FMT_YUVJ420P` (fmt=12) instead of `AV_PIX_FMT_YUV420P` (fmt=0)
- Current mitigation: Must accept both formats or frames silently discarded
- Example: Moto G Play 2024 → YUVJ420P; Samsung S25 Ultra → YUV420P
- Workaround: Decoder must detect and handle both pixel formats

**Video Focus Request Suppression Causes Exit Signal:**
- Symptoms: Sending `VIDEO_FOCUS_INDICATION(UNFOCUSED)` causes phone to exit projection
- Files: `docs/troubleshooting.md:205-207`
- Trigger: Phone aggressively re-requests VIDEO_FOCUS_INDICATION(FOCUSED) and interprets UNFOCUSED as termination
- Current mitigation: Always respond with FOCUSED; don't suppress requests
- Fix approach: Ensure VIDEO_FOCUS_INDICATION(FOCUSED) is sent immediately after AV_SETUP_RESPONSE

**Port Bind Failure After App Restart (Socket Descriptor Inheritance):**
- Symptoms: TCP sockets not rebindable after app restart; "address already in use" error
- Files: `docs/troubleshooting.md:265-268`
- Trigger: Forked processes (restart handlers) inherit acceptor FD, preventing port rebind
- Current mitigation: Use `SO_REUSEADDR` before bind or set `SOCK_CLOEXEC` after socket open
- Fix approach: Set `fcntl(fd, F_SETFD, FD_CLOEXEC)` immediately after socket creation

**Process Name Truncation Breaks `pkill`:**
- Symptoms: `pkill` silently fails to kill process
- Files: `docs/troubleshooting.md:279-281`
- Trigger: Process names >15 characters truncated in procfs
- Current mitigation: Must use `pkill -f '<full-binary-path>'` (full command match)
- Fix approach: Use full command-line matching in kill scripts; avoid relying on binary name alone

## Fragile Areas

**APK Analysis Tools (Large Obfuscated Search Space):**
- Files: `analysis/tools/proto_stream_validator/`, `analysis/tools/proto_schema_validator/`
- Why fragile: Tools operate on obfuscated Android bytecode where class names, field IDs, and enums change between APK versions
- Dependency on: Stable fingerprinting (enum values, BFS scores, package patterns); any change to APK obfuscation strategy breaks mappings
- Safe modification: Add comprehensive regression tests matching known proto classes across multiple APK versions; store test fixtures in `analysis/tools/proto_stream_validator/tests/fixtures/`
- Test coverage: 5 test files exist but fixtures directory has limited data; expand with known good cross-version proto class mappings

**Baseline Validation with Limited Samples:**
- Files: `analysis/baselines/`, `analysis/tools/proto_stream_validator/run.py`
- Why fragile: Baseline diff validation relies on pre-computed "locked" baselines; changes to proto parsing or phone behavior cause false-positives
- Current state: Baselines exist at `analysis/baselines/` but only sparse capture data available for revalidation
- Safe modification: Before making parser changes, regenerate baseline with `--bless` and document reason; maintain separate baseline versions per APK version
- Coverage gap: Only Android 14 (Moto G Play 2024) and Android 16 (Samsung S25 Ultra) phone baseline data exists

**Proto Class Triage and Cross-Version Matching:**
- Files: `analysis/tools/proto_triage/` (mentioned in memory), `analysis/reports/proto-triage.md`
- Why fragile: Matching obfuscated class names across APK versions (16.1 → 16.2) via enum fingerprints is brittle
- Current state: 221/236 proto class mappings validated; 76 telemetry classes auto-excluded
- Safe modification: Any changes to signal-scoring algorithm (BFS, hub-file, package, structural) must be validated against all three APK versions (15.9, 16.1, 16.2)
- Coverage gap: Unknown APK version in `analysis/android_auto_unknown_unknown/` — version inference may be incorrect

## Storage & Build Concerns

**Large Uncompressed APK Files in Repository:**
- Issue: 33MB APK mirror file at `analysis/com.google.android.projection.gearhead_16.2.660604-release-162660604_1arch_7dpi_24lang_7f18983399622180da63cd9429ab8ae5_apkmirror.com(2).apkm`
- Files: `analysis/*.apkm`, `temp/com.google.android.projection.gearhead_15.9.655104-release-159655104_1arch_7dpi_24lang.apkm` (33MB)
- Impact: Bloats repository; violates `.gitignore` intent to exclude binary artifacts
- Fix approach: Remove `.apkm` files from repository and `.gitattributes` LFS filter; document download source in `analysis/README.md` instead

**Large SQLite Database Files Tracked in Git:**
- Issue: SQLite APK index databases are 90–155MB each and checked into repo
- Files: `analysis/android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db` (137MB), `.gitignore` marks these as `*.db` but they remain tracked
- Impact: Repository clones are slow; diffs are large and unreadable; `.gitattributes` LFS filter barely helps without Git LFS backend
- Fix approach: Remove existing `.db` files from git history (`git filter-branch` or `bfg`); ensure all `.db` files honor `.gitignore` exclusion; document re-indexing workflow in `analysis/README.md`

**Undocumented Cross-Version APK Version Naming:**
- Issue: Directory names use version patterns like `16.2.660604-release_162660604` but mapping between APK display version, build number, and release identifier is undocumented
- Files: `analysis/android_auto_*/`, `analysis/tools/proto_stream_validator/`
- Impact: Difficult to match captured phones to APK versions; version detection tools must guess or hardcode mappings
- Fix approach: Document version format in `analysis/README.md` with examples; add version parsing unit tests in `analysis/tools/proto_stream_validator/tests/`

## Missing Critical Features

**AA Capture Tool (aa-logcat) Logcat Access Broken on Android 13+:**
- Problem: `LogcatManagerService` (Android 13+) gates logcat behind foreground-only approval that expires when AA takes focus
- Files: `docs/plans/2026-03-01-aa-capture-tool-design.md`
- Blocks: Community-facing protocol data collection from production head units
- Status: v0.1.0 released but broken; Shizuku integration planned but not implemented
- Fix needed: Integrate Shizuku library for persistent ADB-level logcat access (reference: LogFox app via `github.com/F0x1d/LogFox`)

**AA Version Detection Returns "Not Installed":**
- Problem: `PackageManager.getPackageInfo()` returns null without proper flags
- Files: `docs/plans/2026-03-01-aa-capture-tool-design.md` (mentions "Also fix")
- Blocks: Automatic AA version detection for captured sessions
- Fix needed: Add `PackageManager.GET_META_DATA` flag to getPackageInfo call

**No Centralized Proto Descriptor Repository:**
- Problem: Analysis tools rebuild descriptor bundles from source protos; no compiled descriptor file (.pb, .descriptor) cached
- Files: `analysis/tools/proto_stream_validator/descriptors.py` (builds bundle on-demand)
- Impact: Proto decoding slow for large captures; tempfile creation overhead on each run
- Improvement path: Pre-compile descriptor file for each known APK version; cache in `analysis/descriptors/` with version tagging

## Test Coverage Gaps

**Proto Decoding Validation:**
- What's not tested: End-to-end decoding of real captured frames against known proto structures
- Files: `analysis/tools/proto_stream_validator/tests/test_decode.py` (only 40 lines, minimal fixtures)
- Risk: Silent parse failures or incorrect field interpretation when APK proto definitions change
- Priority: High — critical path for protocol discovery pipeline
- Fix approach: Expand fixtures with decoded frames from each major APK version; add assertions for known field values

**Message Map Resolution:**
- What's not tested: Cross-version message ID → message type resolution
- Files: `analysis/tools/proto_stream_validator/message_map.py`, `analysis/tools/proto_stream_validator/tests/test_message_map.py` (2489 lines but may lack edge cases)
- Risk: Mis-mapping channels or message types silently produces incorrect baseline data
- Priority: High — cascading impact on all downstream validation
- Fix approach: Add explicit test cases for known message ID collisions or version-specific mappings

**APK Indexer Test Coverage:**
- What's not tested: Large APK decompilation + re-indexing (archive tests archived; .worktrees contain old tests)
- Files: `.worktrees/proto-stream-validator/research/archive/openauto-prodigy/analysis/tools/apk_indexer/tests/`
- Risk: Indexer breakage goes undetected until next full APK analysis run (weeks later)
- Priority: Medium — expensive to run but infrequent
- Fix approach: Add integration test with small synthetic APK or fixture APK slice; run in CI on version bumps

## Security Considerations

**APK Mirror File Authenticity:**
- Risk: Downloaded APK from APKMirror is unverified; no checksum validation against official Google Play Store
- Files: `analysis/*.apkm` (mirror download, source may be compromised)
- Current mitigation: Visual inspection only
- Recommendations: Document APK source and version tag; ideally fetch from official Google Play Store via `play-sdk` or cached verified build; add SHA256 checksum validation in indexer

**Prototype Enum Validation (Untrusted Serialized Data):**
- Risk: Parsing untrusted proto frames without schema validation could allow DoS or memory exhaustion
- Files: `analysis/tools/proto_stream_validator/decode.py`, `analysis/tools/proto_stream_validator/diffing.py`
- Current mitigation: protobuf library handles buffer overflows; recursive diff depth is unbounded
- Recommendations: Add depth limit to recursive diff function in `diffing.py` to prevent stack exhaustion on malformed baselines

## Performance Bottlenecks

**Large JSON Baseline Files:**
- Problem: Normalized baselines written as uncompressed JSON; `analysis/baselines/*.json` are large and slow to deserialize
- Files: `analysis/tools/proto_stream_validator/io.py:62-68` (no compression)
- Cause: Each frame's decoded protobuf is a nested dict; baselines grow linearly with capture size
- Improvement path: Add optional gzip compression to baseline writes; lazy-load baseline on validation instead of loading entirely into memory

**Descriptor Bundle Rebuild on Every Run:**
- Problem: `descriptors.py` compiles proto files to descriptor set in tempfile every validation run
- Files: `analysis/tools/proto_stream_validator/run.py:91-92`, `analysis/tools/proto_stream_validator/descriptors.py`
- Cause: No caching of compiled descriptor bundles
- Improvement path: Pre-compile descriptor file for each APK version; cache in `analysis/descriptors/`; load once per tool invocation

**APK Indexing (One-Time Cost, High Latency):**
- Problem: Full APK decompilation, obfuscation analysis, and SQLite indexing takes hours
- Files: `analysis/tools/proto_indexer/` (implied from database existence)
- Status: One-time cost but regeneration blocks new APK version support
- Improvement path: Parallelize class extraction; use incremental indexing for APK versions that share obfuscation strategy

## Dependencies at Risk

**Protobuf Compiler Version Drift:**
- Risk: Proto syntax changes between protoc versions; old `.proto` files may not compile with newer protoc
- Files: All 223 `.proto` files in `oaa/`
- Current state: Files use `syntax="proto3"` uniformly; should be compatible with modern protoc
- Mitigation: Document minimum protoc version in `README.md` or CMake; test compilation on release CI

**Android API Level Mismatches in APK Analysis:**
- Risk: APK indexing tools assume Android API structure that may change with new Android versions
- Files: `analysis/tools/apk_indexer/extract.py`, `analysis/tools/proto_schema_validator/`
- Current state: Only tested on Android 14–16
- Mitigation: Document target API levels; add version checks in indexer that warn on unknown API levels

---

*Concerns audit: 2026-03-02*
