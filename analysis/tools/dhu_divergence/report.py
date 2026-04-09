"""Emit the VW-vs-DHU divergence report as markdown + JSON sidecar.

The 8 markdown section headers are LOCKED (see SECTION_HEADERS). The JSON
sidecar's top-level keys mirror the markdown sections (snake_case). Both
formats are deterministic: markdown uses a fixed layout, JSON uses
`sort_keys=True, indent=2` with a trailing newline.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

from .attribution import AttributedDivergence
from .baseline_merge import MergedDhu

# LOCKED — these exact 8 section headers, in this order. Any change here is
# a locked-contract change and must be reflected in CONTEXT.md and 09-RESEARCH.md.
SECTION_HEADERS = [
    "## 1. Summary",
    "## 2. Version-attributed divergences",
    "## 3. OEM-attributed divergences",
    "## 4. Ambiguous divergences",
    "## 5. Services in VW but not DHU",
    "## 6. Services in DHU but not VW",
    "## 7. Per-baseline observation summary",
    "## 8. Baseline reproduction",
]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _safe_rel(path: Path) -> str:
    """Render a path relative to cwd when possible; fall back to str()."""
    try:
        if path.is_absolute():
            return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)
    return str(path)


def _attr_to_json(a: AttributedDivergence) -> dict[str, Any]:
    d = a.divergence
    return {
        "kind": d.kind,
        "service": d.service,
        "vw_config": d.vw_config,
        "dhu_configs": d.dhu_configs,
        "baselines_matched": d.baselines_matched,
        "attribution": a.attribution,
        "attribution_reason": a.attribution_reason,
        "phase_8_delta_report_lookup": a.phase_8_delta_report_lookup,
    }


def build_json(
    attributed: list[AttributedDivergence],
    merged_dhu: MergedDhu,
    vw_sdp_values: dict[str, Any],
    vw_capture_path: str,
    delta_report_path: Path,
    run_date: str | None = None,
) -> dict[str, Any]:
    """Build the JSON sidecar dict. All top-level keys match the markdown sections."""
    run_date = run_date or date.today().isoformat()
    hu_info = vw_sdp_values.get("response", {}).get("head_unit_info", {})
    vw_aa_version = (
        hu_info.get("head_unit_software_version")
        or hu_info.get("aa_version")
        or "unknown"
    )

    dhu_baselines_meta = [
        {
            "name": b.name,
            "path": _safe_rel(b.path),
            "sha256": _sha256_file(b.path),
        }
        for b in merged_dhu.baselines
    ]

    version_list = [_attr_to_json(a) for a in attributed if a.attribution == "version"]
    oem_list = [_attr_to_json(a) for a in attributed if a.attribution == "oem"]
    ambig_list = [_attr_to_json(a) for a in attributed if a.attribution == "ambiguous"]

    services_in_vw_only = sorted(
        a.divergence.service
        for a in attributed
        if a.divergence.kind == "service_only_in_vw"
    )
    services_in_dhu_only = sorted(
        a.divergence.service
        for a in attributed
        if a.divergence.kind == "service_only_in_dhu"
    )

    by_attribution = {
        "version": len(version_list),
        "oem": len(oem_list),
        "ambiguous": len(ambig_list),
    }
    by_service: dict[str, int] = {}
    for a in attributed:
        by_service[a.divergence.service] = by_service.get(a.divergence.service, 0) + 1

    per_baseline_summary: dict[str, dict[str, int]] = {}
    for b in merged_dhu.baselines:
        distinct_kinds = {c["channel_kind"] for c in b.channels if c.get("channel_kind")}
        per_baseline_summary[b.name] = {
            "channels": len(b.channels),
            "kinds": len(distinct_kinds),
        }

    return {
        "metadata": {
            "generated_date": run_date,
            "vw_capture_path": vw_capture_path,
            "vw_aa_version": vw_aa_version,
            "dhu_baselines": dhu_baselines_meta,
            "phase_8_delta_report_sha256": _sha256_file(delta_report_path),
        },
        "summary": {
            "total_divergences": len(attributed),
            "by_attribution": by_attribution,
            "by_service": by_service,
        },
        "version_attributed_divergences": version_list,
        "oem_attributed_divergences": oem_list,
        "ambiguous_divergences": ambig_list,
        "services_in_vw_but_not_dhu": services_in_vw_only,
        "services_in_dhu_but_not_vw": services_in_dhu_only,
        "per_baseline_observation_summary": per_baseline_summary,
        "baseline_reproduction": {
            "command": (
                "PYTHONPATH=. python3 -m analysis.tools.dhu_divergence.run "
                "--vw-sdp-json analysis/reports/oem-vw/sdp-values.json "
                "--dhu captures/general --dhu captures/idle-baseline "
                "--dhu captures/music-playback --dhu captures/active-navigation "
                "--delta-report analysis/reports/cross-version/16-4-delta-report.json "
                "--out analysis/reports/oem-vw/"
            ),
            "run_date": run_date,
        },
    }


def emit_json(data: dict[str, Any], out_path: Path) -> None:
    """Deterministic JSON dump: `sort_keys=True, indent=2`, trailing newline."""
    out_path.write_text(
        json.dumps(data, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _emit_divergence_list(lines: list[str], entries: list[dict[str, Any]]) -> None:
    if not entries:
        lines.append("_(none)_")
        return
    for e in entries:
        lines.append(f"### {e['service']} ({e['kind']})")
        lines.append("")
        lines.append(f"- Attribution: **{e['attribution']}**")
        lines.append(f"- Reason: {e['attribution_reason']}")
        if e.get("baselines_matched"):
            lines.append(f"- Baselines matched: {e['baselines_matched']}")
        lines.append("")


def emit_markdown(data: dict[str, Any], out_path: Path) -> None:
    """Emit the 8-section markdown report. All 8 locked headers MUST appear in order."""
    lines: list[str] = []
    lines.append("# VW vs DHU SDP Divergence Report")
    lines.append("")
    lines.append(f"Generated: {data['metadata']['generated_date']}")
    lines.append(f"VW capture: `{data['metadata']['vw_capture_path']}`")
    lines.append(f"VW AA version: `{data['metadata']['vw_aa_version']}`")
    lines.append("")

    # ## 1. Summary
    lines.append(SECTION_HEADERS[0])
    lines.append("")
    lines.append(f"- Total divergences: **{data['summary']['total_divergences']}**")
    lines.append(
        f"- By attribution: {json.dumps(data['summary']['by_attribution'], sort_keys=True)}"
    )
    lines.append(
        f"- By service: {json.dumps(data['summary']['by_service'], sort_keys=True)}"
    )
    lines.append("")

    # ## 2. Version-attributed divergences
    lines.append(SECTION_HEADERS[1])
    lines.append("")
    _emit_divergence_list(lines, data["version_attributed_divergences"])
    lines.append("")

    # ## 3. OEM-attributed divergences
    lines.append(SECTION_HEADERS[2])
    lines.append("")
    _emit_divergence_list(lines, data["oem_attributed_divergences"])
    lines.append("")

    # ## 4. Ambiguous divergences
    lines.append(SECTION_HEADERS[3])
    lines.append("")
    _emit_divergence_list(lines, data["ambiguous_divergences"])
    lines.append("")

    # ## 5. Services in VW but not DHU
    lines.append(SECTION_HEADERS[4])
    lines.append("")
    if data["services_in_vw_but_not_dhu"]:
        for s in data["services_in_vw_but_not_dhu"]:
            lines.append(f"- `{s}`")
    else:
        lines.append("- _(none)_")
    lines.append("")

    # ## 6. Services in DHU but not VW
    lines.append(SECTION_HEADERS[5])
    lines.append("")
    if data["services_in_dhu_but_not_vw"]:
        for s in data["services_in_dhu_but_not_vw"]:
            lines.append(f"- `{s}`")
    else:
        lines.append("- _(none)_")
    lines.append("")

    # ## 7. Per-baseline observation summary
    lines.append(SECTION_HEADERS[6])
    lines.append("")
    for name, info in sorted(data["per_baseline_observation_summary"].items()):
        lines.append(
            f"- **{name}**: {info['channels']} channels, {info['kinds']} distinct kinds"
        )
    lines.append("")

    # ## 8. Baseline reproduction
    lines.append(SECTION_HEADERS[7])
    lines.append("")
    lines.append("```bash")
    lines.append(data["baseline_reproduction"]["command"])
    lines.append("```")
    lines.append("")
    lines.append(f"**Run date:** {data['baseline_reproduction']['run_date']}")
    lines.append("")
    lines.append("### DHU baselines")
    lines.append("")
    for b in data["metadata"]["dhu_baselines"]:
        lines.append(
            f"- `{b['name']}`: `{b['path']}` — sha256 `{b['sha256']}`"
        )
    lines.append("")
    lines.append(
        f"**Phase 8 delta report sha256:** `{data['metadata']['phase_8_delta_report_sha256']}`"
    )
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
