from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable

from analysis.tools.proto_stream_validator.models import Frame


_REQUIRED_FRAME_KEYS = {
    "ts_ms",
    "direction",
    "channel_id",
    "message_id",
    "message_name",
    "payload_hex",
}


def _normalize_json(value: Any) -> Any:
    if is_dataclass(value):
        return _normalize_json(asdict(value))
    if isinstance(value, dict):
        return {key: _normalize_json(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_normalize_json(item) for item in value]
    return value


def _parse_frame_row(raw: dict[str, Any], line_no: int) -> Frame:
    missing = sorted(_REQUIRED_FRAME_KEYS - set(raw.keys()))
    if missing:
        raise ValueError(f"capture row {line_no} missing required keys: {', '.join(missing)}")

    return Frame(
        ts_ms=float(raw["ts_ms"]),
        direction=str(raw["direction"]),
        channel_id=int(raw["channel_id"]),
        message_id=int(raw["message_id"]),
        message_name=str(raw["message_name"]),
        payload_hex=str(raw["payload_hex"]),
    )


def load_capture_jsonl(path: Path) -> list[Frame]:
    frames: list[Frame] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        text = line.strip()
        if not text:
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"capture row {line_no} is not valid json") from exc
        if not isinstance(parsed, dict):
            raise ValueError(f"capture row {line_no} must be an object")
        frames.append(_parse_frame_row(parsed, line_no))
    return frames


def write_normalized_baseline(path: Path, rows: Iterable[Any]) -> None:
    normalized = [_normalize_json(row) for row in rows]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(normalized, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
