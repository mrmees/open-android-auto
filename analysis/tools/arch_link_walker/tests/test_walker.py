"""Walker unit tests (Phase 11 Plan 02 ARCH-04)."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from analysis.tools.arch_link_walker.walker import (
    SENTINEL,
    CALLOUT_CHANNELS,
    CALLOUT_README,
    insert_cross_link,
    walk,
)


def test_insert_clean_doc(tmp_path: Path, fixtures_dir: Path) -> None:
    """Inserting into a doc without the sentinel produces the callout block
    between # Title and ## First Section."""
    target = tmp_path / "audio.md"
    shutil.copy(fixtures_dir / "channel_doc_clean.md", target)
    assert SENTINEL not in target.read_text()
    modified = insert_cross_link(target, "channels")
    assert modified is True
    text = target.read_text()
    assert SENTINEL in text
    # Callout is BETWEEN # heading and ## heading, not at EOF
    lines = text.split("\n")
    title_idx = next(i for i, l in enumerate(lines) if l.startswith("# "))
    callout_idx = next(i for i, l in enumerate(lines) if SENTINEL in l)
    section_idx = next(i for i, l in enumerate(lines) if l.startswith("## "))
    assert title_idx < callout_idx < section_idx


def test_insert_already_present(tmp_path: Path, fixtures_dir: Path) -> None:
    """Inserting into a doc with sentinel already present returns False
    and does not modify content."""
    target = tmp_path / "with_link.md"
    shutil.copy(fixtures_dir / "channel_doc_with_link.md", target)
    original = target.read_text()
    modified = insert_cross_link(target, "channels")
    assert modified is False
    assert target.read_text() == original  # byte-identical


def test_self_exclusion(tmp_path: Path) -> None:
    """Walker skips docs/channels/architecture.md (does not insert, does not error)."""
    arch = tmp_path / "docs" / "channels" / "architecture.md"
    arch.parent.mkdir(parents=True)
    arch.write_text("# Channel Architecture Reference\n\n## Transport\n\nContent.\n")
    original = arch.read_text()
    modified = insert_cross_link(arch, "channels")
    assert modified is False
    assert arch.read_text() == original


def test_readme_variant(tmp_path: Path) -> None:
    """README.md gets docs/channels/architecture.md link path."""
    readme = tmp_path / "README.md"
    readme.write_text("# Open Android Auto\n\nDescription paragraph.\n\n## Origins\n\nContent.\n")
    insert_cross_link(readme, "readme")
    text = readme.read_text()
    assert "docs/channels/architecture.md" in text
    # Must NOT contain the bare architecture.md link (that's for channel docs)
    assert "(architecture.md)" not in text


def test_channels_variant(tmp_path: Path, fixtures_dir: Path) -> None:
    """Per-channel docs get bare architecture.md link path."""
    target = tmp_path / "audio.md"
    shutil.copy(fixtures_dir / "channel_doc_clean.md", target)
    insert_cross_link(target, "channels")
    text = target.read_text()
    assert "(architecture.md)" in text
    assert "docs/channels/architecture.md" not in text


def test_walk_returns_14_modified(tmp_path: Path, fixtures_dir: Path) -> None:
    """walk() on clean tree returns 14 True values (13 channel docs + README)."""
    # Create a mock repo tree
    channels = tmp_path / "docs" / "channels"
    channels.mkdir(parents=True)
    channel_names = [
        "audio.md", "bluetooth.md", "carcontrol.md", "coolwalk-layout.md",
        "display-routing.md", "input.md", "media.md", "nav.md", "phone.md",
        "radio.md", "sensor.md", "video.md", "wifi-projection.md",
    ]
    for name in channel_names:
        shutil.copy(fixtures_dir / "channel_doc_clean.md", channels / name)
    # Create architecture.md (should be self-excluded)
    (channels / "architecture.md").write_text("# Architecture\n\n## Section\n\nContent.\n")
    # Create README.md
    (tmp_path / "README.md").write_text("# Open Android Auto\n\nDescription.\n\n## Origins\n\nContent.\n")

    results = walk(tmp_path)
    assert len(results) == 14
    assert sum(1 for v in results.values() if v) == 14
    # architecture.md must NOT be in results (self-excluded via target list)
    assert "docs/channels/architecture.md" not in results


def test_walk_returns_14_false_on_rerun(tmp_path: Path, fixtures_dir: Path) -> None:
    """walk() on already-processed tree returns 14 False values."""
    channels = tmp_path / "docs" / "channels"
    channels.mkdir(parents=True)
    channel_names = [
        "audio.md", "bluetooth.md", "carcontrol.md", "coolwalk-layout.md",
        "display-routing.md", "input.md", "media.md", "nav.md", "phone.md",
        "radio.md", "sensor.md", "video.md", "wifi-projection.md",
    ]
    for name in channel_names:
        shutil.copy(fixtures_dir / "channel_doc_clean.md", channels / name)
    (channels / "architecture.md").write_text("# Architecture\n\n## Section\n\nContent.\n")
    (tmp_path / "README.md").write_text("# Open Android Auto\n\nDescription.\n\n## Origins\n\nContent.\n")

    # First walk
    walk(tmp_path)
    # Second walk
    results = walk(tmp_path)
    assert len(results) == 14
    assert all(v is False for v in results.values())
