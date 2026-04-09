"""Cross-link walker for Phase 9 TIER-05 non-claim callouts.

Inserts the locked cross-link callout block into a small, explicit set of
channel docs so that readers who land on a doc that discusses framing-layer
surfaces (`channel_id`, `flags`, outer frame header layout) see the scope
boundary documented in `docs/verification/06-capture-non-claim-boundary.md`.

Idempotent by sentinel-substring detection: the first non-blank line of the
callout block is used as the idempotency key. Running the walker a second
time on an already-processed tree produces zero file changes.

The walker self-excludes `docs/verification/06-capture-non-claim-boundary.md`
(the destination of the cross-links). The 06 doc contains the sentinel as its
own content by design, not as an inserted callout, and the walker raises
ValueError if asked to edit it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

# Locked cross-link callout block (verbatim from 09-CONTEXT.md).
# First non-blank line is the SENTINEL used as the idempotency key.
SENTINEL = "> **Capture evidence boundary:** The VW capture cannot validate claims about this surface."

CALLOUT_CHANNELS_VARIANT = (
    "\n"
    "> **Capture evidence boundary:** The VW capture cannot validate claims about this surface.\n"
    "> The on-phone hook lives inside the AA framing layer; `channel_id`, `flags`, and outer\n"
    "> frame header semantics are below the hook's observation point. See\n"
    "> [06-capture-non-claim-boundary.md](../verification/06-capture-non-claim-boundary.md).\n"
)

CALLOUT_CHANNEL_MAP_VARIANT = (
    "\n"
    "> **Capture evidence boundary:** The VW capture cannot validate claims about this surface.\n"
    "> The on-phone hook lives inside the AA framing layer; `channel_id`, `flags`, and outer\n"
    "> frame header semantics are below the hook's observation point. See\n"
    "> [06-capture-non-claim-boundary.md](verification/06-capture-non-claim-boundary.md).\n"
)

# Explicit walker target list. Relative to repo root. DO NOT discover via glob.
WALKER_TARGETS: dict[str, Literal["channels", "channel_map"]] = {
    "docs/channels/wifi-projection.md": "channels",
    "docs/channels/audio.md":           "channels",
    "docs/channels/video.md":           "channels",
    "docs/channels/sensor.md":          "channels",
    "docs/channel-map.md":              "channel_map",
}

# Walker self-exclusion — file that contains the sentinel by design.
WALKER_EXCLUDE = {"docs/verification/06-capture-non-claim-boundary.md"}


def insert_cross_link(doc_path: Path, variant: Literal["channels", "channel_map"]) -> bool:
    """Insert the callout block into doc_path if not already present.

    Returns True if the file was modified, False if it was a no-op.

    Self-exclusion: raises ValueError if doc_path matches any entry in
    WALKER_EXCLUDE. The comparison is by path suffix to be robust against
    absolute/relative paths and tmp_path fixtures in tests.
    """
    # Self-exclusion check — compare by suffix to be path-shape-agnostic.
    suffix = str(doc_path).replace("\\", "/")
    for excluded in WALKER_EXCLUDE:
        if suffix.endswith(excluded):
            raise ValueError(f"Walker refusing to edit self-excluded file: {doc_path}")

    text = doc_path.read_text(encoding="utf-8")
    if SENTINEL in text:
        return False  # Already has callout, no-op. This is the idempotency key.

    callout = CALLOUT_CHANNELS_VARIANT if variant == "channels" else CALLOUT_CHANNEL_MAP_VARIANT
    new_text = text.rstrip() + "\n" + callout
    doc_path.write_text(new_text, encoding="utf-8")
    return True


def walk(repo_root: Path) -> dict[str, bool]:
    """Run the walker against every target in WALKER_TARGETS.

    Returns a mapping {relative_path: was_modified} so callers can report.
    Raises FileNotFoundError if any target is missing.
    """
    results: dict[str, bool] = {}
    for rel, variant in WALKER_TARGETS.items():
        doc = repo_root / rel
        if not doc.exists():
            raise FileNotFoundError(f"Walker target missing: {rel}")
        results[rel] = insert_cross_link(doc, variant)
    return results
