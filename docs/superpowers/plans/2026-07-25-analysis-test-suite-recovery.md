# Analysis Test Suite Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore one clean-checkout verification contract for every maintained `analysis/tools` test while preserving the 736-test Android Auto 17.3 release gate and proving that confidence-comment repair does not change protobuf descriptors.

**Architecture:** Keep audit YAML and `tier_policy.py` canonical, make proto confidence comments a checked generated mirror, centralize protobuf runtime compatibility, and separate committed-fixture unit coverage from explicitly marked ignored-asset integration checks. Add the CI workflow only after the identical local `make verify` command is green.

**Tech Stack:** Python 3.11+, pytest, PyYAML, jsonschema, protobuf Python runtime 4.21.12 through 6.x, protoc 3.21+, GNU Make, GitHub Actions.

## Global Constraints

- Stay within the repository's protocol-reference scope: protobuf definitions, protocol documentation, and analysis tooling only.
- Do not change proto field numbers, field types, cardinality, enum values, packages, or message semantics.
- Do not promote confidence tiers, invent evidence, or change audit YAML merely to satisfy comment checks.
- Do not commit APKs, JADX trees, SQLite indexes, captures, or any other ignored/private analysis asset.
- Preserve every maintained test. Do not use broad `xfail`, unexplained skips, or test deletion to produce a green count.
- A missing local APK index may skip only a test marked `apk_index_integration`, and the skip reason must name the missing version(s).
- Stop immediately if pre/post annotation descriptor sets differ.
- Do not change `.github/workflows/publish-dist.yml` or the `dist` publication contract.
- Keep commits atomic and run the task's focused verification before each commit.
- Before completion, update `docs/session-handoffs.md` with what changed, why, status, next steps, and exact verification results as required by `AGENTS.md`.

---

### Task 1: Establish the local verification contract

**Files:**

- Create: `requirements-test.txt`
- Create: `pytest.ini`
- Create: `Makefile`
- Modify: `README.md`

**Interfaces:**

- `make test` collects the entire maintained `analysis/tools` tree.
- `make test-release` runs the exact historical Task 14 selection, which currently collects 736 tests.
- `make proto-check` compiles every active `oaa/**/*.proto` into one descriptor set.
- `make annotation-check` invokes the check-only annotation interface added in Task 3.
- `make verify` runs `proto-check`, `test`, and `annotation-check` without requiring ignored assets.
- `make test-integration` selects `apk_index_integration` checks and is allowed to skip when assets are absent.

- [ ] **Step 1: Record the existing red aggregate and green release collection**

Run:

```bash
PYTHONPATH=/usr/lib/python3/dist-packages:. \
  /tmp/oaa-task13-venv/bin/pytest --collect-only -q analysis/tools | tail -n 1

PYTHONPATH=/usr/lib/python3/dist-packages:. \
  /tmp/oaa-task13-venv/bin/pytest --collect-only -q \
  analysis/tools/apk_indexer/tests \
  analysis/tools/proto_schema_matcher/tests \
  analysis/tools/proto_schema_validator/tests \
  analysis/tools/proto_stream_validator/tests \
  analysis/tools/coverage_dashboard/tests \
  analysis/tools/arch_link_walker/tests \
  analysis/tools/cross_link_walker/tests \
  analysis/tools/seed_import/tests/test_audit_yaml_schema_validation.py \
  analysis/tools/seed_import/tests/test_audit_yaml_tier_consistency.py \
  analysis/tools/promotion_walker/tests | tail -n 1
```

Expected: aggregate collection reports 1,726 tests, and the historical selection reports exactly `736 tests collected`. If `/tmp/oaa-task13-venv` no longer exists, create `.venv` from the manifest in Step 3 and use `.venv/bin/python -m pytest` for both commands.

- [ ] **Step 2: Add the dependency and marker manifests**

Create `requirements-test.txt` with:

```text
pytest>=9,<10
PyYAML>=6,<7
jsonschema>=4.23,<5
protobuf>=4.21.12,<7
```

Create `pytest.ini` with:

```ini
[pytest]
markers =
    apk_index_integration: requires ignored local Android Auto APK-index SQLite snapshots
```

- [ ] **Step 3: Prove the manifest installs in an isolated environment**

Run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/python - <<'PY'
import google.protobuf
import jsonschema
import pytest
import yaml

print("protobuf", google.protobuf.__version__)
print("pytest", pytest.__version__)
print("jsonschema", jsonschema.__version__)
print("yaml", yaml.__version__)
PY
```

Expected: imports succeed and the protobuf version is at least 4.21.12 and below 7.

- [ ] **Step 4: Add the root Make targets**

Create `Makefile` with these concrete targets and the exact Task 14 release selection:

```make
PYTHON ?= python3
PYTEST := PYTHONPATH=. $(PYTHON) -m pytest
PROTO_FILES := $(shell find oaa -type f -name '*.proto' -print | sort)
OAA_DIRS := $(shell find oaa -mindepth 1 -maxdepth 1 -type d -print | sort)
RELEASE_TESTS := \
	analysis/tools/apk_indexer/tests \
	analysis/tools/proto_schema_matcher/tests \
	analysis/tools/proto_schema_validator/tests \
	analysis/tools/proto_stream_validator/tests \
	analysis/tools/coverage_dashboard/tests \
	analysis/tools/arch_link_walker/tests \
	analysis/tools/cross_link_walker/tests \
	analysis/tools/seed_import/tests/test_audit_yaml_schema_validation.py \
	analysis/tools/seed_import/tests/test_audit_yaml_tier_consistency.py \
	analysis/tools/promotion_walker/tests

.PHONY: test test-release test-integration proto-check annotation-check verify

test:
	$(PYTEST) -q analysis/tools

test-release:
	$(PYTEST) -q $(RELEASE_TESTS)

test-integration:
	$(PYTEST) -q -m apk_index_integration analysis/tools

proto-check:
	@descriptor="$$(mktemp)"; \
	trap 'rm -f "$$descriptor"' EXIT; \
	protoc --proto_path=. --include_imports \
	  --descriptor_set_out="$$descriptor" $(PROTO_FILES); \
	test -s "$$descriptor"

annotation-check:
	PYTHONPATH=. $(PYTHON) -m analysis.tools.seed_import.annotate --check $(OAA_DIRS)

verify: proto-check test annotation-check
```

- [ ] **Step 5: Document the local contract**

Add a `### Verify the repository` subsection under `README.md`'s Quick Start. It must document:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
make PYTHON=.venv/bin/python verify
```

Also document that `make PYTHON=.venv/bin/python test-integration` runs optional historical APK-index checks and prints explicit skips when the ignored indexes are unavailable.

- [ ] **Step 6: Verify the harness without pretending the suite is fixed**

Run:

```bash
make PYTHON=.venv/bin/python proto-check
make PYTHON=.venv/bin/python test-release
make PYTHON=.venv/bin/python test || true
git diff --check
```

Expected: proto compilation succeeds, the release gate reports 736 passed, and the aggregate remains red only in the already-classified recovery buckets. `annotation-check` is intentionally not invoked until Task 3 implements `--check`.

- [ ] **Step 7: Commit the verification surface**

Run:

```bash
git add requirements-test.txt pytest.ini Makefile README.md
git diff --cached --check
git commit -m "build(test): add repository verification contract"
```

---

### Task 2: Centralize protobuf message-class compatibility

**Files:**

- Create: `analysis/tools/protobuf_compat.py`
- Create: `analysis/tools/tests/test_protobuf_compat.py`
- Modify: `analysis/tools/proto_stream_validator/decode.py`
- Modify: `analysis/tools/oem_vw_parser/sdp_decode.py`

**Interface:**

```python
def message_class_for_descriptor(descriptor: object) -> type[Any]:
    """Return the dynamic message class on modern and protobuf 4.21 runtimes."""
```

The helper uses module-level `message_factory.GetMessageClass` when callable and otherwise uses `message_factory.MessageFactory().GetPrototype`.

- [ ] **Step 1: Write failing compatibility tests**

Create `analysis/tools/tests/test_protobuf_compat.py` with two isolated factory doubles. Keeping this new coverage outside the historical Task 14 directory selection preserves that gate's exact 736-test count:

```python
from types import SimpleNamespace

from analysis.tools import protobuf_compat


def test_message_class_uses_modern_module_api(monkeypatch):
    descriptor = object()
    expected = type("ModernMessage", (), {})
    fake_module = SimpleNamespace(GetMessageClass=lambda value: expected if value is descriptor else None)
    monkeypatch.setattr(protobuf_compat, "message_factory", fake_module)
    monkeypatch.setattr(protobuf_compat, "_PROTOBUF_IMPORT_ERROR", None)

    assert protobuf_compat.message_class_for_descriptor(descriptor) is expected


def test_message_class_falls_back_to_legacy_factory(monkeypatch):
    descriptor = object()
    expected = type("LegacyMessage", (), {})

    class LegacyFactory:
        def GetPrototype(self, value):
            assert value is descriptor
            return expected

    fake_module = SimpleNamespace(MessageFactory=LegacyFactory)
    monkeypatch.setattr(protobuf_compat, "message_factory", fake_module)
    monkeypatch.setattr(protobuf_compat, "_PROTOBUF_IMPORT_ERROR", None)

    assert protobuf_compat.message_class_for_descriptor(descriptor) is expected
```

Run:

```bash
.venv/bin/python -m pytest -q \
  analysis/tools/tests/test_protobuf_compat.py
```

Expected: RED because `analysis.tools.protobuf_compat` does not exist.

- [ ] **Step 2: Implement the shared helper**

Create `analysis/tools/protobuf_compat.py` with guarded protobuf import behavior equivalent to the existing validator boundary:

```python
from __future__ import annotations

from typing import Any

try:
    from google.protobuf import message_factory
except ModuleNotFoundError as exc:
    message_factory = None  # type: ignore[assignment]
    _PROTOBUF_IMPORT_ERROR = exc
else:
    _PROTOBUF_IMPORT_ERROR = None


def message_class_for_descriptor(descriptor: object) -> type[Any]:
    if _PROTOBUF_IMPORT_ERROR is not None:
        raise RuntimeError(
            "python protobuf runtime is required (install package: protobuf)"
        ) from _PROTOBUF_IMPORT_ERROR

    get_message_class = getattr(message_factory, "GetMessageClass", None)
    if callable(get_message_class):
        return get_message_class(descriptor)

    factory = message_factory.MessageFactory()  # type: ignore[union-attr]
    return factory.GetPrototype(descriptor)
```

- [ ] **Step 3: Route both decoders through the helper**

In `analysis/tools/proto_stream_validator/decode.py`, import `message_class_for_descriptor`, remove the private `_message_class_for_descriptor`, and call the shared helper from `decode_payload`.

In `analysis/tools/oem_vw_parser/sdp_decode.py`, remove `message_factory` from the protobuf import and change `_message_class` to:

```python
from analysis.tools.protobuf_compat import message_class_for_descriptor


def _message_class(bundle: DescriptorBundle, fqn: str):
    desc = bundle.pool.FindMessageTypeByName(fqn)
    return message_class_for_descriptor(desc)
```

- [ ] **Step 4: Run the focused red-to-green regression set**

Run:

```bash
.venv/bin/python -m pytest -q \
  analysis/tools/tests/test_protobuf_compat.py \
  analysis/tools/proto_stream_validator/tests/test_decode.py \
  analysis/tools/oem_vw_parser/tests \
  analysis/tools/dhu_divergence/tests/test_baseline_merge.py
```

Expected: all tests pass under the installed runtime. Then explicitly verify the legacy branch with the system protobuf 4.21.12 environment:

```bash
PYTHONPATH=/usr/lib/python3/dist-packages:. \
  /tmp/oaa-task13-venv/bin/pytest -q \
  analysis/tools/tests/test_protobuf_compat.py \
  analysis/tools/oem_vw_parser/tests \
  analysis/tools/dhu_divergence/tests/test_baseline_merge.py
```

Expected: the former nine `GetMessageClass` failures are gone.

- [ ] **Step 5: Commit the compatibility boundary**

Run:

```bash
git add \
  analysis/tools/protobuf_compat.py \
  analysis/tools/proto_stream_validator/decode.py \
  analysis/tools/tests/test_protobuf_compat.py \
  analysis/tools/oem_vw_parser/sdp_decode.py
git diff --cached --check
git commit -m "fix(test): support protobuf 4.21 dynamic messages"
```

---

### Task 3: Make annotation rendering checkable and idempotent

**Files:**

- Modify: `analysis/tools/seed_import/annotate.py`
- Create: `analysis/tools/seed_import/tests/test_annotate.py`

**Interfaces:**

```python
def render_annotated_content(
    content: str,
    audit: dict | None,
) -> tuple[str, dict[str, int]]:
    """Return generated proto text and declaration/field counts without I/O."""

def annotate_proto(
    proto_path: Path,
    audit: dict | None,
    *,
    check: bool = False,
) -> dict[str, int | bool]:
    """Write generated content, or report drift without writing in check mode."""

def annotate_directory(
    dir_path: Path,
    *,
    check: bool = False,
) -> dict[str, int]:
    """Process direct child protos and include a changed-file count."""

def main(argv: list[str] | None = None) -> int:
    """Return 1 when --check finds drift, otherwise 0."""
```

- [ ] **Step 1: Write focused rendering and CLI tests**

Create tests covering all of these behaviors:

1. A sidecar tier/evidence list produces the exact comment from `format_confidence`.
2. No sidecar replaces a stale Gold comment with `// confidence: unverified`.
3. Field-level overrides use their own tier/evidence.
4. A non-confidence inline field comment is preserved before the generated confidence comment.
5. Rendering already-rendered content is byte-identical.
6. `annotate_proto(..., check=True)` reports `changed=True` and does not write.
7. `main(["--check", directory])` returns 1 and prints the exact drifting proto path.
8. Repair followed by check returns zero and the second repair is a no-op.

Use a minimal proto fixture such as:

```python
PROTO = '''syntax = "proto2";
package fixture;

// confidence: gold [stale]
message Example {
  optional string value = 1; // semantic note  // confidence: gold [stale]
}
'''

AUDIT = {
    "confidence": "bronze",
    "evidence": [{"type": "apk_static"}],
}
```

Run:

```bash
.venv/bin/python -m pytest -q analysis/tools/seed_import/tests/test_annotate.py
```

Expected: RED because the in-memory renderer, check flag, and `main(argv)` contract do not exist.

- [ ] **Step 2: Extract the pure renderer**

Move the current line transformation loop from `annotate_proto` into `render_annotated_content`. Preserve newlines with `splitlines(keepends=True)`, preserve semantic comments, and derive missing-sidecar comments from:

```python
tier = audit.get("confidence", "unverified") if audit else "unverified"
evidence = audit.get("evidence", []) if audit else []
field_overrides = audit.get("fields", {}) if audit else {}
```

The renderer must be the only code path that decides generated comment text.

- [ ] **Step 3: Add non-mutating check mode**

Refactor `annotate_proto` to read once, render once, compare exact text, and write only when `changed and not check`. Add a `changed` count to directory totals. When `check=True`, print one stable line per drifted path:

```text
DRIFT: oaa/mic/MicrophoneOpenResponse.proto
```

Replace direct `sys.argv` parsing with `argparse`, accept one or more directory paths plus `--check`, warn and continue for nonexistent directories, and use `raise SystemExit(main())` in the module entry point.

- [ ] **Step 4: Run focused tests and a real read-only drift check**

Run:

```bash
.venv/bin/python -m pytest -q analysis/tools/seed_import/tests/test_annotate.py
before_status="$(git status --short)"
set +e
PYTHONPATH=. .venv/bin/python -m analysis.tools.seed_import.annotate \
  --check $(find oaa -mindepth 1 -maxdepth 1 -type d -print | sort)
check_status=$?
set -e
after_status="$(git status --short)"
test "$check_status" -eq 1
test "$before_status" = "$after_status"
```

Expected: focused tests pass; the repository check lists the known drift, exits 1, and leaves the worktree unchanged.

- [ ] **Step 5: Commit the renderer and check contract**

Run:

```bash
git add \
  analysis/tools/seed_import/annotate.py \
  analysis/tools/seed_import/tests/test_annotate.py
git diff --cached --check
git commit -m "feat(test): add confidence annotation check mode"
```

---

### Task 4: Synchronize confidence comments under descriptor protection

**Files:**

- Modify: `analysis/tools/cross_version/tests/test_silver_annotations.py`
- Modify: `analysis/tools/seed_import/tests/test_proto_annotations_match_sidecars.py`
- Modify: `analysis/tools/seed_import/tests/test_annotation_scope.py`
- Modify: only the `oaa/**/*.proto` files reported by annotation `--check`

**Contract:** Every generated confidence comment is the exact output of `format_confidence` for its sidecar or field override; a proto without a sidecar is rendered `unverified`. Audit YAML and `tier_policy.py` remain unchanged.

- [ ] **Step 1: Capture the pre-repair descriptor set**

Run:

```bash
descriptor_dir="$(mktemp -d)"
protoc --proto_path=. --include_imports \
  --descriptor_set_out="$descriptor_dir/before.pb" \
  $(find oaa -type f -name '*.proto' -print | sort)
test -s "$descriptor_dir/before.pb"
printf '%s\n' "$descriptor_dir" > /tmp/oaa-annotation-descriptor-dir
```

Expected: all 247 active protos compile. Retain this exact temporary path through Step 5.

- [ ] **Step 2: Replace hard-coded confidence assumptions with the canonical renderer**

In `test_proto_annotations_match_sidecars.py`, parameterize every active `oaa/**/*.proto`, load its sidecar with `load_audit_yaml`, and assert:

```python
expected, _ = render_annotated_content(
    proto_path.read_text(encoding="utf-8"),
    load_audit_yaml(proto_path),
)
assert proto_path.read_text(encoding="utf-8") == expected
```

In `test_annotation_scope.py`, retain the positive sensor/common presence checks but derive orphan validity through `render_annotated_content` instead of scanning for any old non-unverified label.

In `test_silver_annotations.py`, preserve sidecar/proto existence and no-upgrade-leak coverage, but replace the mandatory `cross_version` substring assertion with the exact canonical comment:

```python
expected_comment = format_confidence(
    sidecar_data["confidence"],
    sidecar_data.get("evidence", []),
)
assert expected_comment in proto_path.read_text(encoding="utf-8")
```

This deliberately accepts any evidence combination allowed by `tier_policy.py`; it does not invent or require a historical evidence-type pair.

- [ ] **Step 3: Demonstrate the tests are red before repair**

Run:

```bash
.venv/bin/python -m pytest -q \
  analysis/tools/cross_version/tests/test_silver_annotations.py \
  analysis/tools/seed_import/tests/test_proto_annotations_match_sidecars.py \
  analysis/tools/seed_import/tests/test_annotation_scope.py
```

Expected: RED only for current comment drift, including unsupported non-unverified comments on protos without sidecars.

- [ ] **Step 4: Repair all active proto comments through the production renderer**

Run:

```bash
PYTHONPATH=. .venv/bin/python -m analysis.tools.seed_import.annotate \
  $(find oaa -mindepth 1 -maxdepth 1 -type d -print | sort)
```

Review the diff with:

```bash
git diff --stat -- 'oaa/**/*.proto'
git diff -- 'oaa/**/*.proto' | rg '^[+-].*confidence:'
```

Expected: only `// confidence:` comments change. If any syntax, field, enum, package, import, or semantic prose changes, stop and fix the renderer before proceeding.

- [ ] **Step 5: Prove descriptor equality and idempotence**

Run:

```bash
descriptor_dir="$(cat /tmp/oaa-annotation-descriptor-dir)"
protoc --proto_path=. --include_imports \
  --descriptor_set_out="$descriptor_dir/after.pb" \
  $(find oaa -type f -name '*.proto' -print | sort)
cmp "$descriptor_dir/before.pb" "$descriptor_dir/after.pb"

PYTHONPATH=. .venv/bin/python -m analysis.tools.seed_import.annotate \
  --check $(find oaa -mindepth 1 -maxdepth 1 -type d -print | sort)

before_second="$(git diff -- 'oaa/**/*.proto')"
PYTHONPATH=. .venv/bin/python -m analysis.tools.seed_import.annotate \
  $(find oaa -mindepth 1 -maxdepth 1 -type d -print | sort)
after_second="$(git diff -- 'oaa/**/*.proto')"
test "$before_second" = "$after_second"
```

Expected: `cmp` exits zero, `--check` exits zero, and the second repair does not change the diff.

- [ ] **Step 6: Run the confidence-policy regression set**

Run:

```bash
.venv/bin/python -m pytest -q \
  analysis/tools/cross_version/tests/test_silver_annotations.py \
  analysis/tools/seed_import/tests/test_annotate.py \
  analysis/tools/seed_import/tests/test_annotation_scope.py \
  analysis/tools/seed_import/tests/test_proto_annotations_match_sidecars.py \
  analysis/tools/seed_import/tests/test_audit_yaml_schema_validation.py \
  analysis/tools/seed_import/tests/test_audit_yaml_tier_consistency.py \
  analysis/tools/promotion_walker/tests
```

Expected: all pass without sidecar changes.

- [ ] **Step 7: Commit the generated mirror repair**

Run:

```bash
mapfile -t proto_comment_files < <(
  git diff --name-only -- 'oaa/**/*.proto'
)
test "${#proto_comment_files[@]}" -gt 0
git add \
  analysis/tools/cross_version/tests/test_silver_annotations.py \
  analysis/tools/seed_import/tests/test_proto_annotations_match_sidecars.py \
  analysis/tools/seed_import/tests/test_annotation_scope.py \
  "${proto_comment_files[@]}"
git diff --cached --check
if git diff --cached --name-only | rg -v \
  '^(analysis/tools/(cross_version|seed_import)/tests/|oaa/.+\.proto$)'; then
  exit 1
fi
git commit -m "docs(proto): synchronize confidence comment mirrors"
```

---

### Task 5: Separate APK-index unit and integration coverage

**Files:**

- Modify: `analysis/tools/cross_version/tests/test_match_16_4.py`
- Modify: `analysis/tools/cross_version/tests/test_run.py`

**Contract:** Default collection sees and explicitly skips real-snapshot tests when ignored indexes are missing. Unit tests of path selection and matcher helpers use committed or temporary fixtures and always execute.

- [ ] **Step 1: Add a fixture-backed `_find_db` unit test**

In `test_run.py`, add:

```python
def test_find_db_164_prefers_canonical_build(tmp_path: Path, monkeypatch) -> None:
    from analysis.tools.cross_version import run

    canonical = (
        tmp_path
        / "android_auto_16.4.661014-release_164661014"
        / "apk-index"
        / "sqlite"
        / "apk_index.db"
    )
    canonical.parent.mkdir(parents=True)
    canonical.touch()
    monkeypatch.setattr(run, "_ANALYSIS", tmp_path)

    assert run._find_db("16.4") == canonical
```

Run:

```bash
.venv/bin/python -m pytest -q \
  analysis/tools/cross_version/tests/test_run.py::test_find_db_164_prefers_canonical_build
```

Expected: pass with no ignored repository assets.

- [ ] **Step 2: Mark the real database checks and make missing prerequisites explicit**

Import `pytest` in `test_run.py`, mark the existing real-tree test with `@pytest.mark.apk_index_integration`, and replace its hard assertion with:

```python
result = _find_db("16.4")
if result is None:
    pytest.skip("missing ignored APK-index SQLite snapshot: Android Auto 16.4.661014")
```

In `test_match_16_4.py`, add a helper that resolves 15.9, 16.1, 16.2, and 16.4 via `_find_db`, builds an exact missing-version list, and skips before `run_matcher` if any are absent. Mark `test_match_snapshot` with `@pytest.mark.apk_index_integration` and pass explicit inputs:

```python
db_paths_prior, db_164 = _historical_db_paths_or_skip()
result = run_matcher(db_paths_prior=db_paths_prior, db_164=db_164)
```

The skip text must be:

```text
missing ignored APK-index SQLite snapshot(s): 15.9, 16.4
```

with the actual sorted missing versions substituted.

- [ ] **Step 3: Remove the unit test's ordering dependency on the integration test**

Rename `test_candidates_md_has_table_rows` to `test_committed_candidates_md_has_table_rows`, update its docstring to say it validates the committed report, and remove the claim that `test_match_snapshot` ran first. Keep the file existence, summary, header, and minimum-row assertions.

- [ ] **Step 4: Verify both default and selected-integration behavior**

Run:

```bash
.venv/bin/python -m pytest -q -ra \
  analysis/tools/cross_version/tests/test_match_16_4.py \
  analysis/tools/cross_version/tests/test_run.py

.venv/bin/python -m pytest -q -ra -m apk_index_integration \
  analysis/tools/cross_version/tests/test_match_16_4.py \
  analysis/tools/cross_version/tests/test_run.py
```

Expected in a clean checkout: all fixture/unit checks pass, exactly the ignored-asset tests skip with named reasons, and no snapshot test reports pass without running `run_matcher`. If all four local DBs are present, the two marked checks execute instead and must pass.

- [ ] **Step 5: Commit the asset boundary**

Run:

```bash
git add \
  analysis/tools/cross_version/tests/test_match_16_4.py \
  analysis/tools/cross_version/tests/test_run.py
git diff --cached --check
git commit -m "test(cross-version): isolate APK index integrations"
```

---

### Task 6: Update multi-message and Platinum fixture contracts

**Files:**

- Modify: `analysis/tools/seed_import/tests/test_seed_import_grouping.py`
- Modify: `analysis/tools/dhu_divergence/tests/test_example_sidecar.py`

**Contract:** Multi-message grouping is detected from declared messages plus structured sidecar content, not an obsolete `Mapped ...` prefix. Platinum schema behavior is pinned to the committed test fixture, not a production sidecar whose tier is policy-derived.

- [ ] **Step 1: Demonstrate the two legacy contracts are red**

Run:

```bash
.venv/bin/python -m pytest -q \
  analysis/tools/seed_import/tests/test_seed_import_grouping.py \
  analysis/tools/dhu_divergence/tests/test_example_sidecar.py
```

Expected: three failures: two grouping assumptions and the mutable Platinum expectation.

- [ ] **Step 2: Derive grouping from proto declarations and structured evidence**

Add helpers equivalent to:

```python
import re


def _declared_messages(proto_path: Path) -> set[str]:
    return set(
        re.findall(
            r"^\s*message\s+(\w+)",
            proto_path.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
    )


def _messages_mentioned_in_evidence(data: dict, declared: set[str]) -> set[str]:
    evidence_text = yaml.safe_dump(data.get("evidence") or [], sort_keys=True)
    return {name for name in declared if name in evidence_text}
```

Use these helpers in `_find_multi_message_protos` and in the CarControl assertion. Continue requiring at least two declared message names in combined evidence. This keeps coverage of actual evidence combination without encoding one prose sentence format.

Change the primary/composite label assertion to accept only a declared message name or the explicit file-wide label:

```python
declared = _declared_messages(CAR_CONTROL_PROTO)
assert primary in declared or primary == f"{CAR_CONTROL_PROTO.stem} (all)"
```

- [ ] **Step 3: Point the Platinum schema test at its immutable fixture**

In `test_example_sidecar.py`, replace the production path with:

```python
example_path = (
    Path(__file__).parent
    / "fixtures"
    / "example_platinum_sidecar.audit.yaml"
)
```

Update the module docstring to state that this is the committed schema fixture. Keep every existing Platinum field assertion and `jsonschema.validate` call.

- [ ] **Step 4: Run focused and neighboring suites**

Run:

```bash
.venv/bin/python -m pytest -q \
  analysis/tools/seed_import/tests/test_seed_import_grouping.py \
  analysis/tools/dhu_divergence/tests/test_example_sidecar.py \
  analysis/tools/dhu_divergence/tests \
  analysis/tools/seed_import/tests
```

Expected: grouping and fixture tests pass, with no test removed and no production sidecar changed.

- [ ] **Step 5: Commit the current sidecar contracts**

Run:

```bash
git add \
  analysis/tools/seed_import/tests/test_seed_import_grouping.py \
  analysis/tools/dhu_divergence/tests/test_example_sidecar.py
git diff --cached --check
git commit -m "test(audit): align grouping and Platinum fixtures"
```

---

### Task 7: Publish the four missing cross-version category tables

**Files:**

- Create: `docs/cross-version/carintent.md`
- Create: `docs/cross-version/mediabrowser.md`
- Create: `docs/cross-version/mic.md`
- Create: `docs/cross-version/verification.md`

**Contract:** Every active `oaa/` category has a concrete table. Unknown historical class mappings remain `--`; explanatory prose may cite only facts already committed in protos, audits, or existing protocol documentation.

- [ ] **Step 1: Confirm the category-coverage test is red**

Run:

```bash
.venv/bin/python -m pytest -q \
  analysis/tools/cross_version/tests/test_published_outputs.py::test_category_tables_exist_for_each_oaa_subdir
```

Expected: RED listing exactly `carintent`, `mediabrowser`, `mic`, and `verification`.

- [ ] **Step 2: Add the CarIntent table without backfilling unsupported history**

Create `docs/cross-version/carintent.md` with a standard 15.9/16.1/16.2/16.4 table containing:

```markdown
| Proto Name | 15.9 | 16.1 | 16.2 | 16.4 | Fields (15.9/16.1/16.2/16.4) |
|---|---|---|---|---|---|
| CarIntentMessage | -- | -- | -- | -- | 0/0/0/0 |
```

Below it, state that committed Android Auto 17.3 static evidence maps the message to `xgc` and proves only optional string field 2; the raw message ID and historical 15.9-16.4 identities remain unknown.

- [ ] **Step 3: Add the Media Browser historical-reference table**

Create `docs/cross-version/mediabrowser.md` with one `--` row for each declared category surface:

```text
MediaBrowserMessageId, MediaListType, InstrumentClusterAction, MediaSource,
MediaList, MediaSong, MediaRootNode, MediaSourceNode, MediaListNode,
MediaSongNode, MediaGetNode, MediaBrowseInput
```

Use `0/0/0/0` field counts because no APK class mapping is published for these historical definitions. State that the dedicated channel is deprecated/dead in 16.1+ and the committed 16.2 evidence identifies only the empty SDP stub `vxy`, not these message classes.

- [ ] **Step 4: Add the microphone table from the committed 16.2 mapping**

Create `docs/cross-version/mic.md` with:

```markdown
| Proto Name | 15.9 | 16.1 | 16.2 | 16.4 | Fields (15.9/16.1/16.2/16.4) |
|---|---|---|---|---|---|
| MicrophoneOpenResponse | -- | -- | `vyj` | -- | 0/0/2/0 |
```

State that the class and two-field layout come from the committed 16.2 handler trace; no mapping is published for the other table versions.

- [ ] **Step 5: Add the DHU-only verification table**

Create `docs/cross-version/verification.md` with `--` and `0/0/0/0` for these 15 declared surfaces:

```text
GalVerificationMessageId, GalVerificationSetSensor,
GalVerificationMediaSinkStatus, GalVerificationVideoFocus,
GalVerificationAudioFocus, GalVerificationInjectInput,
GalVerificationBugReportRequest, GalVerificationBugReportResponse,
GalVerificationScreenCaptureRequest, GalVerificationScreenCaptureResponse,
GalVerificationDisplayInformationRequest,
GalVerificationDisplayInformationResponse, GoogleDiagnosticsMessageId,
GoogleDiagnosticsBugReportRequest, GoogleDiagnosticsBugReportResponse
```

State that these are DHU/test vendor-extension definitions absent from the committed 16.2 phone APK analysis, so no phone-side obfuscated class mapping is claimed.

- [ ] **Step 6: Run documentation path and table sanity checks**

Run:

```bash
.venv/bin/python -m pytest -q analysis/tools/cross_version/tests/test_published_outputs.py
for category in carintent mediabrowser mic verification; do
  test -f "docs/cross-version/$category.md"
  rg -n '^\| Proto Name \| 15\.9 \| 16\.1 \| 16\.2 \| 16\.4 \|' \
    "docs/cross-version/$category.md"
done
! rg -n '\| `?[a-z]{3}`? \|' \
  docs/cross-version/carintent.md \
  docs/cross-version/mediabrowser.md \
  docs/cross-version/verification.md
rg -n '\| MicrophoneOpenResponse \| -- \| -- \| `vyj` \| -- \|' \
  docs/cross-version/mic.md
git diff --check
```

Expected: all published-output tests pass; only `mic.md` claims a 15.9-16.4 class mapping among the new tables.

- [ ] **Step 7: Commit the missing category documentation**

Run:

```bash
git add \
  docs/cross-version/carintent.md \
  docs/cross-version/mediabrowser.md \
  docs/cross-version/mic.md \
  docs/cross-version/verification.md
git diff --cached --check
git commit -m "docs(cross-version): cover remaining proto categories"
```

---

### Task 8: Close the local gate, add equivalent CI, and record the handoff

**Files:**

- Create: `.github/workflows/verify.yml`
- Modify: `docs/session-handoffs.md`
- Modify: `docs/roadmap-current.md` only if actual execution changed priority or sequencing

**Contract:** CI runs the same `make verify` entrypoint proven locally. The workflow is not added until the command exits zero in a clean local environment.

- [ ] **Step 1: Run the full local gate before creating CI**

Run:

```bash
make PYTHON=.venv/bin/python verify
```

Expected: all maintained tests pass except only explicitly reported `apk_index_integration` skips caused by absent ignored SQLite snapshots; all active protos compile; annotation check is clean. The starting collection was 1,726 tests, but record the exact final passed/skipped counts for the handoff because this plan adds focused regression tests.

- [ ] **Step 2: Re-run the historical release gate and descriptor invariant**

Run:

```bash
make PYTHON=.venv/bin/python test-release
make PYTHON=.venv/bin/python proto-check

descriptor_dir="$(cat /tmp/oaa-annotation-descriptor-dir)"
cmp "$descriptor_dir/before.pb" "$descriptor_dir/after.pb"
```

Expected: exactly 736 release tests pass, all 247 active protos compile, and the pre/post annotation descriptor sets remain byte-identical.

- [ ] **Step 3: Run explicit integration selection and repository sanity checks**

Run:

```bash
make PYTHON=.venv/bin/python test-integration
PYTHONPATH=. .venv/bin/python -m analysis.tools.seed_import.annotate \
  --check $(find oaa -mindepth 1 -maxdepth 1 -type d -print | sort)
git diff --check
git status --short
```

Expected: local APK-index integration checks either execute and pass or skip with exact missing-asset reasons; annotation check and diff check exit zero. Review every dirty path before adding CI.

- [ ] **Step 4: Add the clean-checkout GitHub Actions workflow**

Create `.github/workflows/verify.yml`:

```yaml
name: Verify

on:
  push:
    branches:
      - main
      - dev
      - "dev/**"
  pull_request:

permissions:
  contents: read

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.11"
          cache: pip

      - name: Install protoc and Python test dependencies
        run: |
          sudo apt-get update
          sudo apt-get install --yes protobuf-compiler
          python -m pip install --upgrade pip
          python -m pip install -r requirements-test.txt

      - name: Verify repository
        run: make PYTHON=python verify
```

This new workflow may use the current major versions even though the separate unchanged `publish-dist.yml` still uses its existing checkout version.

- [ ] **Step 5: Validate the workflow and re-run its exact command locally**

Run:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
import yaml

path = Path(".github/workflows/verify.yml")
data = yaml.safe_load(path.read_text(encoding="utf-8"))
assert data["jobs"]["verify"]["steps"][-1]["run"] == "make PYTHON=python verify"
print(path)
PY

make PYTHON=.venv/bin/python verify
git diff --check
```

Expected: YAML parses, its final step is the authoritative Make target, and the local equivalent remains green.

- [ ] **Step 6: Append the required implementation handoff**

Append a dated `Analysis test-suite recovery` entry to `docs/session-handoffs.md` containing:

- what changed: root verification contract, shared protobuf helper, annotation check/repair, asset boundary, current grouping/Platinum contracts, four cross-version tables, and CI;
- why: the aggregate suite had six classified debt buckets and could not gate the analysis-to-main merge;
- status: exact aggregate pass/skip count, exact release count, proto count, annotation status, and descriptor equality;
- next steps: open/review the integration PR, merge to `main` only after GitHub Actions passes, then delete the merged analysis branch; and
- every command/result from Steps 1-5, including explicit integration skip reasons.

Update `docs/roadmap-current.md` only if implementation changed the approved order. If the aggregate gate is green but branch integration has not occurred, keep recovery in `Now` and state that only CI/merge remains.

- [ ] **Step 7: Commit CI and handoff**

Run:

```bash
git add .github/workflows/verify.yml docs/session-handoffs.md
if ! git diff --quiet -- docs/roadmap-current.md; then
  git add docs/roadmap-current.md
fi
git diff --cached --check
git commit -m "ci(test): enforce aggregate analysis verification"
```

- [ ] **Step 8: Perform final evidence-before-completion verification**

Run fresh after the final commit:

```bash
make PYTHON=.venv/bin/python verify
make PYTHON=.venv/bin/python test-release
make PYTHON=.venv/bin/python test-integration
git diff --check
git status --short --branch
git log --oneline -8
```

Expected: `verify` is green; release is 736 passed; integration checks pass or explicitly skip only for absent ignored snapshots; the worktree is clean; and the eight recovery commits are visible. Do not merge, push, or delete the branch as part of this implementation plan unless the user separately authorizes publication/integration.

---

## Plan Self-Review

- The plan covers every approved failure bucket: 226 annotation/policy failures, nine protobuf compatibility failures, two APK-index dependencies, two grouping heuristics, one Platinum sidecar expectation, and one cross-version documentation coverage failure.
- The local and CI commands are identical at the `make verify` boundary.
- The historical 736-test release selection is copied from the checked-in Task 14 plan and independently collection-verified before this plan was written.
- Comment synchronization has both a pre/post descriptor equality gate and an idempotence gate.
- No task changes audit evidence, confidence tiers, protobuf semantics, ignored assets, or the `dist` workflow.
- All new interfaces, fixtures, commands, expected outcomes, and commit messages are concrete; no implementation decision is left unresolved.
