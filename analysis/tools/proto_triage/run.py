"""CLI entry point for proto class triage tool."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analysis.tools.proto_triage.db import (
    build_class_to_packages,
    build_file_to_classes,
    build_sub_message_graph,
    load_class_references,
    load_proto_universe,
    load_seed_service_map,
    load_seeds,
)
from analysis.tools.proto_triage.report import generate_report, write_report
from analysis.tools.proto_triage.score import TriageCategory, score_all
from analysis.tools.proto_triage.signals import (
    compute_bfs_signal,
    compute_hub_signal,
    compute_package_signal,
    compute_structural_signal,
    compute_telemetry_cluster,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Triage unmapped APK proto classes into wire-relevant vs internal."
    )
    parser.add_argument(
        "--db", type=Path, required=True,
        help="Path to APK index SQLite database",
    )
    parser.add_argument(
        "--mapping", type=Path, default=None,
        help="Path to class_mapping.yaml (default: auto-detect)",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Output file for markdown report (default: stdout)",
    )
    parser.add_argument(
        "--version", type=str, default="16.1",
        help="APK version to use for seed resolution (default: 16.1)",
    )
    parser.add_argument(
        "--min-confidence", type=float, default=0.0,
        help="Only show results above this confidence threshold",
    )
    parser.add_argument(
        "--service", type=str, default=None,
        help="Filter wire candidates to a specific service label",
    )
    args = parser.parse_args(argv)

    # --- Load data ---
    print("Loading seeds from class_mapping.yaml...", file=sys.stderr)
    seeds = load_seeds(args.mapping, args.version)
    seed_service_map = load_seed_service_map(args.mapping, args.version)
    print(f"  {len(seeds)} known wire classes", file=sys.stderr)

    print("Loading proto universe from DB...", file=sys.stderr)
    universe = load_proto_universe(args.db)
    print(f"  {len(universe)} total proto classes", file=sys.stderr)

    print("Loading class references...", file=sys.stderr)
    refs = load_class_references(args.db)
    print(f"  {len(refs)} class references", file=sys.stderr)

    # --- Build indexes ---
    print("Building indexes...", file=sys.stderr)
    graph = build_sub_message_graph(universe)
    file_to_classes = build_file_to_classes(refs, universe)
    class_to_packages = build_class_to_packages(refs, universe)
    print(f"  graph: {len(graph)} nodes with edges", file=sys.stderr)
    print(f"  files referencing protos: {len(file_to_classes)}", file=sys.stderr)

    # --- Detect telemetry cluster ---
    print("Detecting telemetry clusters...", file=sys.stderr)
    telemetry = compute_telemetry_cluster(universe, seeds, class_to_packages)
    print(f"  {len(telemetry)} telemetry classes excluded", file=sys.stderr)

    # --- Compute signals ---
    print("Computing Signal 1: sub-message BFS...", file=sys.stderr)
    bfs = compute_bfs_signal(graph, seeds, excluded=telemetry)
    print(f"  {len(bfs.hop_distance)} classes reachable", file=sys.stderr)

    print("Computing Signal 2: hub file co-reference...", file=sys.stderr)
    hub = compute_hub_signal(file_to_classes, seeds)
    print(f"  {len(hub.hub_file_count)} classes from hub files", file=sys.stderr)

    print("Computing Signal 3: package classification...", file=sys.stderr)
    pkg = compute_package_signal(class_to_packages, seeds)
    internal_count = sum(1 for v in pkg.classification.values() if v == "INTERNAL")
    wire_count = sum(1 for v in pkg.classification.values() if v == "WIRE")
    print(f"  {internal_count} INTERNAL, {wire_count} WIRE by package", file=sys.stderr)

    print("Computing Signal 4: structural features...", file=sys.stderr)
    struct = compute_structural_signal(universe, seeds)
    print(f"  {len(struct.features)} classes with features", file=sys.stderr)

    # --- Score ---
    print("Scoring...", file=sys.stderr)
    results = score_all(
        universe, seeds, bfs, hub, pkg, struct,
        seed_service_map, hub, file_to_classes,
        telemetry_cluster=telemetry,
    )

    # --- Apply filters ---
    if args.min_confidence > 0:
        results = [r for r in results if r.confidence >= args.min_confidence]

    if args.service:
        svc_filter = args.service.lower()
        filtered = []
        for r in results:
            if r.category in (TriageCategory.WIRE_HIGH, TriageCategory.WIRE_MEDIUM, TriageCategory.WIRE_LOW):
                if r.service_label.lower() == svc_filter:
                    filtered.append(r)
            else:
                filtered.append(r)
        results = filtered

    # --- Report ---
    from collections import Counter
    cat_counts = Counter(r.category.value for r in results)
    print(f"\nResults: {dict(cat_counts)}", file=sys.stderr)

    report = generate_report(results, len(seeds), len(universe))

    if args.output:
        write_report(report, args.output)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
