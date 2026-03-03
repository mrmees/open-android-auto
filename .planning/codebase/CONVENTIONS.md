# Coding Conventions

**Analysis Date:** 2026-03-02

## Overview

This repository contains Python analysis tools and protocol buffer definitions. The Python codebase emphasizes functional purity, type safety, and explicit error handling. The proto definitions follow a rigid naming convention tied to package structure.

## Python Code Style

### Naming Patterns

**Files:**
- Snake case: `extract.py`, `message_map.py`, `descriptors.py`
- Suffix-based naming for CLI entry points: `run.py` (e.g., `proto_stream_validator/run.py`, `proto_schema_validator/run.py`)

**Functions:**
- Snake case: `decode_payload()`, `normalize_decoded_frames()`, `build_descriptor_bundle()`
- Private functions prefixed with `_`: `_decode_frame()`, `_diff_values()`, `_normalize_json()`, `_message_class_for_descriptor()`
- Main CLI entry point: `main(argv=None) -> int`

**Variables:**
- Snake case: `message_type`, `payload_hex`, `frame_index`, `channel_id`
- Type hints throughout: `payload: bytes`, `rows: list[dict[str, Any]]`, `path: Path`

**Classes:**
- PascalCase: `Frame`, `NormalizedFrame`, `DescriptorBundle`, `DiffIssue`, `SchemaIssue`
- Dataclass-based for immutable data structures using `@dataclass(frozen=True)`
- Enums for categorical data: `Severity(Enum)`, `IssueKind(Enum)`, `class WireType(Enum)`

**Type Hints:**
- Modern union syntax: `str | None` (not `Optional[str]`)
- Dict literals: `dict[str, Any]` (not `Dict[str, Any]`)
- List literals: `list[str]`, `list[dict[str, Any]]`
- Dataclass field types specify `default=None` or `default_factory=dict` explicitly

### Imports and Organization

**Module imports in order:**
1. `from __future__ import annotations` — Always first, enables modern type syntax
2. Standard library: `sys`, `json`, `argparse`, `pathlib`, `tempfile`, `re`, `dataclasses`
3. Third-party: `google.protobuf.*`
4. Local relative imports: `from analysis.tools.proto_stream_validator...`

**Examples from codebase:**
```python
# First: future annotations
from __future__ import annotations

# Then: stdlib
from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any

# Then: third-party
from google.protobuf import json_format

# Finally: local
from analysis.tools.proto_stream_validator.models import Frame
```

**Import handling for optional dependencies:**
- Use try/except for imports that may not be installed
- Set module to `None` if import fails, raise `RuntimeError` at call time with context
- See: `decode.py` lines 5-15 for protobuf runtime handling

### Code Style

**Formatting:**
- No explicit formatter configuration found (no `.flake8`, `.pylintrc`, or Prettier config)
- Implicit PEP 8 adherence throughout codebase
- 4-space indentation
- Lines appear to have no hard limit (some lines exceed 100 chars)

**Comments:**
- Docstrings: Only on public functions/classes when behavior is non-obvious
- Inline comments: Sparse, used to document workarounds or proto-lite encoding quirks
- Example from `layer1_schema.py` lines 24-72: Known issues documented with dict comments explaining rationale

**Type Annotations:**
- Full type hints on all function signatures
- Return type specified: `-> int`, `-> dict[str, Any]`, `-> list[dict[str, Any]]`
- Return type `None` explicitly stated when no return
- Frozen dataclasses for immutable value objects

## Error Handling

**Patterns:**

1. **Validation errors:** Raise `ValueError` with context message
   ```python
   if not path.exists():
       raise FileNotFoundError(f"baseline not found: {path}")
   try:
       descriptor = bundle.pool.FindMessageTypeByName(message_type)
   except KeyError as exc:
       raise ValueError(f"unknown message type: {message_type}") from exc
   ```

2. **Runtime requirement errors:** Use `RuntimeError` with helpful message
   ```python
   if _PROTOBUF_IMPORT_ERROR is not None:
       raise RuntimeError(
           "python protobuf runtime is required (install package: protobuf)"
       ) from _PROTOBUF_IMPORT_ERROR
   ```

3. **CLI argument validation:** Return non-zero exit code, print to stderr
   ```python
   if args.bless and not args.reason:
       print("error: --reason is required with --bless", file=sys.stderr)
       return 2
   ```

4. **Graceful degradation for decode errors:** Wrap with context, re-raise with frame number
   ```python
   try:
       decoded = decode_payload(bundle, message_type, payload)
   except ValueError as exc:
       raise ValueError(f"frame {frame_index}: {exc}") from exc
   ```

**Exit codes:**
- `0`: Success
- `1`: Validation/processing failed (not a usage error)
- `2`: Usage error (bad arguments)

## Protobuf File Conventions

**Naming (from CONTRIBUTING.md):**
- `*Message.proto` → `oaa.proto.messages` package (request/response/indication messages)
- `*Data.proto` → `oaa.proto.data` package (structured data types, configs, events)
- `*Enum.proto` → `oaa.proto.enums` package (enumerations)
- `*IdsEnum.proto` → `oaa.proto.ids` package (channel-specific message ID enums)

**Imports:**
- Absolute paths: `import "oaa/common/StatusEnum.proto";`
- Consistent category directory structure

**Documentation:**
- Inline comments on fields documenting observed values and behavior
- Example from `radio-proto.md`: Service 15, 10 message types 0x801A–0x8023 fully documented

## Function Design

**Size:**
- Functions are small and focused (most < 50 lines)
- Private helper functions split out larger logic: `_decode_frame()` (33 lines) called by `build_normalized_rows()` (12 lines)

**Parameters:**
- Explicit parameter passing, no implicit state
- CLI functions take `argv: list[str] | None = None` to allow testing without sys.argv
- Path-heavy API: `Path` objects throughout instead of strings

**Return Values:**
- Functions return single values or tuple/dataclass with structured results
- CLI/main functions return exit code (int)
- Pure functions (no side effects) return computed values
- Data-loading functions return parsed objects: `list[Frame]`, `dict[str, Any]`

## Module Organization

**Tools structure:**
- `analysis/tools/[tool-name]/` — Tool module directory
- `analysis/tools/[tool-name]/run.py` — CLI entry point with `main(argv=None) -> int`
- `analysis/tools/[tool-name]/models.py` — Dataclass definitions
- `analysis/tools/[tool-name]/[function].py` — Implementation modules
- `analysis/tools/[tool-name]/tests/` — Test directory co-located

**Example paths:**
- `analysis/tools/proto_stream_validator/run.py` — Entry point
- `analysis/tools/proto_stream_validator/models.py` — `Frame`, `NormalizedFrame` dataclasses
- `analysis/tools/proto_stream_validator/decode.py` — `decode_payload()` function
- `analysis/tools/proto_stream_validator/tests/test_decode.py` — Tests

## Dataclass Patterns

**Frozen immutable structures for domain models:**
```python
@dataclass(frozen=True)
class Frame:
    ts_ms: float
    direction: str
    channel_id: int
    message_id: int
    message_name: str
    payload_hex: str
```

**Mutable dataclasses for configuration/mappings:**
```python
@dataclass
class ProtoMapping:
    proto_message: str
    proto_file: str
    proto_fqn: str = ""
    apk_classes: dict[str, str | None] = field(default_factory=dict)
    confidence: str = ""
```

**Frozen enum and issue types (always immutable):**
```python
@dataclass(frozen=True)
class SchemaIssue:
    proto_message: str
    kind: IssueKind
    severity: Severity
    field_number: int | None = None
    detail: str = ""
```

## JSON/YAML Serialization

- **Reading:** `json.loads()` with explicit encoding; validation at parse time (check list items)
- **Writing:** `json.dumps()` with `indent=2`; custom `_normalize_json()` for deterministic output
- **Normalization:** Sort dict keys recursively to ensure stable output for comparison
- Path objects converted to strings implicitly in serialization

## Testing Patterns (reflected in conventions)

- Tests mock external dependencies at module level (protobuf imports)
- Use `pytest.importorskip()` to skip tests when optional deps unavailable
- `tmp_path` fixture used for file I/O testing
- Monkeypatching used for controlled mocking

---

*Convention analysis: 2026-03-02*
