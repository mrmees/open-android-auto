"""REQUIREMENTS.md TIER-01 wording correction (oem_evidence -> platinum_evidence).

Pitfall 7 defense from 09-RESEARCH.md: the TIER-01 text correction is the
easiest edit to miss.
"""
from __future__ import annotations

from pathlib import Path


def test_tier_01_text_fix(repo_root: Path) -> None:
    text = (repo_root / ".planning/REQUIREMENTS.md").read_text()
    assert "oem_evidence" not in text, (
        "REQUIREMENTS.md still contains 'oem_evidence' — TIER-01 text correction missed. "
        "Expected: all occurrences replaced with 'platinum_evidence'."
    )
    # Positive check: the replacement MUST be present
    assert "platinum_evidence" in text, (
        "REQUIREMENTS.md must contain 'platinum_evidence' after the TIER-01 rename."
    )
