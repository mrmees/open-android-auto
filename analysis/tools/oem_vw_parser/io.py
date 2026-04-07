from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Any, Iterator

from .models import UnifiedRecord
from .normalize import normalize_dhu_direction

_log = logging.getLogger(__name__)


# The only capture format the parser currently understands. session.json must
# store this as a JSON integer (NOT a string). Numeric comparison is mandatory:
# silent string-equality checks would fail on every valid capture.
CAPTURE_VERSION_NATIVE_INTERCEPTOR = 5


def load_session_json(path: Path) -> dict[str, Any]:
    """Load and validate a capture session.json.

    Raises ValueError if `capture_version` is not a Python int (e.g., a
    string label like the maintainer's prose `native_interceptor_regnatives`
    being stored verbatim) or if the integer is not the supported value.
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    cv = raw.get("capture_version")
    # Reject bools too: in Python, True is an int subclass and would slip
    # through a naive isinstance(cv, int) check.
    if not isinstance(cv, int) or isinstance(cv, bool):
        raise ValueError(
            f"capture_version must be int, got {type(cv).__name__}: {cv!r}"
        )
    if cv != CAPTURE_VERSION_NATIVE_INTERCEPTOR:
        raise ValueError(
            f"unsupported capture_version: {cv} "
            f"(parser only supports {CAPTURE_VERSION_NATIVE_INTERCEPTOR})"
        )
    return raw


def load_vw_capture(path: Path, capture_id: str) -> Iterator[UnifiedRecord]:
    """Yield UnifiedRecord for every line of a VW messages.jsonl capture.

    The on-phone hook (capture_version=5) does not see channel_id, flags, or
    service_type — those fields are None on every record.
    """
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        yield UnifiedRecord(
            capture_id=capture_id,
            seq=int(r["seq"]),
            ts_ms=int(r["ts_ms"]),
            direction=str(r["direction"]),  # already 'in'/'out'
            msg_type=int(r["msg_type"]),
            payload=base64.b64decode(r["payload_b64"]),
            payload_len=int(r["payload_len"]),
            channel_id=None,
            flags=None,
            service_type=None,
        )


def load_dhu_capture(
    path: Path,
    capture_id: str,
    channel_map_path: Path | None = None,
) -> Iterator[UnifiedRecord]:
    """Yield UnifiedRecord for every line of a DHU aa_messages.jsonl capture.

    Direction is normalized via normalize_dhu_direction (`dhu` → `in`,
    `phone` → `out`).

    Channel-map handling:
      - If `channel_map_path` is given, the loader reads it directly.
      - If `channel_map_path is None`, the loader auto-discovers
        `path.parent / "channel_map.json"`. If that file is absent the loader
        logs a WARNING and proceeds with an empty channel map — every record
        still gets `msg_type`, `direction`, and `channel_id`, but
        `service_type` becomes None.
    """
    channel_map: dict[str, Any] = {}
    if channel_map_path is None:
        candidate = Path(path).parent / "channel_map.json"
        if candidate.exists():
            channel_map = json.loads(candidate.read_text(encoding="utf-8"))
        else:
            _log.warning(
                "load_dhu_capture: no channel_map.json found adjacent to %s; "
                "service_type will be None for every record",
                path,
            )
    else:
        channel_map = json.loads(Path(channel_map_path).read_text(encoding="utf-8"))

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        cid = int(r["channel_id"])
        ch = channel_map.get(str(cid), {})
        # Prefer real seq if present; fall back to timestamp_ms so records
        # remain orderable even when DHU exports omit a seq field.
        seq_value = r.get("seq")
        if seq_value is None:
            seq_value = r.get("timestamp_ms", 0)
        yield UnifiedRecord(
            capture_id=capture_id,
            seq=int(seq_value),
            ts_ms=int(r.get("timestamp_ms", 0)),
            direction=normalize_dhu_direction(r["direction"]),
            msg_type=int(r["msg_type"]),
            payload=bytes.fromhex(r["payload_hex"]),
            payload_len=int(r.get("payload_len", 0)),
            channel_id=cid,
            flags=int(r.get("flags", 0)),
            service_type=ch.get("service_type"),
        )
