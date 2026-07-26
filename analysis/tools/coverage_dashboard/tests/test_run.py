from __future__ import annotations

import json
from pathlib import Path

from analysis.tools.coverage_dashboard.run import main


def _cli_args(mock_oaa_tree: Path, out_name: str = "out", extra: list[str] | None = None) -> list[str]:
    """Build CLI args pointing at the mock tree."""
    out = str(mock_oaa_tree / out_name)
    args = ["--repo-root", str(mock_oaa_tree), "--output-dir", out]
    if extra:
        args.extend(extra)
    return args


def test_cli_stdout_has_table(mock_oaa_tree: Path, capsys) -> None:
    """main() prints tier table to stdout."""
    rc = main(_cli_args(mock_oaa_tree))
    assert rc == 0
    captured = capsys.readouterr()
    assert "Channel" in captured.out
    assert "Bronze" in captured.out


def test_cli_writes_both_files(mock_oaa_tree: Path) -> None:
    """main() creates both .md and .json in output dir."""
    out = mock_oaa_tree / "out"
    rc = main(_cli_args(mock_oaa_tree))
    assert rc == 0
    assert (out / "coverage-dashboard.md").exists()
    assert (out / "coverage-dashboard.json").exists()


def test_cli_quiet_flag(mock_oaa_tree: Path, capsys) -> None:
    """--quiet suppresses stdout, files still written."""
    out = mock_oaa_tree / "out"
    rc = main(_cli_args(mock_oaa_tree, extra=["--quiet"]))
    assert rc == 0
    captured = capsys.readouterr()
    assert "Channel" not in captured.out
    assert (out / "coverage-dashboard.md").exists()
    assert (out / "coverage-dashboard.json").exists()


def test_cli_json_only_flag(mock_oaa_tree: Path) -> None:
    """--json-only writes only .json, no .md."""
    out = mock_oaa_tree / "out"
    rc = main(_cli_args(mock_oaa_tree, extra=["--json-only"]))
    assert rc == 0
    assert (out / "coverage-dashboard.json").exists()
    assert not (out / "coverage-dashboard.md").exists()


def test_cli_output_dir_override(mock_oaa_tree: Path) -> None:
    """--output-dir <path> writes to custom location."""
    rc = main(_cli_args(mock_oaa_tree, out_name="custom_output"))
    assert rc == 0
    custom = mock_oaa_tree / "custom_output"
    assert (custom / "coverage-dashboard.md").exists()
    assert (custom / "coverage-dashboard.json").exists()


def test_cli_exit_code_zero(mock_oaa_tree: Path) -> None:
    """main() returns 0 on success."""
    rc = main(_cli_args(mock_oaa_tree, extra=["--quiet"]))
    assert rc == 0


# ---------------------------------------------------------------------------
# Live snapshot test -- runs against the real oaa/ tree
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
    assert result.total_sidecars == 169, (
        f"Expected 169 sidecars, got {result.total_sidecars}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert result.total_protos == 248, (
        f"Expected 248 protos, got {result.total_protos}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )

    # Missing and orphan counts
    total_missing = sum(len(v) for v in result.missing_sidecars.values())
    assert total_missing == 79, (
        f"Expected 79 missing sidecars, got {total_missing}. "
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

    assert total_platinum == 0, (
        f"Expected 0 platinum, got {total_platinum}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert total_gold == 15, (
        f"Expected 15 gold, got {total_gold}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert total_silver == 118, (
        f"Expected 118 silver, got {total_silver}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert total_bronze == 23, (
        f"Expected 23 bronze, got {total_bronze}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert total_retracted == 13, (
        f"Expected 13 retracted, got {total_retracted}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
    assert total_superseded == 0, (
        f"Expected 0 superseded, got {total_superseded}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )

    # Directory count
    assert result.directories_scanned == 20, (
        f"Expected 20 directories, got {result.directories_scanned}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )

    # Pending gold count
    assert result.pending_gold_count == 0, (
        f"Expected 0 pending_gold, got {result.pending_gold_count}. "
        "Census changed? Update snapshot values after verifying the change is intentional."
    )
