from __future__ import annotations

from pathlib import Path
import argparse
import json
import math
import sys
import time

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[3]))

from analysis.tools.apk_indexer.run_indexer import run_indexer


def benchmark_runs(samples: list[float]) -> dict[str, float | int]:
    if not samples:
        return {
            "runs": 0,
            "mean_seconds": 0.0,
            "p95_seconds": 0.0,
            "min_seconds": 0.0,
            "max_seconds": 0.0,
        }

    ordered = sorted(samples)
    p95_idx = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return {
        "runs": len(samples),
        "mean_seconds": sum(samples) / len(samples),
        "p95_seconds": ordered[p95_idx],
        "min_seconds": ordered[0],
        "max_seconds": ordered[-1],
    }


def run_benchmark(
    source_root: Path, analysis_root: Path, runs: int, scope: str = "all"
) -> dict[str, object]:
    samples: list[float] = []
    for _ in range(runs):
        start = time.perf_counter()
        run_indexer(source_root, analysis_root, scope=scope)
        samples.append(time.perf_counter() - start)

    metrics = benchmark_runs(samples)
    return {
        "source": str(source_root),
        "analysis_root": str(analysis_root),
        "scope": scope,
        "samples_seconds": samples,
        **metrics,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark end-to-end wall-clock time for apk indexer runs."
    )
    parser.add_argument("--source", required=True, type=Path, help="Path to decompiled APK root")
    parser.add_argument(
        "--analysis-root",
        required=True,
        type=Path,
        help="Root directory where analysis outputs are written",
    )
    parser.add_argument(
        "--scope",
        choices=("all", "projection"),
        default="all",
        help="Optional filter scope for extracted files",
    )
    parser.add_argument("--runs", type=int, default=3, help="Number of benchmark runs")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write JSON benchmark output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_benchmark(
        source_root=args.source,
        analysis_root=args.analysis_root,
        runs=args.runs,
        scope=args.scope,
    )
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
