from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from analysis.tools.promotion_walker.index import (
    build_index, build_sdp_kinds, build_classification,
)
from analysis.tools.promotion_walker.verdict import (
    Verdict, VerdictKind, walker_decide, content_hash,
)
from analysis.tools.promotion_walker.report import (
    build_walk_report, emit_md, emit_json,
    build_worklist, emit_worklist_md, emit_worklist_json,
)
from analysis.tools.seed_import.generate import validate_audit, write_audit_yaml

DEFAULT_SCOPE_DIRS = ("oaa/av", "oaa/media", "oaa/video", "oaa/audio")


def _build_platinum_evidence_entry(verdict: Verdict, capture_path: str, run_date: str) -> dict[str, Any]:
    return {
        "type": "platinum_evidence",
        "source": f"{capture_path}/messages.jsonl",
        "date": run_date,
        "description": (
            f"VW MIB3 OI capture: {', '.join(verdict.matched_rules)} citation for "
            f"{verdict.channel_kind}. Phase 10 walker verdict. See analysis/reports/oem-vw/promotion-walk.md."
        ),
        "capture_path": f"{capture_path}/",
        "vehicle_metadata": {
            "make": "Volkswagen",
            "model": "MIB3 OI",
            "year": "2024",
            "aa_version": "16.4.661034",
        },
        "msg_seq": list(verdict.msg_seq) or [0],
        "ts_ms": list(verdict.ts_ms) or [0],
        "message_completeness": verdict.message_completeness or "full",
        "attribution_method": "sdp_service_id",
        "oem_scope": "single",
        "applicability": "message",
        "match_rules": list(verdict.matched_rules),
    }


def _apply_verdict(
    verdict: Verdict,
    sidecar_path: Path,
    capture_path: str,
    run_date: str,
    dry_run: bool,
) -> bool:
    """Apply a verdict to a sidecar file. Returns True if the file was (would be) modified."""
    if verdict.kind not in (
        VerdictKind.PROMOTE_TO_PLATINUM,
        VerdictKind.FLAG_PENDING_GOLD,
        VerdictKind.NOMATCH_OBSERVATION,
        VerdictKind.CONTRADICTION_REVIEW,
    ):
        return False

    sidecar = yaml.safe_load(sidecar_path.read_text())

    entry = _build_platinum_evidence_entry(verdict, capture_path, run_date)
    new_hash = content_hash(entry)

    if verdict.kind == VerdictKind.PROMOTE_TO_PLATINUM:
        # Idempotency: check if an entry with this hash already exists in evidence
        existing = sidecar.get("evidence", [])
        if any(content_hash(e) == new_hash for e in existing):
            return False
        sidecar["confidence"] = "platinum"
        sidecar["platinum_scope"] = "single_oem"
        sidecar["last_updated"] = run_date
        sidecar.setdefault("evidence", []).append(entry)
    elif verdict.kind == VerdictKind.FLAG_PENDING_GOLD:
        existing = sidecar.get("pending_platinum_evidence", [])
        if any(content_hash(e) == new_hash for e in existing):
            # Still ensure the flag is set (might be missing even if hash present)
            if sidecar.get("oem_match_pending_gold") is True:
                return False
        sidecar["oem_match_pending_gold"] = True
        sidecar["last_updated"] = run_date
        sidecar.setdefault("pending_platinum_evidence", []).append(entry)
    else:
        # NOMATCH / CONTRADICTION: not expected to fire on Phase 10 real data
        return False

    # Validate BEFORE writing -- raise if walker produced an invalid sidecar
    try:
        validate_audit(sidecar)
    except Exception as e:
        raise RuntimeError(
            f"walker produced invalid sidecar at {sidecar_path}: {str(e)[:200]}"
        )

    if dry_run:
        return True

    write_audit_yaml(sidecar, sidecar_path)
    return True


def _commit_one(verdict: Verdict, sidecar_path: Path, repo_root: Path, phase_plan: str = "10-02") -> None:
    """Atomic git commit for one sidecar change."""
    rules = ", ".join(verdict.matched_rules) or "no rules"

    if verdict.kind == VerdictKind.PROMOTE_TO_PLATINUM:
        subject = f"feat({phase_plan}): promote {verdict.proto_message} to Platinum ({rules})"
    elif verdict.kind == VerdictKind.FLAG_PENDING_GOLD:
        subject = f"chore({phase_plan}): flag {verdict.proto_message} for oem_match_pending_gold ({rules})"
    elif verdict.kind == VerdictKind.NOMATCH_OBSERVATION:
        nomatch = ", ".join(verdict.nomatch_rules) or "NOMATCH-02"
        subject = f"docs({phase_plan}): record nomatch_observation for {verdict.proto_message} ({nomatch})"
    elif verdict.kind == VerdictKind.CONTRADICTION_REVIEW:
        subject = f"docs({phase_plan}): flag {verdict.proto_message} for retraction review"
    else:
        return  # no commit for SKIP_* verdicts

    rel_path = str(sidecar_path.relative_to(repo_root))
    subprocess.run(
        ["git", "add", rel_path],
        check=True,
        cwd=str(repo_root),
    )
    subprocess.run(
        ["git", "commit", "-m", subject],
        check=True,
        cwd=str(repo_root),
    )


def _compute_capture_sha256(messages_jsonl: Path) -> str:
    return hashlib.sha256(messages_jsonl.read_bytes()).hexdigest()


def _count_unobserved(repo_root: Path, in_scope_dirs: tuple[str, ...]) -> dict[str, dict[str, int]]:
    """Walk oaa/ and count sidecars by directory for dirs NOT in scope."""
    oaa = repo_root / "oaa"
    out: dict[str, dict[str, int]] = {}
    for sub in sorted(oaa.iterdir()):
        if not sub.is_dir():
            continue
        rel = f"oaa/{sub.name}"
        if rel in in_scope_dirs:
            continue
        counts: dict[str, int] = defaultdict(int)
        for fx in sub.rglob("*.audit.yaml"):
            try:
                sc = yaml.safe_load(fx.read_text())
                tier = sc.get("confidence", "unverified")
                counts[tier] += 1
                counts["total"] += 1
            except Exception:
                counts["parse_error"] += 1
                counts["total"] += 1
        if counts:
            out[rel] = dict(counts)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="promotion_walker")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scope-dir", action="append", default=None)
    parser.add_argument("--capture", default="captures/oem-vw-mib3oi-2026-04-06/")
    parser.add_argument("--coverage", default="analysis/reports/oem-vw/coverage.json")
    parser.add_argument("--sdp", default="analysis/reports/oem-vw/sdp-values.json")
    parser.add_argument("--classification", default="analysis/reports/oem-vw/msg-type-classification.json")
    parser.add_argument("--out", default="analysis/reports/oem-vw/")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    scope_dirs = tuple(args.scope_dir) if args.scope_dir else DEFAULT_SCOPE_DIRS
    capture_path_str = args.capture.rstrip("/")
    messages_jsonl = repo_root / capture_path_str / "messages.jsonl"
    capture_sha = _compute_capture_sha256(messages_jsonl)

    # Load schema for pre-validation
    schema = json.loads((repo_root / "docs/verification/audit-schema.json").read_text())

    # Build inputs
    index = build_index(repo_root / args.coverage, messages_jsonl)
    sdp_kinds = build_sdp_kinds(repo_root / args.sdp)
    classification = build_classification(repo_root / args.classification)

    # Count pre-walk Gold / Platinum in scope
    gold_before = 0
    platinum_before = 0
    all_sidecar_paths: list[Path] = []
    for sdir in scope_dirs:
        for p in sorted((repo_root / sdir).rglob("*.audit.yaml")):
            all_sidecar_paths.append(p)
            try:
                sc = yaml.safe_load(p.read_text())
                if sc.get("confidence") == "gold":
                    gold_before += 1
                elif sc.get("confidence") == "platinum":
                    platinum_before += 1
            except Exception:
                pass

    run_date = date.today().isoformat()
    verdicts: list[Verdict] = []

    for path in all_sidecar_paths:
        try:
            sidecar = yaml.safe_load(path.read_text())
        except Exception as e:
            verdicts.append(Verdict(
                sidecar_path=str(path.relative_to(repo_root)),
                proto_message="?", current_tier="unverified",
                kind=VerdictKind.SKIP_SCHEMA_INVALID,
                skip_reason=f"yaml_parse_error: {str(e)[:80]}",
            ))
            continue

        verdict = walker_decide(sidecar, path, index, sdp_kinds, classification, schema)
        # Normalize sidecar_path to a repo-relative string for reporting
        rel_path = str(path.relative_to(repo_root)).replace("\\", "/")
        verdict = Verdict(
            sidecar_path=rel_path,
            proto_message=verdict.proto_message,
            current_tier=verdict.current_tier,
            kind=verdict.kind,
            matched_rules=verdict.matched_rules,
            nomatch_rules=verdict.nomatch_rules,
            msg_seq=verdict.msg_seq,
            ts_ms=verdict.ts_ms,
            message_completeness=verdict.message_completeness,
            channel_kind=verdict.channel_kind,
            skip_reason=verdict.skip_reason,
            contradiction_summary=verdict.contradiction_summary,
        )
        verdicts.append(verdict)

        # Apply + commit (unless dry-run)
        modified = _apply_verdict(verdict, path, capture_path_str, run_date, args.dry_run)
        if modified and not args.dry_run:
            _commit_one(verdict, path, repo_root)
        if args.dry_run:
            print(f"[{verdict.kind.value}] {rel_path} -- {', '.join(verdict.matched_rules) or verdict.skip_reason or ''}")

    # Build + emit reports
    metadata = {
        "walker_run_date": run_date,
        "capture_path": capture_path_str,
        "capture_sha256": capture_sha,
        "messages_jsonl_line_count": sum(1 for _ in messages_jsonl.open()),
        "walker_version": "10.02",
        "scope_dirs": list(scope_dirs),
    }
    unobserved_counts = _count_unobserved(repo_root, scope_dirs)
    report = build_walk_report(
        verdicts, run_date, metadata, unobserved_counts,
        gold_before=gold_before, platinum_before=platinum_before,
    )

    out_dir = Path(args.out) if not args.dry_run else Path("/tmp") / f"walker-dry-run-{run_date}"
    out_dir = (repo_root / out_dir) if not out_dir.is_absolute() else out_dir
    emit_md(report, out_dir / "promotion-walk.md")
    emit_json(report, out_dir / "promotion-walk.json")

    pending_verdicts = [v for v in verdicts if v.kind == VerdictKind.FLAG_PENDING_GOLD]
    worklist = build_worklist(pending_verdicts, metadata)
    emit_worklist_md(worklist, out_dir / "oem-match-pending-gold-worklist.md")
    emit_worklist_json(worklist, out_dir / "oem-match-pending-gold-worklist.json")

    if not args.dry_run:
        # Final reports commit
        report_files = [
            str((out_dir / "promotion-walk.md").relative_to(repo_root)),
            str((out_dir / "promotion-walk.json").relative_to(repo_root)),
            str((out_dir / "oem-match-pending-gold-worklist.md").relative_to(repo_root)),
            str((out_dir / "oem-match-pending-gold-worklist.json").relative_to(repo_root)),
        ]
        subprocess.run(
            ["git", "add", *report_files],
            check=True,
            cwd=str(repo_root),
        )
        subprocess.run(
            ["git", "commit", "-m",
             "docs(10-02): write promotion walk report + worklist + Gold-counts delta"],
            check=True,
            cwd=str(repo_root),
        )

    # Summary to stdout
    by_kind: dict[str, int] = defaultdict(int)
    for v in verdicts:
        by_kind[v.kind.value] += 1
    print(f"\n=== Phase 10 Promotion Walker Summary ===")
    for k, n in sorted(by_kind.items()):
        print(f"  {k}: {n}")
    print(f"  TOTAL: {len(verdicts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
