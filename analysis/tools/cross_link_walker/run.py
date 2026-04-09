"""Cross-link walker CLI.

Run against the real docs tree:

    PYTHONPATH=. python3 -m analysis.tools.cross_link_walker.run --repo-root .

A second run on the same tree is always a no-op (idempotency check).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .walker import SENTINEL, WALKER_TARGETS, walk


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cross-link walker for Phase 9 TIER-05 non-claim callouts",
    )
    parser.add_argument("--repo-root", default=".", help="Repo root (default: cwd)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report which targets would be modified without writing",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    if args.dry_run:
        for rel in WALKER_TARGETS:
            doc = repo_root / rel
            text = doc.read_text(encoding="utf-8")
            status = "no-op" if SENTINEL in text else "would-insert"
            print(f"[{status}] {rel}")
        return 0

    results = walk(repo_root)
    modified = sum(1 for v in results.values() if v)
    for rel, was_modified in results.items():
        marker = "INSERTED" if was_modified else "no-op"
        print(f"[{marker}] {rel}")
    print(f"\nWalker summary: {modified}/{len(results)} files modified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
