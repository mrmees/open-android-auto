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
        message_type = resolve_message_type(frame.direction, frame.channel_id, frame.message_id)
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


def build_normalized_rows(capture_path: Path, repo_root: Path) -> list[dict[str, Any]]:
    frames = load_capture_jsonl(capture_path)

    with tempfile.TemporaryDirectory(prefix="oaa-proto-validator-") as tmp_dir:
        bundle = build_descriptor_bundle(repo_root=repo_root, out_dir=Path(tmp_dir))

        rows: list[dict[str, Any]] = []
        for frame_index, frame in enumerate(frames):
            if not is_phase1_non_media(frame):
                continue
            rows.append(_decode_frame(frame_index, frame, bundle))

    return normalize_decoded_frames(rows)


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
        actual_rows = build_normalized_rows(
            capture_path=args.capture,
            repo_root=args.repo_root.resolve(),
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.bless:
        write_normalized_baseline(args.baseline, actual_rows)
        print(f"baseline updated: {args.baseline}")
        print(f"reason: {args.reason}")
        return 0

    try:
        expected_rows = _load_baseline(args.baseline)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    diffs = diff_normalized(expected_rows, actual_rows)
    if diffs:
        print("validation failed: baseline drift detected", file=sys.stderr)
        for diff in diffs[:50]:
            print(_format_diff(diff), file=sys.stderr)
        if len(diffs) > 50:
            print(f"... {len(diffs) - 50} more diffs", file=sys.stderr)
        return 1

    print("validation passed: no baseline diffs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
