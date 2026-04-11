from __future__ import annotations
import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    """CLI entry point -- Plan 10-02 implements the walker loop."""
    parser = argparse.ArgumentParser(
        prog="promotion_walker",
        description="Phase 10 promotion walker \u2014 walks oaa/{av,media,video,audio}/ "
                    "sidecars against the VW capture, writes verdicts, commits atomically.",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Print verdicts + write reports to tmp; no sidecar writes, no commits")
    parser.add_argument("--scope-dir", action="append", default=None,
                        help="Override scope directories (default: oaa/av oaa/media oaa/video oaa/audio)")
    parser.add_argument("--capture", default="captures/oem-vw-mib3oi-2026-04-06/",
                        help="VW capture directory (messages.jsonl + session.json)")
    parser.add_argument("--coverage", default="analysis/reports/oem-vw/coverage.json",
                        help="Phase 7 coverage manifest (attribution source)")
    parser.add_argument("--sdp", default="analysis/reports/oem-vw/sdp-values.json",
                        help="Phase 7 SDP values (for MATCH-08 channel_kind set)")
    parser.add_argument("--classification", default="analysis/reports/oem-vw/msg-type-classification.json",
                        help="Phase 7 fragment classification (for message_completeness resolution)")
    parser.add_argument("--out", default="analysis/reports/oem-vw/",
                        help="Output directory for promotion-walk.{md,json} + worklist")
    args = parser.parse_args(argv)
    _ = args  # unused in stub
    raise NotImplementedError("Plan 10-02 implements the walker loop")


if __name__ == "__main__":
    sys.exit(main())
