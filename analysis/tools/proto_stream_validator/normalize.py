from __future__ import annotations

from typing import Any


def normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    return value


def normalize_decoded_frames(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_value(row) for row in rows]
