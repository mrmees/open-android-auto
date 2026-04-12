"""Architecture cross-link walker for Phase 11.

Stub -- tests should fail.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

SENTINEL = ""
CALLOUT_CHANNELS = ""
CALLOUT_README = ""
WALKER_TARGETS: dict[str, Literal["channels", "readme"]] = {}
WALKER_EXCLUDE: set[str] = set()


def insert_cross_link(doc_path: Path, variant: Literal["channels", "readme"]) -> bool:
    raise NotImplementedError("Stub")


def walk(repo_root: Path) -> dict[str, bool]:
    raise NotImplementedError("Stub")
