"""Walker idempotency test (Phase 11 Plan 02)."""
from __future__ import annotations

import shutil
from pathlib import Path

from analysis.tools.arch_link_walker.walker import insert_cross_link, walk


def test_double_run_byte_identical(tmp_path: Path, fixtures_dir: Path) -> None:
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


def test_live_rerun_git_clean(repo_root: Path) -> None:
    """After running the walker against the real docs tree, a second run must
    be a pure no-op -- byte-identical files, no git diff."""
    # First walk: may or may not modify files depending on prior state.
    walk(repo_root)
    # Second walk: every target must report no modification.
    results = walk(repo_root)
    for rel, was_modified in results.items():
        assert was_modified is False, (
            f"Second walk modified {rel} -- walker is not idempotent"
        )
