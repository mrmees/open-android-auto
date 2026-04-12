from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


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


def scan_audit_tree(repo_root: Path) -> ScanResult:
    """Walk oaa/ tree, collect tier counts, evidence types, missing/orphan lists."""
    raise NotImplementedError("scan_audit_tree not yet implemented")
