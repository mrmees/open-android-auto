from __future__ import annotations

from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path

from .models import (
    ClassifiedRecord,
    CoverageManifest,
    FrequencyProfile,
    SdpRequestInfo,
    SdpSnapshot,
)


HEURISTIC_CAVEAT = (
    "> **Loud caveat:** This is a heuristic stack over a lossy capture format. The on-phone\n"
    "> hook lives inside the AA framing layer — `channel_id`, `flags`, and frame boundaries are\n"
    "> not visible. Continuation fragments inside multi-frame messages are interpreted as\n"
    "> standalone records by the wire format and must be filtered by the three-tier\n"
    "> plausibility gate. Real ground truth requires the framing-hook capture work tracked as\n"
    "> v2 CAP-01. Residual misclassifications will be visible in aggregate stats.\n"
)


def emit_classification_report(
    classified: list[ClassifiedRecord],
    profile: FrequencyProfile,
    out_path: Path,
    capture_id: str,
    capture_window_s: float,
    total_records: int,
) -> None:
    """Write the per-msg_type classification markdown report.

    Three sections: Tier Distribution, Label Distribution (5 atomic buckets),
    and Per-msg_type Classification table sorted by count desc. The
    HEURISTIC_CAVEAT block is rendered prominently near the top so naïve
    readers cannot mistake fragment classification rows for verified protocol
    messages.
    """
    buf = StringIO()
    buf.write("# VW Capture: Per-msg_type Classification\n\n")
    buf.write(f"**Capture:** `captures/{capture_id}/`\n")
    buf.write("**Capture version:** 5 (`native_interceptor_regnatives`)\n")
    buf.write(f"**Records:** {total_records:,} ({capture_window_s:.1f}s window)\n")
    buf.write(f"**Frequency threshold (empirical):** {profile.threshold}\n\n")
    buf.write(HEURISTIC_CAVEAT + "\n")

    # Tier distribution
    by_tier: Counter[str] = Counter(cr.tier for cr in classified)
    buf.write("## Tier Distribution\n\n")
    buf.write("| Tier | Records | % |\n|------|--------:|--:|\n")
    for tier in ("A", "B", "C"):
        count = by_tier.get(tier, 0)
        pct = (count / total_records * 100) if total_records else 0
        buf.write(f"| {tier} | {count:,} | {pct:.1f}% |\n")
    buf.write("\n")

    # Label distribution
    by_label: Counter[str] = Counter(cr.label for cr in classified)
    buf.write("## Label Distribution (5 buckets — atomic)\n\n")
    buf.write("| Label | Records |\n|-------|--------:|\n")
    for label in (
        "standalone",
        "probable_first",
        "continuation_or_garbage",
        "reassembled",
        "unattributed",
    ):
        buf.write(f"| {label} | {by_label.get(label, 0):,} |\n")
    buf.write("\n")
    buf.write("_`reassembled` is intentionally empty in Phase 7 — see 07-CONTEXT.md decisions._\n\n")
    buf.write("_`unattributed` is reserved for the attribution pipeline in plan 07-02._\n\n")

    # Per-msg_type table
    buf.write("## Per-msg_type Classification\n\n")
    buf.write("| msg_type | hex | tier | direction | count | label | notes |\n")
    buf.write("|---------:|-----|-----|-----------|------:|-------|-------|\n")
    grouped: dict[tuple[int, str, str, str], list[ClassifiedRecord]] = defaultdict(list)
    for cr in classified:
        key = (cr.record.msg_type, cr.record.direction, cr.tier, cr.label)
        grouped[key].append(cr)
    for (mt, direction, tier, label), records in sorted(
        grouped.items(), key=lambda k: -len(k[1])
    ):
        notes_sample = ",".join(records[0].notes) if records[0].notes else "—"
        buf.write(
            f"| {mt} | 0x{mt:04X} | {tier} | {direction} | "
            f"{len(records):,} | {label} | {notes_sample} |\n"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(buf.getvalue(), encoding="utf-8")


# ---------------------------------------------------------------------------
# 07-02 reports: SDP values, coverage manifest, candidate OEM-only msg_types
# ---------------------------------------------------------------------------


_ALL_CHANNEL_KINDS = (
    "sensor_channel",
    "av_channel",
    "input_channel",
    "av_input_channel",
    "bluetooth_channel",
    "radio_channel",
    "navigation_channel",
    "media_info_channel",
    "phone_status_channel",
    "media_browser_channel",
    "vendor_extension_channel",
    "notification_channel",
    "wifi_channel",
    "car_control_channel",
    "generic_notification_channel",
    "voice_channel",
)


def emit_sdp_values_report(
    sdp: SdpSnapshot,
    req: SdpRequestInfo,
    out_path: Path,
) -> None:
    """OEM-02 production SDP values markdown report.

    Documents both directions, the HeadUnitInfo sub-message, every declared
    channel descriptor, and the explicit list of services VW does NOT declare
    (the negative space matters as much as the positive list — Phase 10 needs
    to know what comparative gaps exist).
    """
    buf = StringIO()
    buf.write("# VW Capture: Service Discovery Values\n\n")
    buf.write("**Capture:** `captures/oem-vw-mib3oi-2026-04-06/`\n")
    buf.write("**Source bins:** `sdp_request.bin`, `sdp_response.bin`\n")
    buf.write("**Verified directions** (determined by decode, NOT the README):\n\n")
    buf.write("- `sdp_request.bin` → phone → HU (decodes as ServiceDiscoveryRequest)\n")
    buf.write("- `sdp_response.bin` → HU → phone (decodes as ServiceDiscoveryResponse)\n\n")

    buf.write("## SDP Request (phone → HU)\n\n")
    buf.write(f"- device_name: `{req.device_name}`\n")
    buf.write(f"- device_brand: `{req.device_brand}`\n")
    buf.write(f"- session_uuid: `{req.session_uuid}`\n")
    buf.write(
        f"- phone_icon_small: present={req.icon_small.present}, "
        f"size_bytes={req.icon_small.size_bytes}\n"
    )
    buf.write(
        f"- phone_icon_medium: present={req.icon_medium.present}, "
        f"size_bytes={req.icon_medium.size_bytes}\n"
    )
    buf.write(
        f"- phone_icon_large: present={req.icon_large.present}, "
        f"size_bytes={req.icon_large.size_bytes}\n\n"
    )

    buf.write("## SDP Response (HU → phone)\n\n")
    buf.write(f"- head_unit_name: `{sdp.head_unit_name}`\n")
    buf.write(f"- car_model: `{sdp.car_model}`\n")
    buf.write(f"- car_year: `{sdp.car_year}`\n")
    buf.write(f"- car_serial: `{sdp.car_serial}`\n")
    buf.write(f"- headunit_manufacturer: `{sdp.headunit_manufacturer}`\n")
    buf.write(f"- headunit_model: `{sdp.headunit_model}`\n")
    buf.write(f"- sw_build: `{sdp.sw_build}`\n")
    buf.write(f"- sw_version: `{sdp.sw_version}`\n")
    buf.write(f"- session_configuration: `{sdp.session_configuration}`\n")
    buf.write(f"- display_name: `{sdp.display_name}`\n")
    buf.write(f"- probe_for_support: `{sdp.probe_for_support}`\n")
    if sdp.driver_position is not None:
        buf.write(f"- driver_position: `{sdp.driver_position}`\n")
    if sdp.can_play_native_media_during_vr is not None:
        buf.write(
            f"- can_play_native_media_during_vr: `{sdp.can_play_native_media_during_vr}`\n"
        )
    buf.write("\n")

    buf.write("### HeadUnitInfo (sub-message)\n\n")
    if sdp.head_unit_info:
        for k, v in sorted(sdp.head_unit_info.items()):
            buf.write(f"- {k}: `{v}`\n")
    else:
        buf.write("_(not present in this SDP response)_\n")
    buf.write("\n")

    buf.write(f"### Channel Descriptors ({len(sdp.services)} channels declared)\n\n")
    buf.write("| channel_id | channel_kind | config summary |\n")
    buf.write("|---:|---|---|\n")
    for svc in sorted(sdp.services, key=lambda s: s.channel_id):
        if svc.config:
            cfg_keys = ", ".join(sorted(svc.config.keys())[:6])
        else:
            cfg_keys = "(empty marker)"
        buf.write(f"| {svc.channel_id} | `{svc.channel_kind}` | {cfg_keys} |\n")
    buf.write("\n")

    buf.write("## Services NOT declared by VW\n\n")
    declared = {s.channel_kind for s in sdp.services}
    missing = sorted(set(_ALL_CHANNEL_KINDS) - declared)
    for kind in missing:
        buf.write(f"- `{kind}`\n")
    buf.write("\n")
    buf.write(
        "_These services are part of the full ChannelDescriptor schema but are "
        "absent from VW's SDP advertisement. They are comparative gaps — "
        "potentially observable on other OEMs but not on this VW MIB3 OI._\n"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(buf.getvalue(), encoding="utf-8")


def emit_coverage_report(manifest: CoverageManifest, out_path: Path) -> None:
    """OEM-03 coverage manifest markdown report — three loud sections."""
    buf = StringIO()
    buf.write("# VW Capture: Coverage Manifest\n\n")
    buf.write(f"**Capture:** `captures/{manifest.capture_id}/`\n")
    buf.write(f"**Capture duration:** {manifest.capture_duration_s:.1f}s\n\n")
    buf.write(HEURISTIC_CAVEAT + "\n")

    # Channel kind summary
    buf.write("## Channel Kind Summary\n\n")
    buf.write("| channel_kind | declared | observed | silent |\n")
    buf.write("|--------------|---------:|---------:|-------:|\n")
    for kind in sorted(manifest.channel_kind_summary.keys()):
        s = manifest.channel_kind_summary[kind]
        buf.write(
            f"| `{kind}` | {s['declared']} | {s['observed']} | {s['silent']} |\n"
        )
    total_declared = sum(
        s["declared"] for s in manifest.channel_kind_summary.values()
    )
    buf.write(f"\n_Total declared channels: {total_declared}_\n\n")

    # Section 1: Observed services
    buf.write("## Observed services\n\n")
    buf.write(
        f"VW declared {total_declared} channels; "
        f"traffic seen on {len(manifest.observed)}, "
        f"silent on {len(manifest.gaps_intrinsic)}.\n\n"
    )
    if manifest.observed:
        buf.write("| channel_id | service | msg_types observed (first 10) |\n")
        buf.write("|---:|---------|--------------------|\n")
        for entry in sorted(manifest.observed, key=lambda e: e.get("channel_id", 0)):
            mt_list = ", ".join(f"0x{mt:04X}" for mt in entry["msg_types"][:10])
            buf.write(
                f"| {entry['channel_id']} | `{entry['service']}` | {mt_list} |\n"
            )
    else:
        buf.write("_(no observed services)_\n")
    buf.write("\n")

    # Section 2: Intrinsic gaps
    buf.write("## Gaps — intrinsic (VW declared, no traffic — re-capturable)\n\n")
    if manifest.gaps_intrinsic:
        buf.write("| channel_id | service | observed_count | remediation |\n")
        buf.write("|---:|---------|---------------:|-------------|\n")
        for gap in sorted(manifest.gaps_intrinsic, key=lambda g: g["channel_id"]):
            buf.write(
                f"| {gap['channel_id']} | `{gap['service']}` | "
                f"{gap['observed_count']} | {gap['remediation']} |\n"
            )
    else:
        buf.write("_(no intrinsic gaps — every declared service had traffic)_\n")
    buf.write("\n")

    # Section 3: Comparative gaps
    buf.write(
        "## Gaps — comparative (seen in baselines, NOT declared by VW — capability gap)\n\n"
    )
    if manifest.gaps_comparative:
        buf.write("| service | seen in baselines | remediation |\n")
        buf.write("|---------|-------------------|-------------|\n")
        for gap in manifest.gaps_comparative:
            baselines = ", ".join(gap.get("seen_in_baselines", []))
            buf.write(
                f"| `{gap['service']}` | {baselines} | {gap['remediation']} |\n"
            )
    else:
        buf.write(
            "_(no comparative gaps — every service seen in DHU baselines is also declared by VW)_\n"
        )
    buf.write("\n")

    # Anomalies
    buf.write("## Anomalies (observed but unattributed — investigate)\n\n")
    buf.write(
        f"- `service_not_declared` records: "
        f"{len(manifest.anomalies_service_not_declared)}\n"
    )
    buf.write(
        f"- `unattributed` records: {len(manifest.anomalies_unattributed)}\n\n"
    )
    if manifest.anomalies_unattributed:
        buf.write("### Unattributed (top 20)\n\n")
        buf.write("| msg_type | hex | direction | count |\n")
        buf.write("|---------:|-----|-----------|------:|\n")
        sorted_unattr = sorted(
            manifest.anomalies_unattributed,
            key=lambda e: -e.get("count", 0),
        )
        for entry in sorted_unattr[:20]:
            mt = entry["msg_type"]
            buf.write(
                f"| {mt} | 0x{mt:04X} | {entry['direction']} | {entry['count']} |\n"
            )
        buf.write("\n")

    # Reproducibility
    buf.write("## Gap analysis reproducibility\n\n")
    baselines = ", ".join(
        manifest.gap_analysis.get("compared_against_baselines", [])
    )
    buf.write(f"- baselines: {baselines or '(none)'}\n")
    buf.write(
        f"- baseline_snapshot_hash: `{manifest.gap_analysis.get('baseline_snapshot_hash', '')}`\n"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(buf.getvalue(), encoding="utf-8")


def emit_candidate_report(
    candidates_by_mt: dict[int, dict],
    candidates_by_mt_dir: dict[tuple[int, str], dict],
    out_path: Path,
) -> None:
    """OEM-05 candidate OEM-only msg_types markdown report.

    Every entry is labeled `candidate` (NEVER `confirmed`). Continuation
    fragments are filtered out upstream by the OEM-01 fragment classifier.
    """
    buf = StringIO()
    buf.write("# VW Capture: Candidate OEM-only msg_types\n\n")
    buf.write(
        "**Set difference**: `{(msg_type, direction) in VW} - "
        "`{(msg_type, direction) in any DHU baseline}`\n\n"
    )
    buf.write(
        "**Filter**: every candidate was first filtered through the OEM-01 "
        "fragment classification pipeline — `continuation_or_garbage` records "
        "are NEVER listed here.\n\n"
    )
    buf.write(
        "**Label**: every surviving entry is labeled `candidate` (NEVER "
        "`confirmed`) until repeat observation in a future capture, "
        "successful schema parse, or APK cross-reference.\n\n"
    )

    buf.write("## By (msg_type, direction)\n\n")
    if candidates_by_mt_dir:
        buf.write("| msg_type | hex | direction | count | tier | attribution | label |\n")
        buf.write("|---------:|-----|-----------|------:|------|-------------|-------|\n")
        for (mt, direction), e in sorted(candidates_by_mt_dir.items()):
            buf.write(
                f"| {mt} | 0x{mt:04X} | {direction} | {e['count']} | "
                f"{e.get('tier', '?')} | {e.get('attribution_method', '?')} | candidate |\n"
            )
    else:
        buf.write("_(no candidates — VW capture had no msg_types absent from DHU baselines)_\n")
    buf.write("\n")

    buf.write("## By msg_type only\n\n")
    if candidates_by_mt:
        buf.write("| msg_type | hex | count | label |\n")
        buf.write("|---------:|-----|------:|-------|\n")
        for mt, e in sorted(candidates_by_mt.items()):
            buf.write(f"| {mt} | 0x{mt:04X} | {e['count']} | candidate |\n")
    else:
        buf.write("_(no candidates)_\n")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(buf.getvalue(), encoding="utf-8")
