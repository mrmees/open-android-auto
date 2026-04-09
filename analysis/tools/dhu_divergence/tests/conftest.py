from __future__ import annotations

import json
from pathlib import Path

import pytest

# Repo root = .../open-android-auto
# parents: tests -> dhu_divergence -> tools -> analysis -> repo
REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def schema(repo_root: Path) -> dict:
    return json.loads((repo_root / "docs/verification/audit-schema.json").read_text())
