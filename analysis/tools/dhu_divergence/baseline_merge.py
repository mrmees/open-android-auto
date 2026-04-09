"""DHU SDP baseline loader + union merge across multiple baselines.

Imports `oem_vw_parser.sdp_decode.decode_sdp_response` as a library and
reshapes the resulting `SdpSnapshot.services` tuple into the channel-dict
shape used by Phase 7's `sdp-values.json` (so both sides of the divergence
are structurally identical).

Discipline: this module MUST NOT modify or fork `analysis/tools/oem_vw_parser/`
— it imports the decode function and consumes the returned dataclasses.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from analysis.tools.oem_vw_parser.sdp_decode import decode_sdp_response


@dataclass(frozen=True)
class DhuBaseline:
    """A single DHU SDP baseline: name + source path + decoded channels.

    `channels` is a list of dicts `{channel_id, channel_kind, config}` mirroring
    the Phase 7 `sdp-values.json` shape so both sides of the divergence are
    structurally identical.
    """

    name: str
    path: Path
    channels: list[dict[str, Any]]


@dataclass
class MergedDhu:
    """Merged-union view of all DHU baselines.

    `kinds_to_baselines` — which baselines contributed each `channel_kind`
    (provenance for the `baselines_matched: []` field on divergence entries).
    `representative_channels` — one representative channel dict per distinct
    kind, used by the divergence computation.
    """

    baselines: list[DhuBaseline]
    kinds_to_baselines: dict[str, list[str]] = field(default_factory=dict)
    representative_channels: dict[str, dict[str, Any]] = field(default_factory=dict)


def load_dhu_baseline(bundle: Any, name: str, dhu_dir: Path) -> DhuBaseline:
    """Decode a single DHU baseline's `sdp_response.bin` via
    `oem_vw_parser.sdp_decode.decode_sdp_response`.

    Accepts a directory like `captures/general/` and looks for
    `sdp_response.bin` inside. Reshapes the decoded `SdpSnapshot.services`
    tuple into the `{channel_id, channel_kind, config}` dict shape used by
    Phase 7's sdp-values.json.
    """
    sdp_path = dhu_dir / "sdp_response.bin"
    if not sdp_path.exists():
        raise FileNotFoundError(f"DHU baseline missing sdp_response.bin: {sdp_path}")

    snapshot = decode_sdp_response(bundle, sdp_path)
    # SdpSnapshot carries a `services` tuple of DeclaredService dataclasses —
    # reshape into the phase 7 sdp-values.json channel-dict shape so both
    # sides of the divergence computation share one structural view.
    channels: list[dict[str, Any]] = []
    for svc in snapshot.services:
        channels.append(
            {
                "channel_id": svc.channel_id,
                "channel_kind": svc.channel_kind,
                "config": svc.config or {},
            }
        )
    return DhuBaseline(name=name, path=sdp_path, channels=channels)


def merge_baselines(baselines: list[DhuBaseline]) -> MergedDhu:
    """Merge multiple DHU baselines into a union view.

    - A `channel_kind` is in the merge if ANY baseline contains it.
    - `kinds_to_baselines` tracks which baselines contributed each kind (sorted).
    - `representative_channels` picks the first channel matching each kind
      (deterministic because the baselines list is ordered).
    """
    merged = MergedDhu(baselines=baselines)
    for b in baselines:
        for ch in b.channels:
            kind = ch.get("channel_kind")
            if kind is None:
                continue
            if kind not in merged.kinds_to_baselines:
                merged.kinds_to_baselines[kind] = []
                merged.representative_channels[kind] = ch
            if b.name not in merged.kinds_to_baselines[kind]:
                merged.kinds_to_baselines[kind].append(b.name)
    # Sort baseline-name lists for determinism.
    for k in merged.kinds_to_baselines:
        merged.kinds_to_baselines[k] = sorted(merged.kinds_to_baselines[k])
    return merged
