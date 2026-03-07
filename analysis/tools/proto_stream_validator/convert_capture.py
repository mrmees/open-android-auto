#!/usr/bin/env python3
"""Convert raw DHU capture JSONL to proto_stream_validator input format."""

import json
import sys
from pathlib import Path

DIRECTION_MAP = {"dhu": "HU->Phone", "phone": "Phone->HU"}


def convert_line(raw: dict, channel_map: dict[str, dict] | None) -> dict:
    payload_hex = raw["payload_hex"]
    # Raw captures embed the 2-byte BE message ID as a prefix in payload_hex.
    # Strip it — the message_id is already in a separate JSON field.
    if len(payload_hex) >= 4:
        payload_hex = payload_hex[4:]

    channel_id = raw["channel_id"]
    service_type = ""
    if channel_map and str(channel_id) in channel_map:
        service_type = channel_map[str(channel_id)].get("service_type", "")

    return {
        "ts_ms": raw.get("timestamp_ms", 0),
        "direction": DIRECTION_MAP.get(raw.get("direction", ""), raw.get("direction", "")),
        "channel_id": channel_id,
        "message_id": raw["msg_type"],
        "message_name": "",
        "payload_hex": payload_hex,
        "service_type": service_type,
    }


def main():
    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} <input.jsonl> <output.jsonl> [--channel-map <map.json>]",
            file=sys.stderr,
        )
        sys.exit(1)

    input_path, output_path = Path(sys.argv[1]), Path(sys.argv[2])

    channel_map = None
    if "--channel-map" in sys.argv:
        idx = sys.argv.index("--channel-map")
        if idx + 1 < len(sys.argv):
            channel_map = json.loads(Path(sys.argv[idx + 1]).read_text())

    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(input_path) as fin, open(output_path, "w") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            fout.write(json.dumps(convert_line(raw, channel_map)) + "\n")
            count += 1

    print(f"Converted {count} frames: {input_path} -> {output_path}")


if __name__ == "__main__":
    main()
