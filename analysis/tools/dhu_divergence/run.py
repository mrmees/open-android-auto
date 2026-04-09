"""CLI entry point for the DHU divergence tool (Phase 9 OEM-04).

Reads VW SDP from the pre-parsed Phase 7 `sdp-values.json` (saves a descriptor
bundle build for the VW side), then re-decodes each DHU baseline's raw
`sdp_response.bin` via `oem_vw_parser.sdp_decode`. Writes `dhu-divergence.md`
and `dhu-divergence.json` to the requested output directory.

Example:
  PYTHONPATH=. python3 -m analysis.tools.dhu_divergence.run \
      --vw-sdp-json analysis/reports/oem-vw/sdp-values.json \
      --dhu captures/general \
      --dhu captures/idle-baseline \
      --dhu captures/music-playback \
      --dhu captures/active-navigation \
      --delta-report analysis/reports/cross-version/16-4-delta-report.json \
      --out analysis/reports/oem-vw/ \
      --repo-root .
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from analysis.tools.proto_stream_validator.descriptors import build_descriptor_bundle

from .attribution import classify_divergence
from .baseline_merge import load_dhu_baseline, merge_baselines
from .divergence import compute_divergences, load_vw_channels
from .report import build_json, emit_json, emit_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="VW vs DHU SDP divergence report generator (Phase 9 OEM-04)"
    )
    parser.add_argument(
        "--vw-sdp-json",
        type=Path,
        required=True,
        help="Path to Phase 7 sdp-values.json",
    )
    parser.add_argument(
        "--dhu",
        action="append",
        type=Path,
        required=True,
        help="Path to a DHU capture directory containing sdp_response.bin (repeatable)",
    )
    parser.add_argument(
        "--delta-report",
        type=Path,
        required=True,
        help="Path to Phase 8 16-4-delta-report.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output directory (dhu-divergence.md + .json will be written here)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root (default: cwd, used for descriptor bundle construction)",
    )
    args = parser.parse_args(argv)

    # Load VW SDP (pre-parsed).
    vw_sdp_values = json.loads(args.vw_sdp_json.read_text())
    vw_channels = load_vw_channels(vw_sdp_values)

    # Load Phase 8 delta report.
    delta_report = json.loads(args.delta_report.read_text())

    # Build descriptor bundle for DHU SDP decoding, then load baselines.
    with tempfile.TemporaryDirectory() as tmp:
        bundle = build_descriptor_bundle(
            repo_root=args.repo_root, out_dir=Path(tmp)
        )

        baselines = []
        for dhu_dir in args.dhu:
            name = dhu_dir.name  # e.g. "general", "idle-baseline"
            bl = load_dhu_baseline(bundle, name, dhu_dir)
            baselines.append(bl)

        merged = merge_baselines(baselines)

        # Compute divergences.
        divergences = compute_divergences(vw_channels, merged)

        # Classify each.
        attributed = [classify_divergence(d, delta_report) for d in divergences]

        # Build the JSON sidecar data.
        data = build_json(
            attributed=attributed,
            merged_dhu=merged,
            vw_sdp_values=vw_sdp_values,
            vw_capture_path="captures/oem-vw-mib3oi-2026-04-06/",
            delta_report_path=args.delta_report,
        )

        # Emit both report forms.
        args.out.mkdir(parents=True, exist_ok=True)
        emit_json(data, args.out / "dhu-divergence.json")
        emit_markdown(data, args.out / "dhu-divergence.md")

    print(f"Wrote {args.out / 'dhu-divergence.json'}")
    print(f"Wrote {args.out / 'dhu-divergence.md'}")
    print(f"Summary: {data['summary']['by_attribution']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
