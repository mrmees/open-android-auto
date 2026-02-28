from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from analysis.tools.proto_stream_validator import run  # type: ignore[attr-defined]

try:
    _GOOGLE_PROTOBUF_AVAILABLE = importlib.util.find_spec("google.protobuf") is not None
except ModuleNotFoundError:
    _GOOGLE_PROTOBUF_AVAILABLE = False
_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def test_bless_requires_reason(tmp_path):
    capture = tmp_path / "capture.jsonl"
    capture.write_text("", encoding="utf-8")
    baseline = tmp_path / "baseline.json"

    rc = run.main([
        "--capture",
        str(capture),
        "--baseline",
        str(baseline),
        "--bless",
    ])

    assert rc != 0
    assert not baseline.exists()


def test_validate_fails_on_diff_and_does_not_write_baseline(tmp_path, monkeypatch):
    capture = tmp_path / "capture.jsonl"
    capture.write_text("", encoding="utf-8")
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps([{"frame_index": 0, "decoded": {"status": "OK"}}], indent=2) + "\n",
        encoding="utf-8",
    )
    original = baseline.read_text(encoding="utf-8")

    monkeypatch.setattr(
        run,
        "build_normalized_rows",
        lambda capture_path, repo_root: [
            {
                "frame_index": 0,
                "decoded": {"status": "ERROR"},
            }
        ],
    )

    rc = run.main([
        "--capture",
        str(capture),
        "--baseline",
        str(baseline),
    ])

    assert rc == 1
    assert baseline.read_text(encoding="utf-8") == original


def test_bless_writes_updated_baseline(tmp_path, monkeypatch):
    capture = tmp_path / "capture.jsonl"
    capture.write_text("", encoding="utf-8")
    baseline = tmp_path / "baseline.json"

    monkeypatch.setattr(
        run,
        "build_normalized_rows",
        lambda capture_path, repo_root: [
            {
                "frame_index": 0,
                "decoded": {"minor": 7, "major": 1},
            }
        ],
    )

    rc = run.main([
        "--capture",
        str(capture),
        "--baseline",
        str(baseline),
        "--bless",
        "--reason",
        "intentional proto update",
    ])

    assert rc == 0
    written = json.loads(baseline.read_text(encoding="utf-8"))
    assert written[0]["decoded"] == {"major": 1, "minor": 7}


@pytest.mark.skipif(
    not _GOOGLE_PROTOBUF_AVAILABLE,
    reason="google.protobuf runtime not available",
)
def test_golden_fixture_passes_validation():
    capture = _FIXTURES_DIR / "non_media_sample.jsonl"
    baseline = _FIXTURES_DIR / "non_media_sample.normalized.json"

    rc = run.main(
        [
            "--capture",
            str(capture),
            "--baseline",
            str(baseline),
            "--repo-root",
            str(Path.cwd()),
        ]
    )

    assert rc == 0


@pytest.mark.skipif(
    not _GOOGLE_PROTOBUF_AVAILABLE,
    reason="google.protobuf runtime not available",
)
def test_golden_fixture_detects_drift(tmp_path):
    capture = _FIXTURES_DIR / "non_media_sample.jsonl"
    baseline = tmp_path / "baseline-mutated.json"
    baseline.write_text(
        json.dumps(
            [
                {
                    "channel_id": 0,
                    "decoded": {"timestamp": "2"},
                    "direction": "Phone->HU",
                    "frame_index": 0,
                    "message_id": 11,
                    "message_name": "PING_REQUEST",
                    "message_type": "oaa.proto.messages.PingRequest",
                }
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    rc = run.main(
        [
            "--capture",
            str(capture),
            "--baseline",
            str(baseline),
            "--repo-root",
            str(Path.cwd()),
        ]
    )

    assert rc == 1
