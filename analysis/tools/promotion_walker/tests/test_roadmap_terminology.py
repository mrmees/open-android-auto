from __future__ import annotations
import re
from pathlib import Path


def test_no_oem_evidence_in_roadmap(repo_root: Path) -> None:
    """ROADMAP.md must contain zero 'oem_evidence' occurrences (Phase 9 terminology retired)."""
    text = (repo_root / ".planning/ROADMAP.md").read_text()
    count = text.count("oem_evidence")
    assert count == 0, f"ROADMAP.md contains {count} 'oem_evidence' occurrences; expected 0"


def test_no_gold_single_oem_in_roadmap(repo_root: Path) -> None:
    """ROADMAP.md must contain zero 'Gold/single-OEM' or 'Gold / single-OEM' occurrences."""
    text = (repo_root / ".planning/ROADMAP.md").read_text()
    pattern = re.compile(r"Gold\s*/\s*single-OEM")
    hits = pattern.findall(text)
    assert not hits, f"ROADMAP.md contains {len(hits)} 'Gold / single-OEM' occurrences: {hits}"


def test_platinum_single_oem_present(repo_root: Path) -> None:
    """ROADMAP.md must contain at least one 'Platinum / single-OEM' -- the new terminology."""
    text = (repo_root / ".planning/ROADMAP.md").read_text()
    assert "Platinum / single-OEM" in text, \
        "ROADMAP.md must mention 'Platinum / single-OEM' after terminology fix"


def test_platinum_evidence_present(repo_root: Path) -> None:
    """ROADMAP.md must reference platinum_evidence (the new evidence type name)."""
    text = (repo_root / ".planning/ROADMAP.md").read_text()
    assert "platinum_evidence" in text, \
        "ROADMAP.md must mention 'platinum_evidence' after terminology fix"
