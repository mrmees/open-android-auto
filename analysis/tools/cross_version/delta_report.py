"""16.4 delta report generator.

Phase 8 XVER-02. Produces:
- analysis/reports/cross-version/16-4-delta-report.md (human-readable, 8 locked sections)
- analysis/reports/cross-version/16-4-delta-report.json (machine-readable, Phase 9 sidecar)

The 4 known spurious enum drifts (DriverPosition, HapticFeedbackType,
SensorErrorStatus, CarLocalMediaPlayback) are SUPPRESSED from the
Schema Changes section and moved to a Known Indexer Artifacts section.
They fire because `proto_enum_classes` is present in 15.9 and 16.4 DBs
but ABSENT in 16.1 and 16.2 DBs — the comparator sees the 15.9 fallback
return enum values while 16.1/16.2 return nothing, and interprets that
as "all fields removed". This is a data-layer artifact, not a real
16.4 delta.

The Markdown report opens with a build-number note that explicitly states
the canonical 16.4 build for Phase 8 is 661014; 661034 is referenced
only for the XVER-05 reproducibility-gap doc.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

from analysis.tools.cross_version.compare import ComparisonResult
from analysis.tools.proto_schema_validator.models import IssueKind, Severity

_REPO_ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = _REPO_ROOT / "analysis" / "reports" / "cross-version"

SPURIOUS_ENUM_NAMES = frozenset(
    {
        "DriverPosition",
        "HapticFeedbackType",
        "SensorErrorStatus",
        "CarLocalMediaPlayback",
    }
)

# Locked section headers (verbatim, enforced by test_section_structure).
SECTION_HEADERS: tuple[str, ...] = (
    "## 1. Summary",
    "## 2. New in 16.4",
    "## 3. Removed in 16.4",
    "## 4. Schema Changes",
    "## 5. Promoted Bronze → Silver",
    "## 6. Drifted Silver/Gold",
    "## 7. Unmappable Protos",
    "## 8. Baseline Reproduction",
)

INTRO_BUILD_NOTE = (
    "> **Canonical 16.4 build for Phase 8 is 661014** (the indexed build). "
    "16.4.661034 is referenced ONLY for the manual-JADX reproducibility-gap doc — "
    "all structural analysis runs exclusively against 661014."
)


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_spurious(result: ComparisonResult) -> bool:
    """Return True if this ComparisonResult matches the known spurious enum drift pattern.

    A result is spurious if its proto_message is in the locked suppression list
    AND its drift pairs involve 15.9 on one side with 16.1/16.2 on the other
    (the missing-table signature).
    """
    name = result.mapping.proto_message
    if name not in SPURIOUS_ENUM_NAMES:
        return False
    for p in result.pairs_compared:
        if "15.9" in p and ("16.1" in p or "16.2" in p):
            return True
    return False


def _serialize_issue(issue: Any) -> dict[str, Any]:
    """Serialize a DriftIssue dataclass to a JSON-friendly dict."""
    return {
        "kind": issue.kind.value if isinstance(issue.kind, IssueKind) else str(issue.kind),
        "severity": issue.severity.value if isinstance(issue.severity, Severity) else str(issue.severity),
        "field_number": issue.field_number,
        "detail": issue.detail,
    }


def _build_summary(
    total_mappings: int,
    real_results: list[ComparisonResult],
) -> dict[str, Any]:
    """Build the Summary section counts.

    total_mappings is the full class_mapping.yaml row count (240), independent
    of whether each row produced a comparable pair.
    """
    eligible = len([r for r in real_results if r.pairs_compared])
    consistent = sum(1 for r in real_results if r.is_consistent)
    with_drift = eligible - consistent
    all_six = sum(1 for r in real_results if len(r.pairs_compared) == 6)
    with_164_pair = sum(
        1 for r in real_results if any("16.4" in (p[0], p[1]) for p in r.pairs_compared)
    )
    return {
        "total": total_mappings,
        "eligible": eligible,
        "consistent": consistent,
        "with_drift": with_drift,
        "all_six_pairs_clean": all_six,
        "with_16_4_pair": with_164_pair,
    }


def _new_in_16_4(
    results: list[ComparisonResult],
    db_paths: dict[str, Path],
) -> list[dict[str, Any]]:
    """Protos 'new in 16.4' — placeholder: no source-of-truth signal today.

    A proto would be 'new in 16.4' if it exists in the 16.4 DB and has no
    matching entry in any prior version's class_mapping.yaml. Detecting this
    reliably requires scanning the 16.4 DB for classes whose field-tuples
    don't match any existing mapping, which is out of scope for Phase 8.

    For now, return an empty list with a note. Phase 9 / 10 can revisit.
    """
    return []


def _schema_changes(real_results: list[ComparisonResult]) -> list[dict[str, Any]]:
    """FIELD_ADDED / FIELD_REMOVED / FIELD_TYPE_CHANGED per mapping.

    Only emits entries where at least one pair involves 16.4 OR there are
    any real field-level drift issues. Spurious drifts are already excluded
    upstream in the caller.
    """
    out: list[dict[str, Any]] = []
    for r in real_results:
        if not r.issues:
            continue
        out.append(
            {
                "proto_message": r.mapping.proto_message,
                "proto_file": r.mapping.proto_file,
                "pairs_compared": [f"{a}_vs_{b}" for a, b in r.pairs_compared],
                "issues": [_serialize_issue(i) for i in r.issues],
            }
        )
    return out


def _drifted(real_results: list[ComparisonResult]) -> list[dict[str, Any]]:
    """Mappings with suspicious drift (FIELD_REMOVED / FIELD_TYPE_CHANGED).

    These are flagged for review but NOT auto-downgraded per the XVER-03
    walker semantics (see 08-CONTEXT.md "Drifted Silver/Gold").
    """
    out: list[dict[str, Any]] = []
    for r in real_results:
        if not r.has_suspicious:
            continue
        out.append(
            {
                "proto_message": r.mapping.proto_message,
                "confidence": r.mapping.confidence,
                "suspicious_issues": [
                    _serialize_issue(i)
                    for i in r.issues
                    if i.kind in (IssueKind.FIELD_REMOVED, IssueKind.FIELD_TYPE_CHANGED)
                ],
            }
        )
    return out


def generate_delta_report(
    results: list[ComparisonResult],
    db_paths: dict[str, Path],
    all_mappings_results: list[ComparisonResult] | None = None,
    mapping_candidates_md: Path | None = None,
    output_dir: Path = REPORT_DIR,
    total_mappings: int | None = None,
    promotion_outcomes: list[tuple[str, str]] | None = None,
) -> None:
    """Generate the markdown + JSON delta report.

    Args:
        results: ComparisonResult list from run_comparison(). Only entries with
            at least one pair_compared.
        db_paths: version → APK index DB path (all 4 versions required).
        all_mappings_results: optional full mapping list (for unmappable
            section — ones with no pair ran at all). If None, uses `results`.
        mapping_candidates_md: optional reference to the candidates report.
        output_dir: target directory for the two output files.
        promotion_outcomes: optional list of (proto_message, outcome) tuples
            from the Phase 8 Plan 02 walker. Populates section 5 and the
            ``promoted_bronze_to_silver`` JSON key.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / "16-4-delta-report.md"
    json_path = output_dir / "16-4-delta-report.json"

    if all_mappings_results is None:
        all_mappings_results = results

    # Partition: suppress the 4 known spurious enum drifts
    spurious_results = [r for r in results if _is_spurious(r)]
    real_results = [r for r in results if not _is_spurious(r)]

    if total_mappings is None:
        # Fall back to loading the mapping file count directly — the total
        # should reflect every ProtoMapping in class_mapping.yaml, not just
        # the ones that produced a ComparisonResult (run_comparison skips
        # 0-field pairs).
        from analysis.tools.proto_schema_validator.mapping import load_mapping

        total_mappings = len(load_mapping())

    summary = _build_summary(total_mappings, real_results)
    schema_changes = _schema_changes(real_results)
    drifted = _drifted(real_results)
    # For unmappable, use the full mapping list (some mappings never enter
    # run_comparison because their 16.2 source class is also null / empty).
    from analysis.tools.proto_schema_validator.mapping import load_mapping

    all_mappings = load_mapping()
    unmappable = [
        {"proto_message": m.proto_message, "proto_file": m.proto_file}
        for m in all_mappings
        if m.apk_classes.get("16.4") is None
    ]
    removed = [
        {
            "proto_message": m.proto_message,
            "last_present_in": (
                "16.2"
                if m.apk_classes.get("16.2")
                else "16.1"
                if m.apk_classes.get("16.1")
                else "15.9"
                if m.apk_classes.get("15.9")
                else "none"
            ),
            "note": "Either removed from 16.4 or unresolved by the auto-matcher — see 16-4-mapping-candidates.md",
        }
        for m in all_mappings
        if m.apk_classes.get("16.4") is None
        and (m.apk_classes.get("16.2") or m.apk_classes.get("16.1") or m.apk_classes.get("15.9"))
    ]

    known_artifacts = [
        {
            "proto_message": r.mapping.proto_message,
            "proto_file": r.mapping.proto_file,
            "reason": (
                "proto_enum_classes table absent in 16.1/16.2 but present in 15.9/16.4 — "
                "drift is a data-layer artifact, not a real 16.4 delta."
            ),
            "suppressed_issues": len(r.issues),
        }
        for r in spurious_results
    ]
    # Ensure all 4 locked names appear even if the comparison didn't surface them
    present = {a["proto_message"] for a in known_artifacts}
    for name in sorted(SPURIOUS_ENUM_NAMES - present):
        known_artifacts.append(
            {
                "proto_message": name,
                "proto_file": "",
                "reason": (
                    "Locked suppression: proto_enum_classes table artifact. "
                    "Not surfaced by this run but suppressed unconditionally."
                ),
                "suppressed_issues": 0,
            }
        )

    # 661034 reproducibility-gap reference goes into the intro / references
    # section of the markdown. The JSON sidecar records it explicitly.
    promoted_outcomes_json: list[dict[str, str]] = (
        [
            {"proto_message": p, "outcome": o}
            for p, o in (promotion_outcomes or [])
        ]
    )

    report: dict[str, Any] = {
        "generated_date": date.today().isoformat(),
        "canonical_build": "16.4.661014",
        "reproducibility_gap_build": "16.4.661034",
        "reproducibility_gap_doc": "analysis/reports/cross-version/manual-jadx-reproducibility-gap.md",
        "summary": summary,
        "new_in_16_4": _new_in_16_4(real_results, db_paths),
        "removed_in_16_4": removed,
        "schema_changes": schema_changes,
        "promoted_bronze_to_silver": promoted_outcomes_json,
        "drifted_silver_gold": drifted,
        "unmappable": unmappable,
        "baseline_reproduction": {
            "command": "PYTHONPATH=. python3 -m analysis.tools.cross_version.run",
            "run_date": date.today().isoformat(),
            "db_sha256": {v: _sha256_of_file(p) for v, p in sorted(db_paths.items())},
        },
        "known_indexer_artifacts": known_artifacts,
    }
    json_path.write_text(json.dumps(report, indent=2) + "\n")

    md = _build_markdown(report, mapping_candidates_md)
    md_path.write_text(md)


def _build_markdown(report: dict[str, Any], candidates_md: Path | None) -> str:
    lines: list[str] = [
        "# 16.4 Cross-Version Delta Report",
        "",
        f"**Generated:** {report['generated_date']}",
        f"**Canonical build:** `{report['canonical_build']}`",
        "",
        INTRO_BUILD_NOTE,
        "",
        f"For the 16.4.661034 build and the 5 salvaged manual-JADX classes, see "
        f"[manual-jadx-reproducibility-gap.md](./manual-jadx-reproducibility-gap.md).",
        "",
    ]

    # ---- Section 1: Summary ----
    lines.append(SECTION_HEADERS[0])
    lines.append("")
    s = report["summary"]
    lines.append(f"- **Total mappings analyzed:** {s['total']}")
    lines.append(f"- **Eligible (≥1 pair compared):** {s['eligible']}")
    lines.append(f"- **Consistent (no drift):** {s['consistent']}")
    lines.append(f"- **With drift (suspicious or additive):** {s['with_drift']}")
    lines.append(f"- **All 6 pairs compared cleanly:** {s['all_six_pairs_clean']}")
    lines.append(f"- **Mappings with 16.4 pair included:** {s['with_16_4_pair']}")
    lines.append(
        f"- **Known indexer artifacts suppressed:** {len(report['known_indexer_artifacts'])} "
        f"({', '.join(e['proto_message'] for e in report['known_indexer_artifacts'])})"
    )
    lines.append("")

    # ---- Section 2: New in 16.4 ----
    lines.append(SECTION_HEADERS[1])
    lines.append("")
    if report["new_in_16_4"]:
        for entry in report["new_in_16_4"]:
            lines.append(f"- `{entry['class_name']}`: {entry.get('note', '')}")
    else:
        lines.append(
            "_No protos classified as 'new in 16.4' by the auto-matcher. A proto would be "
            "new here if it appeared in the 16.4 DB with a field-tuple that has no counterpart "
            "in any prior version's class_mapping.yaml — detecting that is out of scope for "
            "Phase 8 (would require scanning every unmapped 16.4 class against every existing "
            "mapping). Phase 9 / 10 may revisit._"
        )
    lines.append("")

    # ---- Section 3: Removed in 16.4 ----
    lines.append(SECTION_HEADERS[2])
    lines.append("")
    if report["removed_in_16_4"]:
        lines.append(
            f"**{len(report['removed_in_16_4'])}** mappings have a null 16.4 class — "
            f"either truly removed from 16.4 or unresolved by the auto-matcher. See "
            f"[16-4-mapping-candidates.md](./16-4-mapping-candidates.md) for the distinction."
        )
        lines.append("")
        lines.append("| Proto | Last present in |")
        lines.append("|-------|-----------------|")
        for entry in report["removed_in_16_4"][:30]:
            lines.append(f"| `{entry['proto_message']}` | {entry['last_present_in']} |")
        if len(report["removed_in_16_4"]) > 30:
            lines.append(
                f"| … | _{len(report['removed_in_16_4']) - 30} more — see JSON sidecar_ |"
            )
    else:
        lines.append("_None._")
    lines.append("")

    # ---- Section 4: Schema Changes ----
    lines.append(SECTION_HEADERS[3])
    lines.append("")
    if report["schema_changes"]:
        lines.append(
            f"**{len(report['schema_changes'])}** mappings have at least one field-level "
            f"drift issue (FIELD_ADDED / FIELD_REMOVED / FIELD_TYPE_CHANGED). The 4 known "
            f"spurious enum drifts are excluded — see the Known Indexer Artifacts note below."
        )
        lines.append("")
        lines.append("| Proto | Pairs | Issues |")
        lines.append("|-------|-------|--------|")
        for entry in report["schema_changes"]:
            issue_summary = ", ".join(
                f"{i['kind']}(field={i['field_number']})" for i in entry["issues"][:3]
            )
            if len(entry["issues"]) > 3:
                issue_summary += f" (+{len(entry['issues']) - 3} more)"
            lines.append(
                f"| `{entry['proto_message']}` | "
                f"{', '.join(entry['pairs_compared'])} | {issue_summary} |"
            )
    else:
        lines.append(
            "_None._ After suppressing the 4 known spurious enum drifts "
            "(DriverPosition, HapticFeedbackType, SensorErrorStatus, CarLocalMediaPlayback), "
            "no mapping has any field-level drift issues across the 4 versions."
        )
    lines.append("")

    # ---- Known Indexer Artifacts (suppressed drifts) ----
    lines.append("### Known Indexer Artifacts (Suppressed from Schema Changes)")
    lines.append("")
    lines.append(
        "The following enum mappings appear to drift but are spurious — they are "
        "artifacts of `proto_enum_classes` being present in the 15.9 and 16.4 DBs but "
        "absent in the 16.1 and 16.2 DBs. Schema evolution at the indexer layer, not "
        "the proto layer. These are suppressed from Section 4 above and listed here "
        "for transparency."
    )
    lines.append("")
    for entry in report["known_indexer_artifacts"]:
        lines.append(
            f"- `{entry['proto_message']}` — {entry['reason']} "
            f"(suppressed {entry['suppressed_issues']} issue(s))"
        )
    lines.append("")

    # ---- Section 5: Promoted Bronze → Silver ----
    lines.append(SECTION_HEADERS[4])
    lines.append("")
    outcomes_list = report["promoted_bronze_to_silver"]
    if not outcomes_list:
        lines.append(
            "_No outcomes recorded (promotion walk did not run). Re-run with "
            "`--promote` to populate this section._"
        )
    else:
        promoted_entries = [o for o in outcomes_list if o["outcome"] == "promoted"]
        lines.append(f"**Promoted to Silver:** {len(promoted_entries)}")
        lines.append("")
        if promoted_entries:
            lines.append("| Proto Message |")
            lines.append("|---------------|")
            for entry in promoted_entries:
                lines.append(f"| `{entry['proto_message']}` |")
            lines.append("")
        else:
            lines.append(
                "_Zero Bronze sidecars met the strict 'all 6 pairs clean' rule. "
                "This is the expected headline per 08-RESEARCH.md 'Bronze Promotion "
                "Reality Check' — all Bronze sidecars map to 0-field marker classes._"
            )
            lines.append("")
        by_outcome: dict[str, int] = {}
        for o in outcomes_list:
            by_outcome[o["outcome"]] = by_outcome.get(o["outcome"], 0) + 1
        lines.append("**Outcome breakdown:**")
        lines.append("")
        for outcome, count in sorted(by_outcome.items()):
            lines.append(f"- `{outcome}`: {count}")
        lines.append("")

    # ---- Section 6: Drifted Silver/Gold ----
    lines.append(SECTION_HEADERS[5])
    lines.append("")
    if report["drifted_silver_gold"]:
        lines.append(
            f"**{len(report['drifted_silver_gold'])}** mappings with prior-version consensus "
            f"have suspicious drift in 16.4. Flagged for human review, NOT downgraded automatically."
        )
        lines.append("")
        lines.append("| Proto | Confidence | Drift |")
        lines.append("|-------|------------|-------|")
        for entry in report["drifted_silver_gold"]:
            drift = ", ".join(
                f"{i['kind']}(field={i['field_number']})"
                for i in entry["suspicious_issues"][:3]
            )
            lines.append(
                f"| `{entry['proto_message']}` | {entry['confidence']} | {drift} |"
            )
    else:
        lines.append(
            "_None._ No Silver or Gold mapping has suspicious drift (FIELD_REMOVED or "
            "FIELD_TYPE_CHANGED) in any pair involving 16.4."
        )
    lines.append("")

    # ---- Section 7: Unmappable Protos ----
    lines.append(SECTION_HEADERS[6])
    lines.append("")
    um = report["unmappable"]
    lines.append(
        f"**{len(um)}** mappings have `'16.4': null`. Detailed reasoning per mapping "
        f"is in [16-4-mapping-candidates.md](./16-4-mapping-candidates.md)."
    )
    lines.append("")
    if um:
        lines.append("| Proto | File |")
        lines.append("|-------|------|")
        for entry in um[:30]:
            lines.append(f"| `{entry['proto_message']}` | `{entry['proto_file']}` |")
        if len(um) > 30:
            lines.append(f"| … | _{len(um) - 30} more — see JSON sidecar_ |")
    lines.append("")

    # ---- Section 8: Baseline Reproduction ----
    lines.append(SECTION_HEADERS[7])
    lines.append("")
    br = report["baseline_reproduction"]
    lines.append(f"**Command:** `{br['command']}`")
    lines.append("")
    lines.append(f"**Run date:** {br['run_date']}")
    lines.append("")
    lines.append("**DB sha256 hashes:**")
    lines.append("")
    lines.append("| Version | sha256 |")
    lines.append("|---------|--------|")
    for v, h in br["db_sha256"].items():
        lines.append(f"| `{v}` | `{h}` |")
    lines.append("")

    if candidates_md:
        lines.append(
            f"**Ambiguous matcher candidates:** see "
            f"[{candidates_md.name}](./{candidates_md.name})."
        )
        lines.append("")

    return "\n".join(lines) + "\n"
