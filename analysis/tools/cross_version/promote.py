"""Audit sidecar promotion logic.

Adds cross_version evidence to eligible sidecars and promotes bronze to silver.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from analysis.tools.cross_version.compare import ComparisonResult
from analysis.tools.seed_import.generate import (
    compute_tier,
    sidecar_path,
    validate_audit,
    write_audit_yaml,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]


def promote_sidecars(
    results: list[ComparisonResult],
    repo_root: Path | None = None,
) -> int:
    """Promote eligible audit sidecars from bronze to silver.

    For each consistent ComparisonResult, add cross_version evidence
    to the audit sidecar and recompute the confidence tier.

    Args:
        results: Comparison results from run_comparison.
        repo_root: Repository root path (default: auto-detected).

    Returns:
        Number of sidecars promoted.
    """
    root = repo_root or _REPO_ROOT
    promoted = 0

    for r in results:
        if not r.is_consistent:
            continue
        if not r.pairs_compared:
            continue

        sp = root / sidecar_path(r.mapping.proto_file)
        if not sp.exists():
            continue

        with open(sp) as f:
            audit = yaml.safe_load(f)

        if audit is None:
            continue

        # Skip if already has cross_version evidence
        evidence = audit.get("evidence", [])
        if any(e.get("type") == "cross_version" for e in evidence):
            continue

        # Add cross_version evidence
        versions = r.versions_matched
        evidence.append({
            "type": "cross_version",
            "method": "structural_comparison",
            "source": f"cross-version checker ({', '.join(versions)})",
            "date": date.today().isoformat(),
            "description": (
                f"Structural match confirmed across versions "
                f"{', '.join(versions)}. Field numbers, types, "
                f"and modifiers are consistent."
            ),
        })
        audit["evidence"] = evidence

        # Recompute tier
        audit["confidence"] = compute_tier(evidence)
        audit["last_updated"] = date.today().isoformat()

        # Validate and write
        validate_audit(audit)
        write_audit_yaml(audit, sp)
        promoted += 1

    return promoted
