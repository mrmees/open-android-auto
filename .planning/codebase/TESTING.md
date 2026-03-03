# Testing Patterns

**Analysis Date:** 2026-03-02

## Test Framework

**Runner:**
- pytest (referenced throughout as test framework)
- Config: No `pytest.ini` or `pyproject.toml` found; using pytest defaults
- Cache: `.pytest_cache/` directory present

**Assertion Library:**
- pytest assertions (native `assert` statements)
- No pytest plugins explicitly imported

**Run Commands:**
```bash
pytest                           # Run all tests
pytest analysis/tools/           # Run specific tool tests
pytest -v                        # Verbose output
pytest --co                      # Collect tests without running
```

## Test File Organization

**Location:**
- Tests co-located with source code in `tests/` subdirectories
- Pattern: `analysis/tools/[tool-name]/tests/`

**Examples:**
- `analysis/tools/proto_stream_validator/tests/test_*.py` (4 test modules)
- `analysis/tools/apk_indexer/tests/test_*.py` (9 test modules)

**Naming:**
- Files: `test_[module_name].py` (PEP 517 convention)
- Functions: `test_[specific_behavior_being_tested]()`
- Example: `test_extract_uuid()`, `test_decode_payload_ping_request()`

**Fixture Organization:**
- Fixtures stored in `tests/fixtures/` when shared across tools
- Example path: `analysis/tools/proto_stream_validator/tests/fixtures/non_media_sample.jsonl`

## Test Structure

**Standard pytest pattern:**
```python
def test_extract_uuid(tmp_path):
    sample = tmp_path / "A.java"
    sample.write_text('String u = "4de17a00-52cb-11e6-bdf4-0800200c9a66";\n')

    result = extract_signals(tmp_path)

    assert result["uuids"][0]["value"] == "4de17a00-52cb-11e6-bdf4-0800200c9a66"
```

**Sections:**
1. **Setup** — Create fixtures, write test data
2. **Execute** — Call function under test
3. **Assert** — Verify results

**Docstring-less tests:**
- Test name is the documentation (descriptive function name)
- No docstrings on test functions

## Handling Optional Dependencies

**Pattern: Skip tests when dependency missing**

```python
# Module-level skip if dependency unavailable
pytest.importorskip("google.protobuf")

# Or per-test conditional skip
import importlib.util
_GOOGLE_PROTOBUF_AVAILABLE = importlib.util.find_spec("google.protobuf") is not None

@pytest.mark.skipif(
    not _GOOGLE_PROTOBUF_AVAILABLE,
    reason="google.protobuf runtime not available",
)
def test_golden_fixture_passes_validation():
    ...
```

**Examples:**
- `analysis/tools/proto_stream_validator/tests/test_decode.py` — Module-level skip via `pytest.importorskip("google.protobuf")`
- `analysis/tools/proto_stream_validator/tests/test_run.py` — Per-test skip with `@pytest.mark.skipif`

## Mocking Patterns

**Module/function patching with monkeypatch:**
```python
def test_validate_fails_on_diff_and_does_not_write_baseline(tmp_path, monkeypatch):
    ...
    monkeypatch.setattr(
        run,
        "build_normalized_rows",
        lambda capture_path, repo_root: [
            {"frame_index": 0, "decoded": {"status": "ERROR"}}
        ],
    )

    rc = run.main([...])
    assert rc == 1
```

**What to Mock:**
- External system calls (protobuf runtime, file I/O across modules)
- Functions in modules under test that have expensive side effects

**What NOT to Mock:**
- Core dataclass definitions
- Pure utility functions (sorting, normalization)
- Local private helpers (call them through public interface)

## Fixtures and Factories

**Test Data Creation:**
Fixtures created inline in test using `tmp_path`:

```python
def test_extract_enum_maps(tmp_path):
    sample = tmp_path / "vyn.java"
    sample.write_text(
        "public enum vyn {\n"
        "  MEDIA_CODEC_AUDIO_PCM(1),\n"
        "  MEDIA_CODEC_AUDIO_AAC_LC(2);\n"
        ...
    )
```

**Shared Fixtures:**
Golden files stored in `tests/fixtures/`:
- `analysis/tools/proto_stream_validator/tests/fixtures/non_media_sample.jsonl` — JSONL capture data
- `analysis/tools/proto_stream_validator/tests/fixtures/non_media_sample.normalized.json` — Expected baseline

**Loading Fixtures:**
```python
_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

def test_golden_fixture_passes_validation():
    capture = _FIXTURES_DIR / "non_media_sample.jsonl"
    baseline = _FIXTURES_DIR / "non_media_sample.normalized.json"
    ...
```

## Test Types

**Unit Tests (majority):**
- Test individual functions in isolation
- Use `tmp_path` for file I/O without side effects
- Examples:
  - `test_decode_payload_ping_request()` — Tests `decode_payload()` function
  - `test_normalize_decoded_frames_sorts_nested_keys()` — Tests `normalize_value()` recursion
  - `test_extract_uuid()` — Tests regex extraction on sample Java file

**Integration Tests (some):**
- Test multiple components working together
- Marked with descriptive names, no special markers
- Examples:
  - `test_run_indexer_builds_versioned_outputs()` — Tests full indexing pipeline
  - `test_golden_fixture_passes_validation()` — Tests CLI with real fixtures

**Regression Tests (explicitly):**
- Validate against locked baselines (proto stream validator)
- Files: `[name].normalized.json` as source of truth
- Run with `--bless --reason "rationale"` to update
- Example: `test_golden_fixture_detects_drift()` — Verifies drift detection works

**E2E Tests:**
- Not found in this codebase
- Tools are CLI-based; integration tests serve as E2E

## Async Testing

Not applicable — codebase is synchronous.

## Error Testing

**Pattern: Expect exceptions with pytest.raises**
```python
def test_decode_payload_rejects_malformed_wire_bytes(tmp_path):
    bundle = build_descriptor_bundle(repo_root=Path.cwd(), out_dir=tmp_path)

    with pytest.raises(ValueError):
        decode_payload(bundle, "oaa.proto.messages.PingRequest", bytes.fromhex("08"))
```

**When to test errors:**
- Invalid input to parsing functions
- Missing required fields
- File not found conditions
- Type mismatches

**Examples:**
- `test_decode_payload_rejects_malformed_wire_bytes()` — Malformed protobuf
- CLI tests verify exit codes: `assert rc == 1` for validation failure, `assert rc == 2` for usage error
- `_load_baseline()` tests validate JSON structure before use

## Test Execution Patterns

**Direct function invocation (most tests):**
```python
result = extract_signals(tmp_path)
assert result["uuids"][0]["value"] == "..."
```

**CLI invocation with mocked argv:**
```python
rc = run.main([
    "--capture", str(capture),
    "--baseline", str(baseline),
])
assert rc == 0
```

**Fixture path construction:**
```python
capture = _FIXTURES_DIR / "non_media_sample.jsonl"
baseline = _FIXTURES_DIR / "non_media_sample.normalized.json"
rc = run.main([
    "--capture", str(capture),
    "--baseline", str(baseline),
    "--repo-root", str(Path.cwd()),
])
```

## Coverage

**Requirements:**
- No explicit coverage target enforced (no `[tool.pytest]` config)
- No `.coveragerc` file

**View Coverage:**
```bash
pytest --cov=analysis/tools --cov-report=html
# or
pytest --cov=analysis/tools --cov-report=term-missing
```

## Common Test Patterns

**Tempdir for isolated file I/O:**
```python
def test_bless_writes_updated_baseline(tmp_path, monkeypatch):
    capture = tmp_path / "capture.jsonl"
    capture.write_text("", encoding="utf-8")
    baseline = tmp_path / "baseline.json"

    # ... test creates files in tmp_path

    assert baseline.exists()
    written = json.loads(baseline.read_text(encoding="utf-8"))
    assert written[0]["decoded"] == {"major": 1, "minor": 7}
```

**Dictionary assertion on parsed data:**
```python
def test_diff_reports_field_path_changes():
    expected = [{"frame_index": 0, "decoded": {"status": "OK"}}]
    actual = [{"frame_index": 0, "decoded": {"status": "ERROR"}}]

    diffs = diff_normalized(expected, actual)

    assert any(diff.path == "[0].decoded.status" and diff.kind == "changed" for diff in diffs)
```

**Set assertions for unordered results:**
```python
def test_extract_proto_write_patterns(tmp_path):
    sample = tmp_path / "E.java"
    sample.write_text("xhqVar.b |= 16;\nxhqVar.g = i7;\n...")

    result = extract_signals(tmp_path)

    ops = {(row["target"], row["op"]) for row in result["proto_writes"]}
    assert ("xhqVar.b", "|=") in ops
    assert ("xhqVar.g", "=") in ops
```

**Exit code validation:**
```python
def test_bless_requires_reason(tmp_path):
    capture = tmp_path / "capture.jsonl"
    capture.write_text("", encoding="utf-8")
    baseline = tmp_path / "baseline.json"

    rc = run.main([
        "--capture", str(capture),
        "--baseline", str(baseline),
        "--bless",
    ])

    assert rc != 0
    assert not baseline.exists()
```

## Test Statistics

**Total test coverage:**
- 14 test modules across 2 tools
- `proto_stream_validator`: 4 test files (test_decode.py, test_diffing.py, test_io.py, test_message_map.py, test_run.py)
- `apk_indexer`: 9 test files (test_extract.py, test_catalog.py, test_confidence.py, test_resolve_version.py, test_report.py, test_writers.py, test_run_indexer.py, test_relocate_source.py, test_benchmark.py)

**Test file sizes:**
- Ranges from 11 lines (`test_relocate_source.py`) to 115 lines (`test_extract.py`)
- Most test files 25–50 lines (focused on single module)

## Pre-Commit/Linting

**Configuration:**
- No `.pre-commit-config.yaml` found
- No `.flake8`, `.pylintrc`, or linting configuration files detected
- Tests are the primary quality gate

## Notes

**Missing but useful for future:**
- No pytest plugins (e.g., pytest-cov, pytest-asyncio)
- No centralized conftest.py for shared fixtures
- No test data factories or builders (all data created in-test)
- No parameterized tests (@pytest.mark.parametrize)

---

*Testing analysis: 2026-03-02*
