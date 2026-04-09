"""Walker unit tests (Phase 9 Plan 01 TIER-05)."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from analysis.tools.cross_link_walker.walker import (
    SENTINEL,
    insert_cross_link,
    walk,
)


def test_insert_wifi_projection(tmp_path: Path, fixtures_dir: Path) -> None:
    """Walker inserts callout into a clean fixture doc."""
    target = tmp_path / "wifi-projection.md"
    shutil.copy(fixtures_dir / "channel_doc_clean.md", target)
    assert SENTINEL not in target.read_text()
    modified = insert_cross_link(target, "channels")
    assert modified is True
    text = target.read_text()
    assert SENTINEL in text
    assert "../verification/06-capture-non-claim-boundary.md" in text


def test_relative_path_channel_map(tmp_path: Path, fixtures_dir: Path) -> None:
    """docs/channel-map.md variant uses 'verification/' (NO ../ prefix)."""
    target = tmp_path / "channel-map.md"
    shutil.copy(fixtures_dir / "channel_doc_clean.md", target)
    insert_cross_link(target, "channel_map")
    text = target.read_text()
    assert "[06-capture-non-claim-boundary.md](verification/06-capture-non-claim-boundary.md)" in text
    assert "../verification/06-capture-non-claim-boundary.md" not in text


def test_relative_path_channel_docs(tmp_path: Path, fixtures_dir: Path) -> None:
    """docs/channels/*.md variant uses '../verification/' prefix."""
    target = tmp_path / "wifi-projection.md"
    shutil.copy(fixtures_dir / "channel_doc_clean.md", target)
    insert_cross_link(target, "channels")
    text = target.read_text()
    assert "[06-capture-non-claim-boundary.md](../verification/06-capture-non-claim-boundary.md)" in text


def test_self_exclusion(tmp_path: Path, fixtures_dir: Path) -> None:
    """Walker refuses to touch docs/verification/06-capture-non-claim-boundary.md."""
    excluded_target = tmp_path / "docs" / "verification" / "06-capture-non-claim-boundary.md"
    excluded_target.parent.mkdir(parents=True)
    shutil.copy(fixtures_dir / "non_claim_doc.md", excluded_target)
    original_content = excluded_target.read_text()
    with pytest.raises(ValueError, match="self-excluded"):
        insert_cross_link(excluded_target, "channels")
    # File must be unchanged after the refused call
    assert excluded_target.read_text() == original_content


def test_noop_on_existing(tmp_path: Path, fixtures_dir: Path) -> None:
    """Walker no-ops on a doc that already has the sentinel."""
    target = tmp_path / "with_link.md"
    shutil.copy(fixtures_dir / "channel_doc_with_link.md", target)
    original = target.read_text()
    modified = insert_cross_link(target, "channels")
    assert modified is False
    assert target.read_text() == original  # byte-identical


def test_live_rerun_git_clean(repo_root: Path) -> None:
    """After running the walker against the real docs tree, a second run must
    be a pure no-op. Called 'live_rerun_git_clean' because the assertion is
    'a second walk does nothing new' — which means git status stays clean
    across re-runs.
    """
    # First walk: may or may not modify files depending on prior state.
    walk(repo_root)
    # Second walk: every target must report no modification.
    results = walk(repo_root)
    for rel, was_modified in results.items():
        assert was_modified is False, (
            f"Second walk modified {rel} - walker is not idempotent"
        )
