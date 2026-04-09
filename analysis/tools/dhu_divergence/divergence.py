"""VW-vs-merged-DHU SDP divergence computation.

Produces three kinds of divergences at channel_kind granularity:
  - service_only_in_vw: a kind present in VW SDP but in no DHU baseline
  - service_only_in_dhu: a kind present in at least one DHU baseline but not VW
  - config_mismatch: reserved for future; v1.5 only emits service-level diffs
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .baseline_merge import MergedDhu

DivergenceKind = Literal["service_only_in_vw", "service_only_in_dhu", "config_mismatch"]


@dataclass(frozen=True)
class Divergence:
    """A single divergence between VW SDP and merged DHU baselines."""

    kind: DivergenceKind
    service: str                       # channel_kind string
    vw_config: dict[str, Any] | None
    dhu_configs: list[dict[str, Any]]  # list because merge may carry multiple
    baselines_matched: list[str]       # which DHU baselines have this service


def load_vw_channels(vw_sdp_values: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract the VW channels list from Phase 7's sdp-values.json structure.

    Expects: top-level `response` dict with `channels` list.
    """
    response = vw_sdp_values.get("response", {})
    return list(response.get("channels", []))


def compute_divergences(
    vw_channels: list[dict[str, Any]],
    merged_dhu: MergedDhu,
) -> list[Divergence]:
    """Compute VW-vs-DHU SDP divergences at the channel_kind granularity.

    Returns:
      - service_only_in_vw: each kind present in VW but not in any DHU baseline
      - service_only_in_dhu: each kind present in merged DHU but not in VW
      - (config_mismatch is reserved for future; v1.5 only emits service-level diffs)
    """
    vw_kinds = {
        ch.get("channel_kind") for ch in vw_channels if ch.get("channel_kind")
    }
    dhu_kinds = set(merged_dhu.kinds_to_baselines.keys())

    # Build per-kind representative for VW.
    vw_by_kind: dict[str, dict[str, Any]] = {}
    for ch in vw_channels:
        k = ch.get("channel_kind")
        if k and k not in vw_by_kind:
            vw_by_kind[k] = ch

    divergences: list[Divergence] = []

    # Services in VW but not in any DHU baseline.
    for kind in sorted(vw_kinds - dhu_kinds):
        divergences.append(
            Divergence(
                kind="service_only_in_vw",
                service=kind,
                vw_config=vw_by_kind[kind].get("config", {}),
                dhu_configs=[],
                baselines_matched=[],
            )
        )

    # Services in DHU but not in VW.
    for kind in sorted(dhu_kinds - vw_kinds):
        divergences.append(
            Divergence(
                kind="service_only_in_dhu",
                service=kind,
                vw_config=None,
                dhu_configs=[merged_dhu.representative_channels[kind].get("config", {})],
                baselines_matched=merged_dhu.kinds_to_baselines[kind],
            )
        )

    return divergences


def services_only_in_vw(divergences: list[Divergence]) -> list[str]:
    """Return sorted list of services present only in VW."""
    return sorted(d.service for d in divergences if d.kind == "service_only_in_vw")


def services_only_in_dhu(divergences: list[Divergence]) -> list[str]:
    """Return sorted list of services present only in DHU."""
    return sorted(d.service for d in divergences if d.kind == "service_only_in_dhu")
