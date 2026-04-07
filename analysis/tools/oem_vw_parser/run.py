from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from analysis.tools.proto_stream_validator.descriptors import build_descriptor_bundle

from .io import load_session_json, load_vw_capture
from .manifests import emit_classification_json
from .reports import emit_classification_report
from .tier_classifier import classify_capture


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the VW capture parser.

    Plan 07-01 implements only the classification path. Plan 07-02 will
    extend main() with SDP value extraction, the coverage manifest, the
    OEM-only candidate diff, and a one-line README correction.
    """
    parser = argparse.ArgumentParser(description="VW MIB3 OI capture parser")
    parser.add_argument(
        "--vw",
        type=Path,
        required=True,
        help="VW capture directory (must contain messages.jsonl and session.json)",
    )
    parser.add_argument(
        "--dhu",
        type=Path,
        action="append",
        default=[],
        help="DHU baseline capture directory (repeatable; consumed by 07-02)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output report directory",
    )
    args = parser.parse_args(argv)

    # Validates capture_version is the JSON integer 5 (numeric, not string).
    load_session_json(args.vw / "session.json")

    # Load records
    vw_records = list(
        load_vw_capture(args.vw / "messages.jsonl", capture_id=args.vw.name)
    )

    # Build descriptor bundle once. The bundle's descriptor set goes to a
    # tmp dir — it's an intermediate artifact, not a phase deliverable.
    repo_root = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="oem_vw_parser_bundle_") as td:
        bundle = build_descriptor_bundle(repo_root=repo_root, out_dir=Path(td))

        # Classify
        classified, profile = classify_capture(vw_records, bundle)

    # Compute capture window from record timestamps
    ts_values = [r.ts_ms for r in vw_records]
    capture_window_s = (
        (max(ts_values) - min(ts_values)) / 1000.0 if ts_values else 0.0
    )

    # Emit classification reports
    emit_classification_report(
        classified,
        profile,
        args.out / "msg-type-classification.md",
        capture_id=args.vw.name,
        capture_window_s=capture_window_s,
        total_records=len(vw_records),
    )
    emit_classification_json(
        classified,
        profile,
        args.out / "msg-type-classification.json",
        capture_id=args.vw.name,
        total_records=len(vw_records),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
