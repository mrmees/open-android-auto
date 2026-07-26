"""Tests for the cross_version.run CLI entry point.

XVER-01: --db-16_4 flag wiring and _find_db canonical-build lock.
"""
from __future__ import annotations

from pathlib import Path

import pytest


def test_db_16_4_flag(tmp_path: Path) -> None:
    """build_parser() must accept --db-16_4 and store it at args.db_16_4."""
    from analysis.tools.cross_version.run import build_parser

    parser = build_parser()
    fake = tmp_path / "fake.db"
    args = parser.parse_args(["--db-16_4", str(fake)])
    assert args.db_16_4 == fake


def test_find_db_164_prefers_canonical_build(tmp_path: Path, monkeypatch) -> None:
    """_find_db selects the canonical 16.4 build from a fixture tree."""
    from analysis.tools.cross_version import run

    canonical = (
        tmp_path
        / "android_auto_16.4.661014-release_164661014"
        / "apk-index"
        / "sqlite"
        / "apk_index.db"
    )
    canonical.parent.mkdir(parents=True)
    canonical.touch()
    monkeypatch.setattr(run, "_ANALYSIS", tmp_path)

    assert run._find_db("16.4") == canonical


@pytest.mark.apk_index_integration
def test_find_db_164() -> None:
    """_find_db must resolve the canonical 661014 build directory.

    Note: the existing _find_db helper is version-agnostic via glob — it already
    resolves 16.4 correctly without any code change. This test confirms the
    canonical-build lock: it MUST return the 661014 path, NOT 661034. Phase 8
    uses 661014 for all bulk analysis; 661034 is referenced only for the
    XVER-05 manual-JADX reproducibility-gap doc.
    """
    from analysis.tools.cross_version.run import _find_db

    result = _find_db("16.4")
    if result is None:
        pytest.skip("missing ignored APK-index SQLite snapshot: Android Auto 16.4.661014")
    s = str(result)
    assert "16.4" in s
    # Canonical build is 661014, NOT 661034 — locked by phase decision.
    assert "661014" in s, f"_find_db('16.4') must resolve to the 661014 build, got {s}"
