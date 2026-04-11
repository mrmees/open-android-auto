from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class VerdictKind(str, Enum):
    """Possible walker verdicts for a single sidecar."""
    PROMOTE_TO_PLATINUM = "promote_to_platinum"
    FLAG_PENDING_GOLD = "flag_pending_gold"
    NOMATCH_OBSERVATION = "nomatch_observation"
    CONTRADICTION_REVIEW = "contradiction_review"
    SKIP_RETRACTED = "skip_retracted"
    SKIP_SUPERSEDED = "skip_superseded"
    SKIP_ALREADY_PLATINUM = "skip_already_platinum"
    SKIP_SCHEMA_INVALID = "skip_schema_invalid"
    SKIP_MISSING_GOLD_PREREQ = "skip_missing_gold_prereq"
    SKIP_OUT_OF_SDP_SCOPE = "skip_out_of_sdp_scope"


@dataclass(frozen=True)
class Verdict:
    """A single-sidecar walker decision. Frozen so it's hashable and log-friendly."""
    sidecar_path: str
    proto_message: str
    current_tier: str
    kind: VerdictKind
    matched_rules: tuple[str, ...] = ()
    nomatch_rules: tuple[str, ...] = ()
    msg_seq: tuple[int, ...] = ()
    ts_ms: tuple[int, ...] = ()
    message_completeness: str | None = None
    skip_reason: str | None = None
    contradiction_summary: str | None = None


def walker_decide(
    sidecar: dict[str, Any],
    sidecar_path: Path,
    index: dict[tuple[str, int, str], list[tuple[int, int]]],
    sdp_kinds: set[str],
    classification: dict[tuple[int, str], str],
) -> Verdict:
    """Pure function -- decide one sidecar's verdict. No I/O side effects.

    See 10-RESEARCH.md section Example 2 for the full routing logic Plan 10-02 implements.
    """
    raise NotImplementedError("Plan 10-02 implements walker_decide")
