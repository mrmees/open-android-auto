from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ChannelCounts:
    bronze: int = 0
    silver: int = 0
    gold: int = 0
    platinum: int = 0
    retracted: int = 0
    superseded: int = 0


@dataclass(frozen=True)
class ScanResult:
    per_channel: dict[str, ChannelCounts] = field(default_factory=dict)
    evidence_by_tier: dict[str, dict[str, int]] = field(default_factory=dict)
    missing_sidecars: dict[str, list[str]] = field(default_factory=dict)
    orphan_sidecars: dict[str, list[str]] = field(default_factory=dict)
    total_sidecars: int = 0
    total_protos: int = 0
    pending_gold_count: int = 0
    directories_scanned: int = 0


_TIER_FIELDS = ("bronze", "silver", "gold", "platinum", "retracted", "superseded")


def scan_audit_tree(repo_root: Path) -> ScanResult:
    """Walk oaa/ tree, collect tier counts, evidence types, missing/orphan lists."""
    oaa_root = repo_root / "oaa"
    if not oaa_root.is_dir():
        return ScanResult()

    per_channel: dict[str, ChannelCounts] = {}
    evidence_by_tier: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    missing_sidecars: dict[str, list[str]] = {}
    orphan_sidecars: dict[str, list[str]] = {}
    total_sidecars = 0
    total_protos = 0
    pending_gold_count = 0
    directories_scanned = 0

    for subdir in sorted(oaa_root.iterdir()):
        if not subdir.is_dir():
            continue

        dir_name = subdir.name

        # Collect proto and sidecar stems
        proto_stems = {f.stem for f in subdir.glob("*.proto")}
        sidecar_files = list(subdir.glob("*.audit.yaml"))
        sidecar_stems = set()
        for sf in sidecar_files:
            # Strip .audit.yaml to get the base name
            base = sf.name
            if base.endswith(".audit.yaml"):
                stem = base[: -len(".audit.yaml")]
                sidecar_stems.add(stem)

        # Only count this directory if it has protos OR sidecars
        if not proto_stems and not sidecar_stems:
            continue

        directories_scanned += 1
        total_protos += len(proto_stems)
        total_sidecars += len(sidecar_stems)

        # Missing = protos without matching sidecar
        missing = sorted(proto_stems - sidecar_stems)
        if missing:
            missing_sidecars[dir_name] = [f"{s}.proto" for s in missing]

        # Orphan = sidecars without matching proto
        orphan = sorted(sidecar_stems - proto_stems)
        if orphan:
            orphan_sidecars[dir_name] = [f"{s}.audit.yaml" for s in orphan]

        # Count tiers and evidence for this directory
        tier_counts: dict[str, int] = defaultdict(int)

        for sf in sidecar_files:
            base = sf.name
            if not base.endswith(".audit.yaml"):
                continue

            try:
                data = yaml.safe_load(sf.read_text())
            except Exception:
                continue

            if not isinstance(data, dict):
                continue

            confidence = data.get("confidence", "unverified")
            if confidence in _TIER_FIELDS:
                tier_counts[confidence] += 1

            # Count evidence types (dynamically discovered)
            for ev in data.get("evidence", []):
                if isinstance(ev, dict):
                    ev_type = ev.get("type")
                    if ev_type:
                        evidence_by_tier[confidence][ev_type] += 1

            # CRITICAL: Do NOT count pending_platinum_evidence entries

            # Check oem_match_pending_gold flag
            if data.get("oem_match_pending_gold") is True:
                pending_gold_count += 1

        per_channel[dir_name] = ChannelCounts(
            bronze=tier_counts.get("bronze", 0),
            silver=tier_counts.get("silver", 0),
            gold=tier_counts.get("gold", 0),
            platinum=tier_counts.get("platinum", 0),
            retracted=tier_counts.get("retracted", 0),
            superseded=tier_counts.get("superseded", 0),
        )

    # Convert nested defaultdicts to regular dicts for frozen dataclass
    evidence_dict = {k: dict(v) for k, v in evidence_by_tier.items()}

    return ScanResult(
        per_channel=per_channel,
        evidence_by_tier=evidence_dict,
        missing_sidecars=missing_sidecars,
        orphan_sidecars=orphan_sidecars,
        total_sidecars=total_sidecars,
        total_protos=total_protos,
        pending_gold_count=pending_gold_count,
        directories_scanned=directories_scanned,
    )
