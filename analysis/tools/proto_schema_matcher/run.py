from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .dispatch import extract_dispatch_observations
from .loaders import load_apk_schema, load_canonical_schema
from .matcher import match_enum_domains, match_graphs
from .report import build_payload, write_json, write_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Match canonical OAA schemas to obfuscated APK protobuf classes"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--jadx-root",
        type=Path,
        help="JADX output root containing sources/",
    )
    source.add_argument(
        "--proto-classes-json",
        type=Path,
        help="apk-index proto_classes.json or complete signals JSON",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Repository root containing oaa/ (default: auto-detect)",
    )
    parser.add_argument("--version", required=True, help="APK version label")
    parser.add_argument("--apk-sha256", default="unknown", help="Source APK SHA-256")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args(argv)

    print("Building canonical descriptor graph...", file=sys.stderr)
    canonical_graph, canonical_enums = load_canonical_schema(args.repo_root.resolve())
    print(f"  {len(canonical_graph)} canonical messages", file=sys.stderr)
    print(f"  {len(canonical_enums)} canonical enums", file=sys.stderr)

    print("Loading APK protobuf graph...", file=sys.stderr)
    apk_graph, apk_enums = load_apk_schema(
        jadx_root=args.jadx_root,
        proto_classes_json=args.proto_classes_json,
    )
    print(f"  {len(apk_graph)} decoded APK messages", file=sys.stderr)
    print(f"  {len(apk_enums)} decoded APK enums", file=sys.stderr)

    observations = []
    if args.jadx_root:
        print("Extracting static dispatch observations...", file=sys.stderr)
        observations = extract_dispatch_observations(
            args.jadx_root,
            set(apk_graph),
            set(canonical_graph),
        )
        print(f"  {len(observations)} observations", file=sys.stderr)

    results = match_graphs(
        canonical_graph,
        apk_graph,
        observations,
        canonical_enums,
        apk_enums,
    )
    enum_matches = match_enum_domains(canonical_enums, apk_enums)
    payload = build_payload(
        version=args.version,
        apk_sha256=args.apk_sha256,
        canonical_count=len(canonical_graph),
        apk_count=len(apk_graph),
        canonical_edge_count=sum(
            field.target is not None
            for node in canonical_graph.values()
            for field in node.fields
            if field.base_type in {"message", "group"}
        ),
        apk_edge_count=sum(
            field.target is not None
            for node in apk_graph.values()
            for field in node.fields
            if field.base_type in {"message", "group"}
        ),
        canonical_graph=canonical_graph,
        apk_graph=apk_graph,
        canonical_enums=canonical_enums,
        apk_enums=apk_enums,
        enum_matches=enum_matches,
        results=results,
        observations=observations,
    )
    write_json(payload, args.output_json)
    write_markdown(payload, args.output_md)
    summary = payload["summary"]
    assert isinstance(summary, dict)
    print(
        f"Resolved {summary['resolved']} mappings "
        f"({summary['high_confidence']} high, {summary['medium_confidence']} medium)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
