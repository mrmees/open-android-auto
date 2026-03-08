from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[3]))

from analysis.tools.proto_stream_validator.decode import decode_payload
from analysis.tools.proto_stream_validator.descriptors import build_descriptor_bundle
from analysis.tools.proto_stream_validator.diffing import DiffIssue, diff_normalized
from analysis.tools.proto_stream_validator.filtering import is_phase1_non_media
from analysis.tools.proto_stream_validator.io import load_capture_jsonl, write_normalized_baseline
from analysis.tools.proto_stream_validator.message_map import resolve_message_type
from analysis.tools.proto_stream_validator.normalize import normalize_decoded_frames


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate protobuf stream decoding against a locked baseline."
    )
    parser.add_argument("--capture", required=True, type=Path, help="Path to JSONL capture")
    parser.add_argument(
        "--baseline",
        required=True,
        type=Path,
        help="Path to normalized baseline JSON",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root containing oaa/ protos",
    )
    parser.add_argument(
        "--bless",
        action="store_true",
        help="Update baseline instead of enforcing no-regression diff",
    )
    parser.add_argument(
        "--reason",
        type=str,
        help="Required with --bless to document intentional change rationale",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print details about skipped frames",
    )
    return parser.parse_args(argv)


def _decode_frame(
    frame_index: int,
    frame: Any,
    bundle: Any,
) -> dict[str, Any]:
    try:
        payload = bytes.fromhex(frame.payload_hex)
    except ValueError as exc:
        raise ValueError(f"frame {frame_index}: invalid payload_hex") from exc

    try:
        message_type = resolve_message_type(
            frame.direction,
            frame.channel_id,
            frame.message_id,
            frame.message_name,
            frame.service_type,
        )
    except KeyError as exc:
        raise ValueError(f"frame {frame_index}: {exc}") from exc

    try:
        decoded = decode_payload(bundle, message_type, payload)
    except ValueError as exc:
        raise ValueError(f"frame {frame_index}: {exc}") from exc

    return {
        "frame_index": frame_index,
        "direction": frame.direction,
        "channel_id": frame.channel_id,
        "message_id": frame.message_id,
        "message_name": frame.message_name,
        "message_type": message_type,
        "decoded": decoded,
    }


def _classify_excluded_frame(frame: "Frame") -> str:
    """Classify why a frame was excluded from proto validation."""
    from analysis.tools.proto_stream_validator.filtering import (
        _AV_MEDIA_MESSAGE_IDS, _AV_PROTO_MESSAGE_IDS,
        _NON_PROTO_CONTROL_IDS, _IGNORED_NOISE_MESSAGE_NAMES,
        _is_av_channel,
    )
    if frame.channel_id == 0 and frame.message_id in _NON_PROTO_CONTROL_IDS:
        return "handshake_tls"
    if _is_av_channel(frame):
        if frame.message_id in _AV_MEDIA_MESSAGE_IDS:
            return "raw_av_media"
        if frame.message_id not in _AV_PROTO_MESSAGE_IDS:
            return "av_unknown"
    if frame.message_name in _IGNORED_NOISE_MESSAGE_NAMES:
        return "av_media_ack"
    if frame.message_name.startswith("0x"):
        return "unresolved"
    return "other_excluded"


class FrameStats:
    """Tracks frame classification counts for reporting."""

    _LABELS = {
        "proto_decoded": "Proto decoded",
        "proto_skipped": "Proto unmapped",
        "raw_av_media": "Raw AV media (H.264/PCM)",
        "handshake_tls": "Handshake/TLS",
        "av_media_ack": "AV media ACK",
        "av_unknown": "AV non-proto",
        "unresolved": "Unresolved msg ID",
        "other_excluded": "Other excluded",
    }

    def __init__(self) -> None:
        self.counts: dict[str, int] = {}

    def count(self, category: str) -> None:
        self.counts[category] = self.counts.get(category, 0) + 1

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    def format_report(self) -> str:
        total = self.total
        if total == 0:
            return "  (no frames)"

        decoded = self.counts.get("proto_decoded", 0)
        skipped = self.counts.get("proto_skipped", 0)
        proto_total = decoded + skipped
        excluded = total - proto_total

        lines = [f"  {total} total frames"]
        lines.append("")

        # Proto section
        lines.append(f"  Proto messages: {proto_total}")
        if decoded:
            lines.append(f"    Decoded:  {decoded:>5}  ({100 * decoded / total:.1f}%)")
        if skipped:
            lines.append(f"    Skipped:  {skipped:>5}  (unmapped message types)")

        # Excluded section
        lines.append(f"  Non-proto frames: {excluded}")
        for cat in ("raw_av_media", "handshake_tls", "av_media_ack",
                     "av_unknown", "unresolved", "other_excluded"):
            c = self.counts.get(cat, 0)
            if c:
                label = self._LABELS.get(cat, cat)
                lines.append(f"    {label + ':':.<30} {c:>5}  ({100 * c / total:.1f}%)")

        # Success rate
        if proto_total > 0:
            rate = 100 * decoded / proto_total
            lines.append("")
            lines.append(f"  Proto decode rate: {decoded}/{proto_total} ({rate:.0f}%)")

        return "\n".join(lines)


def build_normalized_rows(
    capture_path: Path, repo_root: Path, *, verbose: bool = False,
) -> tuple[list[dict[str, Any]], FrameStats]:
    frames = load_capture_jsonl(capture_path)
    stats = FrameStats()

    with tempfile.TemporaryDirectory(prefix="oaa-proto-validator-") as tmp_dir:
        bundle = build_descriptor_bundle(repo_root=repo_root, out_dir=Path(tmp_dir))

        rows: list[dict[str, Any]] = []
        for frame_index, frame in enumerate(frames):
            if not is_phase1_non_media(frame):
                stats.count(_classify_excluded_frame(frame))
                continue
            try:
                rows.append(_decode_frame(frame_index, frame, bundle))
                stats.count("proto_decoded")
            except ValueError as exc:
                if "unmapped tuple" in str(exc):
                    stats.count("proto_skipped")
                    if verbose:
                        print(f"skip: {exc}", file=sys.stderr)
                else:
                    raise

    return normalize_decoded_frames(rows), stats


def _load_baseline(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"baseline not found: {path}")

    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, list):
        raise ValueError("baseline must be a JSON array")

    rows = [row for row in loaded if isinstance(row, dict)]
    if len(rows) != len(loaded):
        raise ValueError("baseline rows must all be JSON objects")

    return normalize_decoded_frames(rows)


def _format_diff(diff: DiffIssue) -> str:
    return f"{diff.kind}: {diff.path} expected={diff.expected!r} actual={diff.actual!r}"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.bless and not args.reason:
        print("error: --reason is required with --bless", file=sys.stderr)
        return 2

    try:
        actual_rows, stats = build_normalized_rows(
            capture_path=args.capture,
            repo_root=args.repo_root.resolve(),
            verbose=args.verbose,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.bless:
        write_normalized_baseline(args.baseline, actual_rows)
        print(f"baseline updated: {args.baseline}")
        print(f"reason: {args.reason}")
        print()
        print(stats.format_report())
        return 0

    try:
        expected_rows = _load_baseline(args.baseline)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    diffs = diff_normalized(expected_rows, actual_rows)
    if diffs:
        print("FAIL: baseline drift detected", file=sys.stderr)
        for diff in diffs[:50]:
            print(_format_diff(diff), file=sys.stderr)
        if len(diffs) > 50:
            print(f"... {len(diffs) - 50} more diffs", file=sys.stderr)
        print()
        print(stats.format_report())
        return 1

    print(f"PASS: {args.capture.name}")
    print(stats.format_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
