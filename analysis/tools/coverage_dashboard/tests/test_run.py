from __future__ import annotations

import json
from pathlib import Path

from analysis.tools.coverage_dashboard.run import main


def test_cli_stdout_has_table(mock_oaa_tree: Path, capsys) -> None:
    """main() prints tier table to stdout."""
    rc = main(["--output-dir", str(mock_oaa_tree / "out")])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Channel" in captured.out
    assert "Bronze" in captured.out


def test_cli_writes_both_files(mock_oaa_tree: Path) -> None:
    """main() creates both .md and .json in output dir."""
    out = mock_oaa_tree / "out"
    rc = main(["--output-dir", str(out)])
    assert rc == 0
    assert (out / "coverage-dashboard.md").exists()
    assert (out / "coverage-dashboard.json").exists()


def test_cli_quiet_flag(mock_oaa_tree: Path, capsys) -> None:
    """--quiet suppresses stdout, files still written."""
    out = mock_oaa_tree / "out"
    rc = main(["--output-dir", str(out), "--quiet"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Channel" not in captured.out
    assert (out / "coverage-dashboard.md").exists()
    assert (out / "coverage-dashboard.json").exists()


def test_cli_json_only_flag(mock_oaa_tree: Path) -> None:
    """--json-only writes only .json, no .md."""
    out = mock_oaa_tree / "out"
    rc = main(["--output-dir", str(out), "--json-only"])
    assert rc == 0
    assert (out / "coverage-dashboard.json").exists()
    assert not (out / "coverage-dashboard.md").exists()


def test_cli_output_dir_override(mock_oaa_tree: Path) -> None:
    """--output-dir <path> writes to custom location."""
    custom = mock_oaa_tree / "custom_output"
    rc = main(["--output-dir", str(custom)])
    assert rc == 0
    assert (custom / "coverage-dashboard.md").exists()
    assert (custom / "coverage-dashboard.json").exists()


def test_cli_exit_code_zero(mock_oaa_tree: Path) -> None:
    """main() returns 0 on success."""
    out = mock_oaa_tree / "out"
    rc = main(["--output-dir", str(out), "--quiet"])
    assert rc == 0


# ---------------------------------------------------------------------------
# Live snapshot test — runs against the real oaa/ tree
# ---------------------------------------------------------------------------

def _find_repo_root() -> Path:
    """Walk up from this file to find the directory containing oaa/."""
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "oaa").is_dir():
            return parent
    raise RuntimeError("Cannot locate repo root with oaa/ directory")


def test_live_snapshot() -> None:
    """Run against the real oaa/ tree and assert locked census numbers.

    If this test fails, the oaa/ tree has been modified. Verify the change
    is intentional, then update the snapshot values below.

    Census changed? Update snapshot values after verifying the change is intentional.
    """
    from analysis.tools.coverage_dashboard.scanner import scan_audit_tree

    repo_root = _find_repo_root()
    result = scan_audit_tree(repo_root)

    # Total counts
    assert result.total_sidecars == 160, (
        f"Expected 160 sidecars, got {result.total_sidecars}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert result.total_protos == 245, (
        f"Expected 245 protos, got {result.total_protos}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )

    # Missing and orphan counts
    total_missing = sum(len(v) for v in result.missing_sidecars.values())
    assert total_missing == 85, (
        f"Expected 85 missing sidecars, got {total_missing}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    total_orphan = sum(len(v) for v in result.orphan_sidecars.values())
    assert total_orphan == 0, (
        f"Expected 0 orphan sidecars, got {total_orphan}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )

    # Tier counts (sum across all channels)
    total_bronze = sum(c.bronze for c in result.per_channel.values())
    total_silver = sum(c.silver for c in result.per_channel.values())
    total_gold = sum(c.gold for c in result.per_channel.values())
    total_platinum = sum(c.platinum for c in result.per_channel.values())
    total_retracted = sum(c.retracted for c in result.per_channel.values())
    total_superseded = sum(c.superseded for c in result.per_channel.values())

    assert total_platinum == 3, (
        f"Expected 3 platinum, got {total_platinum}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert total_gold == 29, (
        f"Expected 29 gold, got {total_gold}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert total_silver == 111, (
        f"Expected 111 silver, got {total_silver}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert total_bronze == 10, (
        f"Expected 10 bronze, got {total_bronze}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert total_retracted == 6, (
        f"Expected 6 retracted, got {total_retracted}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert total_superseded == 1, (
        f"Expected 1 superseded, got {total_superseded}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )

    # Directory count
    assert result.directories_scanned == 19, (
        f"Expected 19 directories, got {result.directories_scanned}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )

    # Pending gold count
    assert result.pending_gold_count == 21, (
        f"Expected 21 pending_gold, got {result.pending_gold_count}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
