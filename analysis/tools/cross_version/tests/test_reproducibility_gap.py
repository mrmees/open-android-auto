"""Tests for the manual-JADX reproducibility-gap doc (XVER-05).

Wave 0 stubs: xfail-marked tests for verbatim non-claim bullets, PROVENANCE link,
and 5 salvaged-class name presence. Task 5 will unxfail these.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
DOC = REPO_ROOT / "analysis" / "reports" / "cross-version" / "manual-jadx-reproducibility-gap.md"


@pytest.mark.xfail(strict=True, reason="Pending Task 5 — reproducibility gap doc")
def test_five_non_claims() -> None:
    """All 5 verbatim non-claim bullet headers must be present."""
    text = DOC.read_text()
    assert "**No cross-version structural comparison.**" in text
    assert "**No byte-match reproducibility.**" in text
    assert "**No confidence tier promotion.**" in text
    assert "**No methodology validation.**" in text
    assert "**No build-number claim.**" in text


@pytest.mark.xfail(strict=True, reason="Pending Task 5 — reproducibility gap doc")
def test_provenance_link() -> None:
    """Doc must reference PROVENANCE.md and the 16.4.661034 manual-jadx path."""
    text = DOC.read_text()
    assert "PROVENANCE.md" in text
    assert "analysis/aa_apk_16.4.661034_apkm/manual-jadx" in text


@pytest.mark.xfail(strict=True, reason="Pending Task 5 — reproducibility gap doc")
def test_class_names() -> None:
    """All 5 salvaged class names must be present."""
    text = DOC.read_text()
    for cls in ["rcn", "rco", "rcp", "rdt", "red"]:
        assert cls in text, f"Missing salvaged class name: {cls}"
