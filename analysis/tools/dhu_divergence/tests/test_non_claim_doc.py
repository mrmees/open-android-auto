"""Content tests for docs/verification/06-capture-non-claim-boundary.md (TIER-05)."""
from __future__ import annotations

from pathlib import Path


def test_five_surfaces(repo_root: Path) -> None:
    text = (repo_root / "docs/verification/06-capture-non-claim-boundary.md").read_text()
    required_surfaces = [
        "channel_id",
        "flags",
        "Outer frame header",
        "Fragmentation",
        "Encryption",
    ]
    for surface in required_surfaces:
        assert surface in text, f"Missing surface: {surface!r}"
    # Must cross-link NOMATCH-01
    assert "NOMATCH-01" in text
    assert "05-oem-match-policy.md" in text
