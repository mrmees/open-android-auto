from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis.tools.oem_vw_parser.io import (
    CAPTURE_VERSION_NATIVE_INTERCEPTOR,
    load_dhu_capture,
    load_session_json,
    load_vw_capture,
)
from analysis.tools.oem_vw_parser.models import UnifiedRecord
from analysis.tools.oem_vw_parser.normalize import normalize_dhu_direction


VW_SESSION = Path("captures/oem-vw-mib3oi-2026-04-06/session.json")


def test_capture_version_numeric(tmp_path):
    """capture_version is the JSON integer 5, not the string "v5"."""
    raw = load_session_json(VW_SESSION)
    assert isinstance(raw["capture_version"], int)
    assert raw["capture_version"] == CAPTURE_VERSION_NATIVE_INTERCEPTOR == 5

    # A session with the string "v5" must be rejected.
    fake = tmp_path / "fake_session.json"
    fake.write_text(json.dumps({"capture_version": "v5"}))
    with pytest.raises(ValueError, match="capture_version must be int"):
        load_session_json(fake)

    # A session with an unsupported integer version must also be rejected.
    fake_v6 = tmp_path / "fake_v6.json"
    fake_v6.write_text(json.dumps({"capture_version": 6}))
    with pytest.raises(ValueError, match="unsupported capture_version"):
        load_session_json(fake_v6)


def test_load_vw_jsonl_roundtrip(vw_micro_path):
    records = list(load_vw_capture(vw_micro_path, capture_id="vw_micro"))
    assert len(records) >= 25
    for r in records:
        assert isinstance(r, UnifiedRecord)
        assert r.direction in {"in", "out"}
        # payload starts with the 2-byte big-endian msg_type prefix
        assert r.payload[0] == (r.msg_type >> 8) & 0xFF
        assert r.payload[1] == r.msg_type & 0xFF
        assert r.channel_id is None
        assert r.flags is None
        assert r.service_type is None
        assert r.capture_id == "vw_micro"


def test_load_dhu_jsonl_roundtrip(dhu_micro_path, dhu_channel_map_path):
    records = list(
        load_dhu_capture(
            dhu_micro_path,
            capture_id="dhu_micro",
            channel_map_path=dhu_channel_map_path,
        )
    )
    assert len(records) >= 25
    for r in records:
        assert isinstance(r, UnifiedRecord)
        # NORMALIZED — never raw "dhu" / "phone"
        assert r.direction in {"in", "out"}
        assert isinstance(r.channel_id, int)
    # Explicit channel map was consumed → at least one record has a service_type
    assert any(r.service_type is not None for r in records)


def test_load_dhu_jsonl_no_channel_map_falls_back(dhu_micro_path, caplog):
    """When no channel_map is provided AND no adjacent channel_map.json exists,
    the loader logs a WARNING and proceeds with empty service_types."""
    import logging

    caplog.set_level(logging.WARNING, logger="analysis.tools.oem_vw_parser.io")
    records = list(load_dhu_capture(dhu_micro_path, capture_id="dhu_micro"))
    assert len(records) >= 25
    for r in records:
        assert r.msg_type is not None
        assert r.direction in {"in", "out"}
        assert isinstance(r.channel_id, int)
        assert r.service_type is None
    # WARNING log emitted referencing channel_map
    warning_msgs = [rec.getMessage() for rec in caplog.records if rec.levelname == "WARNING"]
    assert any("channel_map" in m for m in warning_msgs), (
        f"expected a WARNING about channel_map, got: {warning_msgs}"
    )


def test_dhu_direction_normalized():
    assert normalize_dhu_direction("dhu") == "in"
    assert normalize_dhu_direction("phone") == "out"
    with pytest.raises(ValueError):
        normalize_dhu_direction("junk")
