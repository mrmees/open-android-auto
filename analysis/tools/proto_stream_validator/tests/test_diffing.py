from __future__ import annotations

from analysis.tools.proto_stream_validator.diffing import diff_normalized  # type: ignore[attr-defined]
from analysis.tools.proto_stream_validator.normalize import (  # type: ignore[attr-defined]
    normalize_decoded_frames,
)


def test_normalize_decoded_frames_sorts_nested_keys():
    rows = [
        {
            "frame_index": 0,
            "direction": "Phone->HU",
            "channel_id": 0,
            "message_id": 1,
            "message_type": "oaa.proto.messages.Foo",
            "decoded": {
                "z": 1,
                "a": {
                    "y": 2,
                    "x": 1,
                },
            },
        }
    ]

    normalized = normalize_decoded_frames(rows)

    assert list(normalized[0]["decoded"].keys()) == ["a", "z"]
    assert list(normalized[0]["decoded"]["a"].keys()) == ["x", "y"]


def test_diff_reports_field_path_changes():
    expected = [{"frame_index": 0, "decoded": {"status": "OK"}}]
    actual = [{"frame_index": 0, "decoded": {"status": "ERROR"}}]

    diffs = diff_normalized(expected, actual)

    assert any(diff.path == "[0].decoded.status" and diff.kind == "changed" for diff in diffs)


def test_diff_reports_missing_rows():
    expected = [{"frame_index": 0}, {"frame_index": 1}]
    actual = [{"frame_index": 0}]

    diffs = diff_normalized(expected, actual)

    assert any(diff.path == "[1]" and diff.kind == "missing" for diff in diffs)
