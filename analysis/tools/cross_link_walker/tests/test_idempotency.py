"""Walker idempotency test (Phase 9 Plan 01 TIER-05)."""
from __future__ import annotations

import shutil
from pathlib import Path

from analysis.tools.cross_link_walker.walker import insert_cross_link


def test_double_run_identical(tmp_path: Path, fixtures_dir: Path) -> None:
    """Running the walker twice on a clean fixture produces byte-identical output."""
    target = tmp_path / "doc.md"
    shutil.copy(fixtures_dir / "channel_doc_clean.md", target)

    # First run inserts.
    assert insert_cross_link(target, "channels") is True
    after_first = target.read_text()

    # Second run no-ops.
    assert insert_cross_link(target, "channels") is False
    after_second = target.read_text()

    assert after_first == after_second
