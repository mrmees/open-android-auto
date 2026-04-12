from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analysis.tools.coverage_dashboard.scanner import scan_audit_tree
from analysis.tools.coverage_dashboard.report import render_markdown, render_json, _extract_tier_table


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for coverage dashboard."""
    parser = argparse.ArgumentParser(
        prog="coverage_dashboard",
        description="Generate coverage dashboard from oaa/ audit sidecars.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: analysis/reports/coverage-dashboard/)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress stdout table output (files still written)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Write only JSON sidecar (no markdown)",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Override repo root (default: auto-detected from package location)",
    )
    args = parser.parse_args(argv)

    # Determine repo root
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        repo_root = Path(__file__).resolve().parents[3]

    result = scan_audit_tree(repo_root)

    # Determine output directory
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = repo_root / "analysis" / "reports" / "coverage-dashboard"

    out_dir.mkdir(parents=True, exist_ok=True)

    # Generate reports
    json_str = render_json(result)

    if not args.json_only:
        md_str = render_markdown(result)
        (out_dir / "coverage-dashboard.md").write_text(md_str)

    (out_dir / "coverage-dashboard.json").write_text(json_str)

    # Print tier table to stdout (unless --quiet)
    if not args.quiet:
        if not args.json_only:
            table = _extract_tier_table(md_str)
        else:
            # Generate markdown just for the table even in json-only mode
            md_str = render_markdown(result)
            table = _extract_tier_table(md_str)
        print(table)

    # Status messages to stderr
    if not args.json_only:
        print(f"Wrote {out_dir / 'coverage-dashboard.md'}", file=sys.stderr)
    print(f"Wrote {out_dir / 'coverage-dashboard.json'}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
