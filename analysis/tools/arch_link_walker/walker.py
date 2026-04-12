"""Architecture cross-link walker for Phase 11.

Inserts the locked callout block into per-channel docs and README so
readers see the architecture reference link at the top of every channel doc.

Different from Phase 9's cross_link_walker:
  - Phase 9: APPENDS callout to END of file
  - Phase 11: INSERTS callout between first `# ` heading and first `## ` heading
  - Phase 11: Different sentinel, different targets, different scope

Idempotent by sentinel-substring detection.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

# Locked sentinel -- first non-blank line of the callout block.
SENTINEL = "> **Architecture context:** This channel is part of the Android Auto multiplexed"

# Two callout variants: different link paths.
# em-dashes (\u2014) match CONTEXT.md exactly.
CALLOUT_CHANNELS = (
    "> **Architecture context:** This channel is part of the Android Auto multiplexed\n"
    "> protocol. For the overall architecture \u2014 framing, SDP binding, capability\n"
    "> negotiation \u2014 see [Channel Architecture Reference](architecture.md).\n"
)

CALLOUT_README = (
    "> **Architecture context:** This channel is part of the Android Auto multiplexed\n"
    "> protocol. For the overall architecture \u2014 framing, SDP binding, capability\n"
    "> negotiation \u2014 see [Channel Architecture Reference](docs/channels/architecture.md).\n"
)

# Explicit walker target list. Values are "channels" or "readme" to select the callout variant.
WALKER_TARGETS: dict[str, Literal["channels", "readme"]] = {
    "docs/channels/audio.md": "channels",
    "docs/channels/bluetooth.md": "channels",
    "docs/channels/carcontrol.md": "channels",
    "docs/channels/coolwalk-layout.md": "channels",
    "docs/channels/display-routing.md": "channels",
    "docs/channels/input.md": "channels",
    "docs/channels/media.md": "channels",
    "docs/channels/nav.md": "channels",
    "docs/channels/phone.md": "channels",
    "docs/channels/radio.md": "channels",
    "docs/channels/sensor.md": "channels",
    "docs/channels/video.md": "channels",
    "docs/channels/wifi-projection.md": "channels",
    "README.md": "readme",
}

# Self-exclusion -- don't cross-link architecture.md to itself.
WALKER_EXCLUDE = {"docs/channels/architecture.md"}


def insert_cross_link(doc_path: Path, variant: Literal["channels", "readme"]) -> bool:
    """Insert callout block between first # heading and first ## heading.

    Returns True if file was modified, False if sentinel already present
    or file is self-excluded.
    """
    # Self-exclusion check -- compare by suffix to be path-shape-agnostic.
    suffix = str(doc_path).replace("\\", "/")
    for excluded in WALKER_EXCLUDE:
        if suffix.endswith(excluded):
            return False  # Silently skip (architecture.md is a known self-exclusion)

    text = doc_path.read_text(encoding="utf-8")
    if SENTINEL in text:
        return False

    callout = CALLOUT_CHANNELS if variant == "channels" else CALLOUT_README
    lines = text.split("\n")

    # Find first ## heading -- this is where we insert BEFORE
    insert_idx = None
    for i, line in enumerate(lines):
        if line.startswith("## "):
            insert_idx = i
            break

    if insert_idx is None:
        # Fallback: insert after first # heading + blank line
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_idx = i + 2  # After heading + blank line
                break

    if insert_idx is None:
        return False  # No heading found, skip

    # Insert: callout lines + blank line before the ## heading
    callout_lines = callout.rstrip("\n").split("\n")
    lines[insert_idx:insert_idx] = callout_lines + [""]

    doc_path.write_text("\n".join(lines), encoding="utf-8")
    return True


def walk(repo_root: Path) -> dict[str, bool]:
    """Run walker against all targets. Returns {rel_path: was_modified}."""
    results: dict[str, bool] = {}
    for rel, variant in WALKER_TARGETS.items():
        doc = repo_root / rel
        if not doc.exists():
            raise FileNotFoundError(f"Walker target missing: {rel}")
        results[rel] = insert_cross_link(doc, variant)
    return results
