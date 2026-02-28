from __future__ import annotations

import json

import pytest

from analysis.tools.proto_stream_validator.io import (  # type: ignore[attr-defined]
    load_capture_jsonl,
    write_normalized_baseline,
)


def test_load_capture_jsonl_reads_frames(tmp_path):
    path = tmp_path / "capture.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts_ms": 1,
                        "direction": "Phone->HU",
                        "channel_id": 0,
                        "message_id": 1,
                        "message_name": "VERSION_REQUEST",
                        "payload_hex": "00010007",
                    }
                ),
                json.dumps(
                    {
                        "ts_ms": 2,
                        "direction": "HU->Phone",
                        "channel_id": 0,
                        "message_id": 2,
                        "message_name": "VERSION_RESPONSE",
                        "payload_hex": "000100070000",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    frames = load_capture_jsonl(path)

    assert len(frames) == 2
    assert frames[0].message_id == 1
    assert frames[1].direction == "HU->Phone"


def test_load_capture_jsonl_rejects_malformed_line(tmp_path):
    path = tmp_path / "capture.jsonl"
    path.write_text('{"ts_ms":1}\nnot-json\n', encoding="utf-8")

    with pytest.raises(ValueError):
        load_capture_jsonl(path)


def test_write_normalized_baseline_is_deterministic(tmp_path):
    baseline = tmp_path / "baseline.json"
    rows = [
        {
            "frame_index": 0,
            "direction": "Phone->HU",
            "channel_id": 0,
            "message_id": 1,
            "message_type": "oaa.proto.messages.VersionRequest",
            "decoded": {"minor_version": 7, "major_version": 1},
        }
    ]

    write_normalized_baseline(baseline, rows)

    first = baseline.read_text(encoding="utf-8")
    write_normalized_baseline(baseline, rows)
    second = baseline.read_text(encoding="utf-8")

    assert first == second
    payload = json.loads(first)
    assert payload[0]["decoded"] == {"major_version": 1, "minor_version": 7}
