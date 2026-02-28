from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DiffIssue:
    kind: str
    path: str
    expected: Any
    actual: Any


def _diff_values(expected: Any, actual: Any, path: str, out: list[DiffIssue]) -> None:
    if isinstance(expected, dict) and isinstance(actual, dict):
        keys = sorted(set(expected) | set(actual))
        for key in keys:
            child_path = f"{path}.{key}" if path else key
            if key not in actual:
                out.append(DiffIssue("missing", child_path, expected[key], None))
                continue
            if key not in expected:
                out.append(DiffIssue("extra", child_path, None, actual[key]))
                continue
            _diff_values(expected[key], actual[key], child_path, out)
        return

    if isinstance(expected, list) and isinstance(actual, list):
        max_len = max(len(expected), len(actual))
        for idx in range(max_len):
            child_path = f"{path}[{idx}]"
            if idx >= len(actual):
                out.append(DiffIssue("missing", child_path, expected[idx], None))
                continue
            if idx >= len(expected):
                out.append(DiffIssue("extra", child_path, None, actual[idx]))
                continue
            _diff_values(expected[idx], actual[idx], child_path, out)
        return

    if expected != actual:
        out.append(DiffIssue("changed", path, expected, actual))


def diff_normalized(
    expected_rows: list[dict[str, Any]],
    actual_rows: list[dict[str, Any]],
) -> list[DiffIssue]:
    out: list[DiffIssue] = []
    max_len = max(len(expected_rows), len(actual_rows))

    for idx in range(max_len):
        path = f"[{idx}]"
        if idx >= len(actual_rows):
            out.append(DiffIssue("missing", path, expected_rows[idx], None))
            continue
        if idx >= len(expected_rows):
            out.append(DiffIssue("extra", path, None, actual_rows[idx]))
            continue
        _diff_values(expected_rows[idx], actual_rows[idx], path, out)

    return out
