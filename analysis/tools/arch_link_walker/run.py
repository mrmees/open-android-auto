"""CLI entry point for the architecture cross-link walker."""
from __future__ import annotations

import sys
from pathlib import Path

from analysis.tools.arch_link_walker.walker import walk


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parents[3]
    results = walk(repo_root)
    modified = sum(1 for v in results.values() if v)
    skipped = sum(1 for v in results.values() if not v)
    print(f"Walker complete: {modified} modified, {skipped} skipped (already present or excluded)")
    for path, was_modified in sorted(results.items()):
        status = "MODIFIED" if was_modified else "skipped"
        print(f"  {path}: {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
