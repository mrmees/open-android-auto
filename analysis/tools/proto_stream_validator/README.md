# Proto Stream Validator

Capture-based protobuf regression gate for `oaa/*.proto` changes.

## Purpose

Given a recorded non-media AA capture, this tool decodes frames with the current
protobuf schema and compares normalized output to a committed baseline.

- `validate` mode: fails on any diff
- `--bless` mode: explicitly rewrites baseline (requires `--reason`)

## Capture Format

Input capture is JSONL (`analysis/captures/non_media/*.jsonl`), one frame per line:

- `ts_ms`
- `direction` (`Phone->HU` or `HU->Phone`)
- `channel_id`
- `message_id`
- `message_name`
- `payload_hex`

Phase 1 excludes AV media payload frames (`AV_MEDIA_*`) from validation.

## Usage

Validate against baseline:

```bash
PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py \
  --capture analysis/captures/non_media/session_a.jsonl \
  --baseline analysis/baselines/non_media/session_a.normalized.json
```

Bless intentional schema changes:

```bash
PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py \
  --capture analysis/captures/non_media/session_a.jsonl \
  --baseline analysis/baselines/non_media/session_a.normalized.json \
  --bless \
  --reason "intentional proto update for <message>"
```

## Requirements

- `protoc` in `PATH`
- Python protobuf runtime (`google.protobuf`)

If protobuf runtime is unavailable, decode/golden tests are skipped and CLI decode
paths fail with an actionable runtime error.

## Smoke / Tests

Tool tests:

```bash
PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests -v
```

CLI help:

```bash
PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py --help
```
