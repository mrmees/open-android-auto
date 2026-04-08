"""CLI entry point for the cross-version comparison tool.

Usage:
    python -m analysis.tools.cross_version.run [options]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    _root = Path(__file__).resolve().parents[3]
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

from analysis.tools.cross_version.compare import run_comparison
from analysis.tools.cross_version.delta_report import generate_delta_report
from analysis.tools.cross_version.promote import promote_sidecars
from analysis.tools.cross_version.report import generate_report
from analysis.tools.cross_version.tables import generate_tables
from analysis.tools.proto_schema_validator.mapping import load_mapping
from analysis.tools.seed_import.annotate import annotate_directory

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ANALYSIS = _REPO_ROOT / "analysis"


def _find_db(version_prefix: str) -> Path | None:
    """Find APK index DB matching a version prefix."""
    for d in sorted(_ANALYSIS.glob(f"android_auto_{version_prefix}*")):
        db = d / "apk-index" / "sqlite" / "apk_index.db"
        if db.exists():
            return db
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cross-version proto structure comparison tool",
        prog="python -m analysis.tools.cross_version.run",
    )
    parser.add_argument(
        "--db-15_9",
        type=Path,
        default=None,
        help="Path to 15.9 APK index DB (auto-detected if omitted)",
    )
    parser.add_argument(
        "--db-16_1",
        type=Path,
        default=None,
        help="Path to 16.1 APK index DB (auto-detected if omitted)",
    )
    parser.add_argument(
        "--db-16_2",
        type=Path,
        default=None,
        help="Path to 16.2 APK index DB (auto-detected if omitted)",
    )
    parser.add_argument(
        "--db-16_4",
        type=Path,
        default=None,
        help="Path to 16.4 APK index DB (auto-detected if omitted, canonical build 661014)",
    )
    parser.add_argument(
        "--promote",
        action="store_true",
        default=False,
        help="Enable sidecar promotion (default: dry-run, no promotion)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_REPO_ROOT / "docs" / "cross-version",
        help="Output directory for markdown files (default: docs/cross-version/)",
    )
    parser.add_argument(
        "--skip-delta-report",
        action="store_true",
        default=False,
        help="Skip generating the 16.4 delta report (useful for 3-version-only runs)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Resolve DB paths
    db_paths: dict[str, Path] = {}

    db_159 = args.db_15_9 or _find_db("15.9")
    if db_159:
        db_paths["15.9"] = db_159
    else:
        print("WARNING: 15.9 DB not found, proceeding without it", file=sys.stderr)

    db_161 = args.db_16_1 or _find_db("16.1")
    if db_161:
        db_paths["16.1"] = db_161
    else:
        print("WARNING: 16.1 DB not found, proceeding without it", file=sys.stderr)

    db_162 = args.db_16_2 or _find_db("16.2")
    if db_162:
        db_paths["16.2"] = db_162
    else:
        print("WARNING: 16.2 DB not found, proceeding without it", file=sys.stderr)

    db_164 = args.db_16_4 or _find_db("16.4")
    if db_164:
        db_paths["16.4"] = db_164
    else:
        print("WARNING: 16.4 DB not found, proceeding without it", file=sys.stderr)

    if len(db_paths) < 2:
        print("ERROR: Need at least 2 version DBs for comparison", file=sys.stderr)
        return 2

    print(f"Comparing {len(db_paths)} versions: {', '.join(sorted(db_paths))}")
    for v, p in sorted(db_paths.items()):
        print(f"  {v}: {p}")

    # Load mappings
    mappings = load_mapping()
    print(f"Loaded {len(mappings)} mappings from class_mapping.yaml")

    # Run comparison
    results = run_comparison(db_paths, mappings)
    consistent = sum(1 for r in results if r.is_consistent)
    print(f"Compared {len(results)} mappings: {consistent} consistent, "
          f"{len(results) - consistent} with discrepancies")

    # Generate tables
    table_files = generate_tables(db_paths, mappings, args.output_dir)
    print(f"Generated {len(table_files)} mapping table(s) in {args.output_dir}")

    # Promote sidecars
    promotion_count = 0
    if args.promote:
        promotion_count = promote_sidecars(results)
        print(f"Promoted {promotion_count} sidecar(s) from bronze to silver")
        if promotion_count > 0:
            # Re-annotate proto files so confidence comments match promoted sidecars
            oaa_root = _REPO_ROOT / "oaa"
            annotated = 0
            for proto_dir in sorted(oaa_root.iterdir()):
                if proto_dir.is_dir():
                    stats = annotate_directory(proto_dir)
                    annotated += stats["files"]
            print(f"Re-annotated {annotated} proto file(s) after promotion")
    else:
        eligible = sum(1 for r in results if r.is_consistent and r.pairs_compared)
        print(f"Promotion skipped (dry-run). {eligible} sidecars eligible. "
              f"Use --promote to enable.")

    # Generate 3-version consistency report (existing output)
    report_path = args.output_dir / "consistency-report.md"
    exit_code = generate_report(results, report_path, promotion_count)
    print(f"Report written to {report_path}")

    # Generate 16.4 delta report (XVER-02) when 16.4 is in play
    if "16.4" in db_paths and not args.skip_delta_report:
        delta_dir = _REPO_ROOT / "analysis" / "reports" / "cross-version"
        candidates_path = delta_dir / "16-4-mapping-candidates.md"
        generate_delta_report(
            results=results,
            db_paths=db_paths,
            all_mappings_results=results,
            mapping_candidates_md=candidates_path if candidates_path.exists() else None,
            output_dir=delta_dir,
        )
        print(f"16.4 delta report written to {delta_dir}/16-4-delta-report.md")
        print(f"16.4 delta JSON sidecar written to {delta_dir}/16-4-delta-report.json")

    if exit_code == 0:
        print("Result: All mappings consistent (no suspicious discrepancies)")
    else:
        print("Result: Suspicious discrepancies found (see report)")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
