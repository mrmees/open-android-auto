from __future__ import annotations
from typing import Any

# Closed enum -- walker cites ONLY these 6 MATCH rules (per 10-CONTEXT.md locked decision).
# MATCH-04 (field-level value match) and MATCH-05 (enum value match) are EXCLUDED:
# both require field-level wire decoding, which is out of scope for automated walker runs.
ALLOWED_MATCH_RULES = ("MATCH-01", "MATCH-02", "MATCH-03", "MATCH-06", "MATCH-07", "MATCH-08")

EXCLUDED_MATCH_RULES = ("MATCH-04", "MATCH-05")

# Walker NEVER emits NOMATCH-01 (framing-layer non-claim boundary).
# See docs/verification/06-capture-non-claim-boundary.md.
FORBIDDEN_NOMATCH_RULES = ("NOMATCH-01",)


def eval_match_rules(
    channel_kind: str,
    msg_type: int,
    observations: list[tuple[int, int]],
    classification_labels: list[str],
    sdp_kinds: set[str],
) -> list[str]:
    """Return sorted list of MATCH-NN rules that fire for this sidecar.

    Never returns MATCH-04 or MATCH-05 (field decoding out of scope).
    Plan 10-02 implements the per-rule predicates.
    """
    raise NotImplementedError("Plan 10-02 implements eval_match_rules")


def eval_nomatch_rules(
    channel_kind: str,
    observed_in_sdp: bool,
    observations: list[tuple[int, int]],
    classification_labels: list[str],
) -> list[str]:
    """Return sorted list of NOMATCH-NN rules that fire. Never returns NOMATCH-01.

    Plan 10-02 implements NOMATCH-02/03/04 logic.
    """
    raise NotImplementedError("Plan 10-02 implements eval_nomatch_rules")
