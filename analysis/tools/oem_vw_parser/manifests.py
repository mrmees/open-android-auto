from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from .models import (
    ClassifiedRecord,
    CoverageManifest,
    FrequencyProfile,
    SdpRequestInfo,
    SdpSnapshot,
)


def emit_classification_json(
    classified: list[ClassifiedRecord],
    profile: FrequencyProfile,
    out_path: Path,
    capture_id: str,
    total_records: int,
) -> None:
    """Write the per-msg_type classification machine-readable manifest.

    Sorted entries by descending count then ascending msg_type. Stable JSON
    output (sort_keys=True, indent=2, trailing newline) so re-runs produce
    byte-identical files when the input hasn't changed.
    """
    by_tier: Counter[str] = Counter(cr.tier for cr in classified)
    by_label: Counter[str] = Counter(cr.label for cr in classified)
    grouped: dict[tuple[int, str, str, str], int] = defaultdict(int)
    for cr in classified:
        grouped[(cr.record.msg_type, cr.record.direction, cr.tier, cr.label)] += 1

    entries = []
    for (mt, direction, tier, label), count in sorted(
        grouped.items(), key=lambda k: (-k[1], k[0][0])
    ):
        entries.append(
            {
                "msg_type": mt,
                "msg_type_hex": f"0x{mt:04X}",
                "direction": direction,
                "tier": tier,
                "label": label,
                "count": count,
            }
        )

    payload = {
        "capture_id": capture_id,
        "total_records": total_records,
        "tier_counts": {k: by_tier.get(k, 0) for k in ("A", "B", "C")},
        "label_counts": {
            k: by_label.get(k, 0)
            for k in (
                "standalone",
                "probable_first",
                "continuation_or_garbage",
                "reassembled",
                "unattributed",
            )
        },
        "freq_threshold": profile.threshold,
        "freq_threshold_source": profile.source,
        "entries": entries,
        "notes": {
            "reassembled": "intentionally empty per Phase 7 CONTEXT.md",
            "unattributed": "reserved for plan 07-02 attribution pipeline",
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# 07-02 JSON sidecars: SDP values, coverage manifest, candidate OEM-only
# ---------------------------------------------------------------------------


def emit_sdp_values_json(
    sdp: SdpSnapshot,
    req: SdpRequestInfo,
    out_path: Path,
) -> None:
    """OEM-02 SDP values machine-readable JSON sidecar."""
    payload = {
        "directions": {
            "sdp_request.bin": "phone -> HU",
            "sdp_response.bin": "HU -> phone",
        },
        "request": {
            "device_name": req.device_name,
            "device_brand": req.device_brand,
            "session_uuid": req.session_uuid,
            "icons": {
                "small": {
                    "present": req.icon_small.present,
                    "size_bytes": req.icon_small.size_bytes,
                },
                "medium": {
                    "present": req.icon_medium.present,
                    "size_bytes": req.icon_medium.size_bytes,
                },
                "large": {
                    "present": req.icon_large.present,
                    "size_bytes": req.icon_large.size_bytes,
                },
            },
        },
        "response": {
            "head_unit_name": sdp.head_unit_name,
            "car_model": sdp.car_model,
            "car_year": sdp.car_year,
            "car_serial": sdp.car_serial,
            "headunit_manufacturer": sdp.headunit_manufacturer,
            "headunit_model": sdp.headunit_model,
            "sw_build": sdp.sw_build,
            "sw_version": sdp.sw_version,
            "session_configuration": sdp.session_configuration,
            "display_name": sdp.display_name,
            "probe_for_support": sdp.probe_for_support,
            "can_play_native_media_during_vr": sdp.can_play_native_media_during_vr,
            "driver_position": sdp.driver_position,
            "head_unit_info": sdp.head_unit_info,
            "channels": [
                {
                    "channel_id": s.channel_id,
                    "channel_kind": s.channel_kind,
                    "config": s.config,
                }
                for s in sdp.services
            ],
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def emit_coverage_json(manifest: CoverageManifest, out_path: Path) -> None:
    """OEM-03 coverage manifest machine-readable JSON sidecar."""
    payload = {
        "capture_id": manifest.capture_id,
        "capture_duration_s": manifest.capture_duration_s,
        "channel_kind_summary": manifest.channel_kind_summary,
        "observed": list(manifest.observed),
        "gaps": {
            "intrinsic": list(manifest.gaps_intrinsic),
            "comparative": list(manifest.gaps_comparative),
        },
        "anomalies": {
            "service_not_declared": list(manifest.anomalies_service_not_declared),
            "unattributed": list(manifest.anomalies_unattributed),
        },
        "gap_analysis": manifest.gap_analysis,
        "per_msg_type": [
            {
                "service": e.service,
                "msg_type": e.msg_type,
                "direction": e.direction,
                "count": e.count,
                "bytes": e.bytes,
                "first_seen_ts_ms": e.first_seen_ts_ms,
                "last_seen_ts_ms": e.last_seen_ts_ms,
                "mean_rate_per_sec": e.mean_rate_per_sec,
                "observation_span_s": e.observation_span_s,
                "duty_cycle": e.duty_cycle,
                "burstiness": e.burstiness,
                "confidence_distribution": e.confidence_distribution,
                "fields_observed": e.fields_observed,
            }
            for e in manifest.per_msg_type
        ],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def emit_candidate_json(
    candidates_by_mt: dict,
    candidates_by_mt_dir: dict,
    out_path: Path,
) -> None:
    """OEM-05 candidate OEM-only msg_types JSON sidecar.

    Both views (by_msg_type and by_msg_type_direction) emit. Every entry is
    labeled `candidate`, never `confirmed`.
    """
    payload = {
        "label": "candidate",
        "note": (
            "Every entry is a CANDIDATE, not a CONFIRMED OEM-only msg_type. "
            "Filtered through OEM-01 fragment classification. Continuation "
            "fragments NEVER appear in this list."
        ),
        "candidates_by_msg_type": {str(k): v for k, v in candidates_by_mt.items()},
        "candidates_by_msg_type_direction": [
            {"msg_type": k[0], "direction": k[1], **v}
            for k, v in sorted(candidates_by_mt_dir.items())
        ],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
