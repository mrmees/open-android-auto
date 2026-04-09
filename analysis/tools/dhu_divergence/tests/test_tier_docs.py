"""Content tests for 01-confidence-tiers.md and 02-audit-trail-format.md (TIER-02)."""
from __future__ import annotations

from pathlib import Path


def test_single_oem_badge_format(repo_root: Path) -> None:
    text = (repo_root / "docs/verification/01-confidence-tiers.md").read_text()
    # The exact rendered badge format MUST appear verbatim
    assert "Platinum / single-OEM" in text, (
        "01-confidence-tiers.md must contain 'Platinum / single-OEM' verbatim"
    )
    # And the tier redefinition language
    assert "strictly above Gold" in text, (
        "01 must say Platinum is 'strictly above Gold'"
    )
    assert "deep-trace APK" in text, (
        "01 must redefine Gold as 'deep-trace APK ...'"
    )
    # Must cross-link the new docs
    assert "05-oem-match-policy.md" in text
    assert "06-capture-non-claim-boundary.md" in text
    # The single-OEM trap must be named
    assert "single-OEM trap" in text


def test_audit_format_tier_list_updated(repo_root: Path) -> None:
    text = (repo_root / "docs/verification/02-audit-trail-format.md").read_text()
    # All 5 tiers + retracted must appear
    for tier in ["unverified", "bronze", "silver", "gold", "platinum", "retracted"]:
        assert tier in text, f"02-audit-trail-format.md missing tier {tier!r}"
    # platinum_evidence must be added to the evidence types
    assert "platinum_evidence" in text
