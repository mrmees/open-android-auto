# Proto Stream Validation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a deterministic non-media protobuf stream regression gate that validates current `oaa/*.proto` behavior against locked capture baselines.

**Architecture:** Add a Python validator tool under `analysis/tools/proto_stream_validator/` that loads captured non-media frames, maps each frame tuple to a protobuf message type, decodes via compiled descriptor set, normalizes output, and diffs against committed baseline JSON. The CLI supports strict read-only validation and explicit bless updates with mandatory rationale. Unit and golden tests enforce deterministic behavior and failure semantics.

**Tech Stack:** Python 3, `pytest`, `protoc` descriptor-set generation, `google.protobuf` dynamic message APIs, JSON/JSONL.

---

### Task 1: Scaffold Validator Package + Capture/Baseline I/O

**Skills:** `@test-driven-development`

**Files:**
- Create: `analysis/tools/proto_stream_validator/__init__.py`
- Create: `analysis/tools/proto_stream_validator/models.py`
- Create: `analysis/tools/proto_stream_validator/io.py`
- Create: `analysis/tools/proto_stream_validator/tests/test_io.py`

**Step 1: Write failing I/O tests**

Add tests for:
- reading JSONL capture into typed frame objects
- rejecting malformed lines
- writing deterministic normalized baseline JSON

```python
def test_load_capture_jsonl_reads_frames(tmp_path):
    path = tmp_path / "capture.jsonl"
    path.write_text('{"ts_ms":1,"direction":"Phone->HU","channel_id":0,"message_id":1,"message_name":"VERSION_REQUEST","payload_hex":"00010007"}\n')
    frames = load_capture_jsonl(path)
    assert len(frames) == 1
    assert frames[0].message_id == 1
```

**Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_io.py -v
```

Expected: `FAIL` (module/function missing).

**Step 3: Write minimal implementation**

Implement:
- `Frame` and `NormalizedFrame` dataclasses in `models.py`
- `load_capture_jsonl(path)` in `io.py`
- `write_normalized_baseline(path, rows)` in `io.py` with deterministic JSON output

**Step 4: Run test to verify it passes**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_io.py -v
```

Expected: `PASS`.

**Step 5: Commit**

```bash
git add analysis/tools/proto_stream_validator/__init__.py \
        analysis/tools/proto_stream_validator/models.py \
        analysis/tools/proto_stream_validator/io.py \
        analysis/tools/proto_stream_validator/tests/test_io.py
git commit -m "feat(proto-validator): scaffold capture and baseline io"
```

### Task 2: Implement Non-Media Filter + Message Mapping Contract

**Skills:** `@test-driven-development`

**Files:**
- Create: `analysis/tools/proto_stream_validator/message_map.py`
- Create: `analysis/tools/proto_stream_validator/filtering.py`
- Create: `analysis/tools/proto_stream_validator/tests/test_message_map.py`

**Step 1: Write failing mapping/filter tests**

Add tests for:
- excluding AV media tuples
- resolving known tuples to fully-qualified protobuf names
- failing on unmapped tuples

```python
def test_resolve_known_control_tuple():
    fqcn = resolve_message_type("Phone->HU", 0, 0x0001)
    assert fqcn == "oaa.proto.messages.VersionRequest"


def test_unmapped_tuple_raises():
    with pytest.raises(KeyError):
        resolve_message_type("Phone->HU", 99, 0x9999)
```

**Step 2: Run tests to verify failure**

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_message_map.py -v
```

Expected: `FAIL`.

**Step 3: Write minimal implementation**

Implement:
- explicit tuple mapping table in `message_map.py`
- `is_phase1_non_media(frame)` in `filtering.py`
- helpers that tag/skip media tuples deterministically

**Step 4: Run tests to verify pass**

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_message_map.py -v
```

Expected: `PASS`.

**Step 5: Commit**

```bash
git add analysis/tools/proto_stream_validator/message_map.py \
        analysis/tools/proto_stream_validator/filtering.py \
        analysis/tools/proto_stream_validator/tests/test_message_map.py
git commit -m "feat(proto-validator): add phase1 non-media mapping and filtering"
```

### Task 3: Descriptor-Backed Decode Engine

**Skills:** `@test-driven-development`

**Files:**
- Create: `analysis/tools/proto_stream_validator/descriptors.py`
- Create: `analysis/tools/proto_stream_validator/decode.py`
- Create: `analysis/tools/proto_stream_validator/tests/test_decode.py`

**Step 1: Write failing decode tests**

Add tests for:
- compiling descriptor set from `oaa/*.proto`
- decoding payload bytes into dynamic messages
- surfacing decode errors with frame context

```python
def test_decode_version_request_round_trip(tmp_path):
    bundle = build_descriptor_bundle(repo_root=Path.cwd(), out_dir=tmp_path)
    decoded = decode_payload(bundle, "oaa.proto.messages.VersionRequest", bytes.fromhex("00010007"))
    assert decoded["major_version"] == 1
```

**Step 2: Run tests to verify failure**

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_decode.py -v
```

Expected: `FAIL`.

**Step 3: Implement minimal decode path**

Implement:
- `build_descriptor_bundle(...)` invoking `protoc --descriptor_set_out`
- dynamic type lookup via `DescriptorPool` + `MessageFactory`
- `decode_payload(...)` returning JSON-like dict

**Step 4: Run tests to verify pass**

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_decode.py -v
```

Expected: `PASS`.

**Step 5: Commit**

```bash
git add analysis/tools/proto_stream_validator/descriptors.py \
        analysis/tools/proto_stream_validator/decode.py \
        analysis/tools/proto_stream_validator/tests/test_decode.py
git commit -m "feat(proto-validator): add descriptor-backed payload decoding"
```

### Task 4: Normalization + Diff Engine

**Skills:** `@test-driven-development`

**Files:**
- Create: `analysis/tools/proto_stream_validator/normalize.py`
- Create: `analysis/tools/proto_stream_validator/diffing.py`
- Create: `analysis/tools/proto_stream_validator/tests/test_diffing.py`

**Step 1: Write failing normalization/diff tests**

Add tests for:
- stable key ordering
- frame-index-preserving normalized rows
- actionable field-path diff output

```python
def test_diff_reports_field_path_changes():
    left = [{"frame_index": 0, "decoded": {"status": "OK"}}]
    right = [{"frame_index": 0, "decoded": {"status": "ERROR"}}]
    diffs = diff_normalized(left, right)
    assert any("decoded.status" in d.path for d in diffs)
```

**Step 2: Run tests to verify failure**

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_diffing.py -v
```

Expected: `FAIL`.

**Step 3: Implement minimal normalization and diffing**

Implement:
- `normalize_decoded_frames(...)`
- `diff_normalized(...)` with deterministic ordering
- mismatch types: missing, extra, changed value

**Step 4: Run tests to verify pass**

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_diffing.py -v
```

Expected: `PASS`.

**Step 5: Commit**

```bash
git add analysis/tools/proto_stream_validator/normalize.py \
        analysis/tools/proto_stream_validator/diffing.py \
        analysis/tools/proto_stream_validator/tests/test_diffing.py
git commit -m "feat(proto-validator): add deterministic normalization and diff engine"
```

### Task 5: CLI Orchestration (`validate` + `--bless`)

**Skills:** `@test-driven-development`

**Files:**
- Create: `analysis/tools/proto_stream_validator/run.py`
- Create: `analysis/tools/proto_stream_validator/tests/test_run.py`

**Step 1: Write failing CLI behavior tests**

Cover:
- validate mode fails on diffs and does not write baseline
- bless mode requires `--reason`
- bless mode writes updated baseline and emits audit summary

```python
def test_bless_requires_reason(tmp_path):
    rc, out = run_cli(["--capture", str(capture), "--baseline", str(base), "--bless"])
    assert rc != 0
    assert "--reason is required" in out
```

**Step 2: Run tests to verify failure**

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_run.py -v
```

Expected: `FAIL`.

**Step 3: Implement CLI orchestration**

Implement:
- argument parsing
- read/filter/map/decode/normalize/diff pipeline
- `--bless` guarded baseline write path
- concise diff reporting

**Step 4: Run tests to verify pass**

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_run.py -v
```

Expected: `PASS`.

**Step 5: Commit**

```bash
git add analysis/tools/proto_stream_validator/run.py \
        analysis/tools/proto_stream_validator/tests/test_run.py
git commit -m "feat(proto-validator): add validate and bless cli workflow"
```

### Task 6: Golden Fixtures + End-to-End Validator Test

**Skills:** `@test-driven-development`

**Files:**
- Create: `analysis/tools/proto_stream_validator/tests/fixtures/non_media_sample.jsonl`
- Create: `analysis/tools/proto_stream_validator/tests/fixtures/non_media_sample.normalized.json`
- Modify: `analysis/tools/proto_stream_validator/tests/test_run.py`

**Step 1: Write failing end-to-end golden tests**

Add:
- passing test for fixture capture + baseline
- failing test when fixture baseline is intentionally mutated

**Step 2: Run tests to verify failure**

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_run.py::test_golden_* -v
```

Expected: one or more `FAIL` before final wiring.

**Step 3: Implement fixture wiring and assertions**

Use committed fixtures and assert deterministic output/diff text.

**Step 4: Run tests to verify pass**

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests/test_run.py -v
```

Expected: `PASS`.

**Step 5: Commit**

```bash
git add analysis/tools/proto_stream_validator/tests/fixtures/non_media_sample.jsonl \
        analysis/tools/proto_stream_validator/tests/fixtures/non_media_sample.normalized.json \
        analysis/tools/proto_stream_validator/tests/test_run.py
git commit -m "test(proto-validator): add golden non-media capture regression coverage"
```

### Task 7: Tool README + Repo Docs Integration

**Files:**
- Create: `analysis/tools/proto_stream_validator/README.md`
- Modify: `analysis/README.md`
- Modify: `CONTRIBUTING.md`
- Modify: `docs/roadmap-current.md`

**Step 1: Write docs updates**

Document:
- capture contract
- validate/bless commands
- baseline update policy
- smoke/verification command set

**Step 2: Run path/reference sanity checks**

```bash
rg -n "proto_stream_validator|validate|--bless|non_media" analysis/README.md CONTRIBUTING.md docs/roadmap-current.md analysis/tools/proto_stream_validator/README.md
```

Expected: expected references in all updated docs.

**Step 3: Commit**

```bash
git add analysis/tools/proto_stream_validator/README.md analysis/README.md CONTRIBUTING.md docs/roadmap-current.md
git commit -m "docs(proto-validator): add usage and policy documentation"
```

### Task 8: Full Verification + Session Handoff

**Skills:** `@verification-before-completion`

**Files:**
- Modify: `docs/session-handoffs.md`

**Step 1: Run tool test suite**

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests -v
```

Expected: all tests pass.

**Step 2: Run tool smoke command**

```bash
PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py --help
```

Expected: CLI help printed, exit 0.

**Step 3: Record handoff entry with evidence**

Append an entry to `docs/session-handoffs.md` including changed files, status, next steps, and verification command outputs.

**Step 4: Commit**

```bash
git add docs/session-handoffs.md
git commit -m "docs: record proto stream validator handoff and verification evidence"
```
