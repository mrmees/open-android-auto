#!/usr/bin/env python3
"""Convert raw DHU capture JSONL to proto_stream_validator input format."""

import json
import sys
from pathlib import Path

DIRECTION_MAP = {"dhu": "HU->Phone", "phone": "Phone->HU"}


def convert_line(raw: dict) -> dict:
    return {
        "ts_ms": raw.get("timestamp_ms", 0),
        "direction": DIRECTION_MAP.get(raw.get("direction", ""), raw.get("direction", "")),
        "channel_id": raw["channel_id"],
        "message_id": raw["msg_type"],
        "message_name": "",
        "payload_hex": raw["payload_hex"],
    }


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.jsonl> <output.jsonl>", file=sys.stderr)
        sys.exit(1)

    input_path, output_path = Path(sys.argv[1]), Path(sys.argv[2])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(input_path) as fin, open(output_path, "w") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            fout.write(json.dumps(convert_line(raw)) + "\n")

    print(f"Converted {input_path} -> {output_path}")


if __name__ == "__main__":
    main()
