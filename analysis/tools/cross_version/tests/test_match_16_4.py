"""Tests for the two-pass 16.4 class identity matcher.

Wave 0 stubs: xfail-marked snapshot test pending Task 3 matcher implementation.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.xfail(strict=True, reason="Pending Task 3 — matcher impl")
def test_match_snapshot() -> None:
    """Snapshot test: matcher output against real 4 APK DBs matches committed snapshot.

    Source of truth: analysis/tools/cross_version/tests/fixtures/match_snapshot.json
    Regeneration: `PYTHONPATH=. python3 -m analysis.tools.cross_version.match_16_4 > analysis/tools/cross_version/tests/fixtures/match_snapshot.json`
    Fail message includes: which DB, run date, and regen command.
    """
    from analysis.tools.cross_version.match_16_4 import run_matcher

    snapshot = json.loads((FIXTURES / "match_snapshot.json").read_text())
    result = run_matcher()
    # Allow ±5 slack on the total committable (empirical baseline from 08-RESEARCH.md)
    assert 88 <= result["total_committable"] <= 98, (
        f"Matcher total_committable ({result['total_committable']}) outside expected range [88, 98].\n"
        f"Baseline: 93 (08-RESEARCH.md empirical sweep against 16.4.661014 DB).\n"
        f"Regenerate: PYTHONPATH=. python3 -m analysis.tools.cross_version.match_16_4 > "
        f"analysis/tools/cross_version/tests/fixtures/match_snapshot.json"
    )
    # Enums are perfectly stable — all 5 must match uniquely.
    assert result["pass1_enum_commits"] == snapshot["pass1_enum_commits"], (
        f"Enum commit count drift: expected {snapshot['pass1_enum_commits']}, got {result['pass1_enum_commits']}"
    )
