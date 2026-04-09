from __future__ import annotations

from pathlib import Path

import pytest

# Repo root = .../open-android-auto
# parents: tests -> cross_link_walker -> tools -> analysis -> repo
REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"
