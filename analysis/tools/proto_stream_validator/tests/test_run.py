from __future__ import annotations

import json

from analysis.tools.proto_stream_validator import run  # type: ignore[attr-defined]


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
