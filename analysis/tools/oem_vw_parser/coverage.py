from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Literal

from .models import (
    AttributedRecord,
    ClassifiedRecord,
    CoverageManifest,
    MsgTypeCoverageEntry,
    SdpSnapshot,
    UnifiedRecord,
)


# Locked override rationale vocabulary per 07-CONTEXT.md § "Override mechanism".
# Tight enum, no free text. Adding a new rationale requires a deliberate
# code change AND review.
VALID_OVERRIDE_RATIONALES = frozenset(
    {
        "structural_equivalence",
        "transitive_evidence",
        "external_spec",
        "cross_capture_convergence",
    }
)

_REQUIRED_OVERRIDE_TOP_FIELDS = (
    "service",
    "msg_type",
    "observed_in_current_capture",
    "override",
)
_REQUIRED_OVERRIDE_INNER_FIELDS = (
    "rationale",
    "evidence",
    "approver",
    "approved_at",
)


# Burstiness coefficient-of-variation threshold (07-CONTEXT.md § "Per-msg_type
# entry schema": "Coefficient of variation of inter-arrival times, thresholded.
# Tight vocabulary, purely mechanical."). 0.5 was picked from real DHU
# baselines: sensor streams come in at CoV ~0.05–0.15 (steady), notification
# bursts at 1.5+ (bursty). 0.5 is well outside both clusters.
_BURSTINESS_COV_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Override schema enforcement
# ---------------------------------------------------------------------------


def validate_override(override: dict) -> None:
    """Raise ValueError if the override entry is malformed.

    Required top-level fields: service, msg_type, observed_in_current_capture,
    override (with sub-fields rationale, evidence, approver, approved_at).
    Rationale MUST be in VALID_OVERRIDE_RATIONALES. Evidence list must be
    non-empty.
    """
    for field in _REQUIRED_OVERRIDE_TOP_FIELDS:
        if field not in override:
            raise ValueError(f"override missing required field: {field}")

    inner = override.get("override")
    if not isinstance(inner, dict):
        raise ValueError("override missing required field: override (must be dict)")
    for field in _REQUIRED_OVERRIDE_INNER_FIELDS:
        if field not in inner:
            raise ValueError(f"override missing required field: override.{field}")

    rationale = inner["rationale"]
    if rationale not in VALID_OVERRIDE_RATIONALES:
        raise ValueError(
            f"override rationale must be one of {sorted(VALID_OVERRIDE_RATIONALES)}, "
            f"got {rationale!r}"
        )

    evidence = inner["evidence"]
    if not isinstance(evidence, list) or len(evidence) == 0:
        raise ValueError("override evidence list must not be empty")


# ---------------------------------------------------------------------------
# Baseline snapshot hash (reproducible)
# ---------------------------------------------------------------------------


def compute_baseline_snapshot_hash(paths: Iterable[Path]) -> str:
    """Reproducible sha256 over the file set across baseline directories.

    Hash inputs are sorted (rel_path, size, mtime_ns) triples — running this
    twice over an unchanged file set produces an identical hash. Used by the
    coverage manifest to make the comparative gap analysis reproducible from
    the manifest alone.
    """
    triples: list[list] = []
    for p in sorted(Path(x) for x in paths):
        if not p.exists():
            continue
        for f in sorted(p.rglob("*")):
            if f.is_file():
                st = f.stat()
                # rel_path is rooted at the parent of the baseline dir so the
                # baseline name is part of the path.
                rel = f.relative_to(p.parent)
                triples.append([str(rel), st.st_size, st.st_mtime_ns])
    data = json.dumps(triples, sort_keys=True).encode()
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Temporal profile (mechanical, no interpretation)
# ---------------------------------------------------------------------------


def _classify_burstiness(
    ts_ms_list: list[int],
) -> Literal["steady", "bursty", "singleton", "unknown"]:
    """Burstiness classification per 07-CONTEXT.md § Per-msg_type entry schema.

    Rules:
        count == 1 → singleton
        count == 2 → unknown (only 1 inter-arrival, can't characterize)
        CoV < 0.5 → steady
        CoV >= 0.5 → bursty
    """
    n = len(ts_ms_list)
    if n == 1:
        return "singleton"
    if n == 2:
        return "unknown"
    intervals = [ts_ms_list[i + 1] - ts_ms_list[i] for i in range(n - 1)]
    if not intervals:
        return "unknown"
    mean = statistics.mean(intervals)
    if mean == 0:
        return "unknown"
    try:
        stdev = statistics.stdev(intervals)
    except statistics.StatisticsError:
        return "unknown"
    cov = stdev / mean
    return "steady" if cov < _BURSTINESS_COV_THRESHOLD else "bursty"


def temporal_profile(
    ts_ms_list: list[int],
    capture_duration_s: float,
) -> dict:
    """Compute the per-(msg_type, direction) temporal profile fields.

    Returns a dict with count, first/last_seen_ts_ms, observation_span_s,
    mean_rate_per_sec, duty_cycle, burstiness. Used both by the manifest
    builder and directly by the test_burstiness_* unit tests.
    """
    count = len(ts_ms_list)
    if count == 0:
        return {
            "count": 0,
            "first_seen_ts_ms": 0,
            "last_seen_ts_ms": 0,
            "observation_span_s": 0.0,
            "mean_rate_per_sec": 0.0,
            "duty_cycle": 0.0,
            "burstiness": "unknown",
        }
    sorted_ts = sorted(ts_ms_list)
    first = sorted_ts[0]
    last = sorted_ts[-1]
    span_s = (last - first) / 1000.0
    rate = count / span_s if span_s > 0 else 0.0
    duty = (span_s / capture_duration_s) if capture_duration_s > 0 else 0.0
    return {
        "count": count,
        "first_seen_ts_ms": first,
        "last_seen_ts_ms": last,
        "observation_span_s": span_s,
        "mean_rate_per_sec": rate,
        "duty_cycle": duty,
        "burstiness": _classify_burstiness(sorted_ts),
    }


# ---------------------------------------------------------------------------
# Manifest builder
# ---------------------------------------------------------------------------


def _per_msg_type_entries(
    classified: list[ClassifiedRecord],
    attributed: list[AttributedRecord],
    capture_duration_s: float,
) -> tuple[MsgTypeCoverageEntry, ...]:
    """Aggregate classified+attributed records into per-(service, msg_type, direction) entries."""
    grouped: dict[tuple[str | None, int, str], dict] = defaultdict(
        lambda: {
            "ts_ms_list": [],
            "bytes_total": 0,
            "confidence": Counter(),
        }
    )
    by_id: dict[int, AttributedRecord] = {id(ar.classified): ar for ar in attributed}
    for cr in classified:
        ar = by_id.get(id(cr))
        # Use the attributed service when available; otherwise None.
        service = ar.service if ar else None
        key = (service, cr.record.msg_type, cr.record.direction)
        bucket = grouped[key]
        bucket["ts_ms_list"].append(cr.record.ts_ms)
        bucket["bytes_total"] += cr.record.payload_len
        if ar is not None:
            bucket["confidence"][ar.confidence] += 1

    entries: list[MsgTypeCoverageEntry] = []
    for (service, msg_type, direction), bucket in sorted(
        grouped.items(), key=lambda kv: (-len(kv[1]["ts_ms_list"]), kv[0][1])
    ):
        prof = temporal_profile(bucket["ts_ms_list"], capture_duration_s)
        entries.append(
            MsgTypeCoverageEntry(
                service=service,
                msg_type=msg_type,
                direction=direction,
                count=prof["count"],
                bytes=bucket["bytes_total"],
                first_seen_ts_ms=prof["first_seen_ts_ms"],
                last_seen_ts_ms=prof["last_seen_ts_ms"],
                mean_rate_per_sec=prof["mean_rate_per_sec"],
                observation_span_s=prof["observation_span_s"],
                duty_cycle=prof["duty_cycle"],
                burstiness=prof["burstiness"],
                confidence_distribution=dict(bucket["confidence"]),
                fields_observed=None,
            )
        )
    return tuple(entries)


def _build_observed(
    sdp: SdpSnapshot,
    attributed: list[AttributedRecord],
) -> tuple[list[dict], dict[tuple[int, str], int]]:
    """Build the observed[] entries (one per declared channel that received traffic).

    Returns (observed_entries, per_channel_counts) — the latter is a
    dict[(channel_id, channel_kind), count] used to compute the gaps.intrinsic
    list.
    """
    # For each declared channel, count records attributed to that channel_kind.
    # The on-phone capture has no channel_id so attribution is at channel_kind
    # granularity. We count per (channel_id, channel_kind) by ALSO counting
    # any record attributed to channel_kind, distributed across all channels
    # of that kind. For VW, the av_channel kind has 5 channel_ids (1, 3, 4,
    # 5, 6), and there's no way to know which one a given record is on
    # without channel_id, so we count "any kind matched" → all matching
    # channel_ids get the same observed_count.
    counts_by_kind: Counter[str] = Counter()
    msg_types_by_kind: dict[str, set[int]] = defaultdict(set)
    for ar in attributed:
        if ar.service is None:
            # Could still be inferred_by_schema with multiple candidates;
            # those don't pin a channel_kind so they don't contribute to
            # observed[] (they're attribution-ambiguous, not channel-ambiguous).
            continue
        # The "control" service is not a declared channel — handled separately.
        if ar.service == "control":
            continue
        counts_by_kind[ar.service] += 1
        msg_types_by_kind[ar.service].add(ar.classified.record.msg_type)

    observed: list[dict] = []
    per_channel_counts: dict[tuple[int, str], int] = {}
    for svc in sorted(sdp.services, key=lambda s: s.channel_id):
        kind = svc.channel_kind
        # Per-channel count: same kind-level count attributed to every
        # channel_id of that kind. The on-phone capture lacks channel_id so
        # that's the most precise we can be. The kind-level summary handles
        # the rollup.
        c = counts_by_kind.get(kind, 0)
        per_channel_counts[(svc.channel_id, kind)] = c
        if c > 0:
            observed.append(
                {
                    "channel_id": svc.channel_id,
                    "channel_kind": kind,
                    "service": kind,
                    "msg_types": sorted(msg_types_by_kind.get(kind, set())),
                    "observed_count": c,
                }
            )
    return observed, per_channel_counts


def _build_intrinsic_gaps(
    sdp: SdpSnapshot,
    per_channel_counts: dict[tuple[int, str], int],
) -> list[dict]:
    """Every (channel_id, channel_kind) declared in SDP with no observed traffic.

    Zero-observation entries are MANDATORY per CONTEXT.md — no silent omission.
    """
    gaps: list[dict] = []
    for svc in sorted(sdp.services, key=lambda s: s.channel_id):
        key = (svc.channel_id, svc.channel_kind)
        if per_channel_counts.get(key, 0) == 0:
            gaps.append(
                {
                    "channel_id": svc.channel_id,
                    "channel_kind": svc.channel_kind,
                    "service": svc.channel_kind,
                    "declared_in_sdp": True,
                    "observed_count": 0,
                    "reason": "declared by HU but no records observed during capture window",
                    "remediation": "re-capture with scenario exercising this service",
                }
            )
    return gaps


def _build_comparative_gaps(
    sdp: SdpSnapshot,
    dhu_records: list[UnifiedRecord],
    dhu_baseline_paths: list[Path],
) -> list[dict]:
    """Services seen in DHU baselines but NOT declared by VW SDP."""
    declared_kinds = {s.channel_kind for s in sdp.services}
    # Map service_type values from DHU records to channel_kind names. The
    # validator's service_type strings include "radio_source", "car_control",
    # "media_sink", etc. — translate the obvious ones, leave the rest as-is.
    _service_type_to_kind = {
        "sensor_source": "sensor_channel",
        "radio_source": "radio_channel",
        "car_control": "car_control_channel",
        "media_sink": "av_channel",
        "input_source": "input_channel",
        "navigation": "navigation_channel",
        "nav_status": "navigation_channel",
        "phone_status": "phone_status_channel",
        "media_info": "media_info_channel",
        "sensor": "wifi_channel",
    }
    seen_kinds_in_dhu: dict[str, set[str]] = defaultdict(set)
    for r in dhu_records:
        if r.service_type:
            kind = _service_type_to_kind.get(r.service_type, r.service_type)
            seen_kinds_in_dhu[kind].add(r.capture_id)

    gaps: list[dict] = []
    for kind in sorted(seen_kinds_in_dhu.keys()):
        if kind not in declared_kinds:
            gaps.append(
                {
                    "channel_kind": kind,
                    "service": kind,
                    "declared_in_sdp": False,
                    "seen_in_baselines": sorted(seen_kinds_in_dhu[kind]),
                    "reason": "service not declared by this HU's SDP at all",
                    "remediation": "not promotable from this capture; use cross-capture data",
                }
            )
    return gaps


def _build_anomalies(
    classified: list[ClassifiedRecord],
    attributed: list[AttributedRecord],
    sdp: SdpSnapshot,
) -> tuple[list[dict], list[dict]]:
    """Records attributed but to non-declared services / records unattributed."""
    declared_kinds = {s.channel_kind for s in sdp.services}
    not_declared_counts: Counter[tuple[int, str]] = Counter()
    unattributed_counts: Counter[tuple[int, str]] = Counter()
    for ar in attributed:
        rec = ar.classified.record
        if ar.attribution_method == "unattributed" and ar.classified.label != "continuation_or_garbage":
            unattributed_counts[(rec.msg_type, rec.direction)] += 1
            continue
        if ar.service and ar.service != "control" and ar.service not in declared_kinds:
            not_declared_counts[(rec.msg_type, rec.direction)] += 1

    not_declared = [
        {"msg_type": mt, "direction": d, "count": c}
        for (mt, d), c in sorted(not_declared_counts.items())
    ]
    unattributed = [
        {"msg_type": mt, "direction": d, "count": c}
        for (mt, d), c in sorted(unattributed_counts.items())
    ]
    return not_declared, unattributed


def _build_channel_kind_summary(
    sdp: SdpSnapshot,
    per_channel_counts: dict[tuple[int, str], int],
) -> dict:
    """Per-channel-kind aggregate: declared vs observed vs silent."""
    by_kind: dict[str, dict[str, int]] = defaultdict(
        lambda: {"declared": 0, "observed": 0, "silent": 0}
    )
    for svc in sdp.services:
        kind = svc.channel_kind
        by_kind[kind]["declared"] += 1
        if per_channel_counts.get((svc.channel_id, kind), 0) > 0:
            by_kind[kind]["observed"] += 1
        else:
            by_kind[kind]["silent"] += 1
    # Plain dict so JSON serialization is stable.
    return {k: dict(v) for k, v in by_kind.items()}


def build_coverage_manifest(
    classified: list[ClassifiedRecord],
    attributed: list[AttributedRecord],
    sdp: SdpSnapshot,
    capture_duration_s: float,
    dhu_baseline_paths: list[Path],
    dhu_records: list[UnifiedRecord],
    capture_id: str = "oem-vw-mib3oi-2026-04-06",
) -> CoverageManifest:
    """End-to-end coverage manifest builder.

    Builds the per-msg_type entries, observed[], gaps.intrinsic[],
    gaps.comparative[], anomalies, channel_kind_summary, and gap_analysis
    (with reproducible baseline_snapshot_hash). Zero-observation entries
    are emitted unconditionally per CONTEXT.md.
    """
    per_msg_type = _per_msg_type_entries(classified, attributed, capture_duration_s)
    observed, per_channel_counts = _build_observed(sdp, attributed)
    gaps_intrinsic = _build_intrinsic_gaps(sdp, per_channel_counts)
    gaps_comparative = _build_comparative_gaps(sdp, dhu_records, dhu_baseline_paths)
    not_declared, unattributed = _build_anomalies(classified, attributed, sdp)
    channel_kind_summary = _build_channel_kind_summary(sdp, per_channel_counts)

    gap_analysis = {
        "compared_against_baselines": [str(p) for p in dhu_baseline_paths],
        "baseline_snapshot_hash": compute_baseline_snapshot_hash(dhu_baseline_paths),
    }

    return CoverageManifest(
        capture_id=capture_id,
        capture_duration_s=capture_duration_s,
        observed=tuple(observed),
        gaps_intrinsic=tuple(gaps_intrinsic),
        gaps_comparative=tuple(gaps_comparative),
        anomalies_service_not_declared=tuple(not_declared),
        anomalies_unattributed=tuple(unattributed),
        gap_analysis=gap_analysis,
        per_msg_type=per_msg_type,
        channel_kind_summary=channel_kind_summary,
    )
