"""Cross-link walker stubs for Phase 9 TIER-05 non-claim callouts.

Wave 0 stub — Wave 1 task 09-01-walker-impl replaces `insert_cross_link` with
the real implementation. The constants (SENTINEL, CALLOUT_*, WALKER_TARGETS,
WALKER_EXCLUDE) are defined here so downstream tests can import them at
collection time even before the implementation lands.
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
    """Stub — Wave 1 task 09-01-walker-impl will implement."""
    raise NotImplementedError("Wave 1 task 09-01-walker-impl will implement insert_cross_link")
