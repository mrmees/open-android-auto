"""Parametric backstop: all 6 retracted sidecars validate against the migrated schema.

Pitfall 5 / 8 defense from 09-RESEARCH.md: CONTEXT.md undercounted retracted
sidecars as 1; there are 6. Every one of them must validate cleanly after the
Phase 9 schema migration.
"""
from __future__ import annotations

from pathlib import Path

import jsonschema
import pytest
import yaml

RETRACTED = [
    "oaa/media/MediaStatusListData.audit.yaml",
    "oaa/media/MediaPlaybackCommandMessage.audit.yaml",
    "oaa/media/MediaTrackIdentifierData.audit.yaml",
    "oaa/video/VideoFocusNotificationMessage.audit.yaml",
    "oaa/video/VideoFocusModeMessage.audit.yaml",
    "oaa/wifi/WifiProjectionChannelData.audit.yaml",
]


@pytest.mark.parametrize("sidecar_path", RETRACTED)
def test_retracted_sidecar_validates(sidecar_path: str, repo_root: Path, schema: dict) -> None:
    p = repo_root / sidecar_path
    assert p.exists(), f"Expected retracted sidecar at {sidecar_path} but file is missing"
    data = yaml.safe_load(p.read_text())
    assert data.get("confidence") == "retracted", (
        f"{sidecar_path} has confidence={data.get('confidence')}, expected retracted"
    )
    jsonschema.validate(data, schema)
