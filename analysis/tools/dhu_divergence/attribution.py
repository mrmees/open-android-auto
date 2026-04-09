"""Classify each VW-vs-DHU divergence as version | oem | ambiguous.

Uses Phase 8's `16-4-delta-report.json` (`new_in_16_4` / `removed_in_16_4`)
as the attribution source. Because the delta report's `new_in_16_4` list is
empty in the live data and service strings are channel_kind identifiers
(not proto message names), the matcher uses a loose substring comparison
so version attributions can fire when Phase 8 starts populating the list.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .divergence import Divergence

Attribution = Literal["version", "oem", "ambiguous"]


@dataclass(frozen=True)
class AttributedDivergence:
    divergence: Divergence
    attribution: Attribution
    attribution_reason: str
    phase_8_delta_report_lookup: dict[str, Any]


def _service_matches_any(service: str, delta_entries: list[dict[str, Any]]) -> bool:
    """Check if any delta entry's proto_message contains the service string.

    Uses case-insensitive substring match because delta entries carry proto
    message names while divergences carry channel_kind strings — they do not
    line up 1:1, so substring is the realistic matcher. The service string
    has `_channel` and underscores stripped before comparison, which lets
    "bluetooth_channel" match a proto named "BluetoothPairingResponse".
    """
    service_lower = service.lower()
    needle = service_lower.replace("_channel", "").replace("_", "")
    if not needle:
        return False
    for entry in delta_entries:
        proto = str(entry.get("proto_message", "")).lower().replace("_", "")
        if needle in proto:
            return True
    return False


def classify_divergence(
    divergence: Divergence,
    delta_report: dict[str, Any],
) -> AttributedDivergence:
    """Classify a single divergence as version | oem | ambiguous.

    Logic (locked from 09-RESEARCH.md § Attribution algorithm):
      - service_only_in_vw + service listed in delta_report.new_in_16_4 → version
      - service_only_in_vw + not in new_in_16_4 → oem (default)
      - service_only_in_dhu + service listed in delta_report.removed_in_16_4 → version
      - service_only_in_dhu + not in removed_in_16_4 → ambiguous (default)
      - config_mismatch → ambiguous
    """
    new_in_16_4 = delta_report.get("new_in_16_4", [])
    removed_in_16_4 = delta_report.get("removed_in_16_4", [])

    lookup: dict[str, Any] = {
        "new_in_16_4": None,
        "removed_in_16_4": None,
        "schema_changes": None,
    }

    if divergence.kind == "service_only_in_vw":
        if _service_matches_any(divergence.service, new_in_16_4):
            lookup["new_in_16_4"] = divergence.service
            return AttributedDivergence(
                divergence=divergence,
                attribution="version",
                attribution_reason=(
                    f"Service {divergence.service!r} matched a proto listed in "
                    f"Phase 8 16-4-delta-report.new_in_16_4."
                ),
                phase_8_delta_report_lookup=lookup,
            )
        return AttributedDivergence(
            divergence=divergence,
            attribution="oem",
            attribution_reason=(
                f"Not listed in Phase 8 16-4-delta-report.new_in_16_4. Present in VW SDP "
                f"but absent from all DHU baselines — attributed to OEM divergence."
            ),
            phase_8_delta_report_lookup=lookup,
        )

    if divergence.kind == "service_only_in_dhu":
        if _service_matches_any(divergence.service, removed_in_16_4):
            lookup["removed_in_16_4"] = divergence.service
            return AttributedDivergence(
                divergence=divergence,
                attribution="version",
                attribution_reason=(
                    f"Service {divergence.service!r} matched a proto listed in "
                    f"Phase 8 16-4-delta-report.removed_in_16_4 — removed before 16.4."
                ),
                phase_8_delta_report_lookup=lookup,
            )
        return AttributedDivergence(
            divergence=divergence,
            attribution="ambiguous",
            attribution_reason=(
                f"Present in DHU but not VW; not listed in Phase 8 removed_in_16_4. "
                f"Could be DHU test harness infrastructure or a version change not "
                f"captured in the delta report."
            ),
            phase_8_delta_report_lookup=lookup,
        )

    return AttributedDivergence(
        divergence=divergence,
        attribution="ambiguous",
        attribution_reason="Config mismatch — requires human review.",
        phase_8_delta_report_lookup=lookup,
    )
