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
    msg_type: int | None,
    observations: list[tuple[int, int]],
    classification_labels: list[str],
    sdp_kinds: set[str],
) -> list[str]:
    """Return sorted list of MATCH-NN rules that fire for this sidecar.

    HARD-CODED EXCLUSION: MATCH-04 and MATCH-05 are NEVER returned regardless of input.
    """
    rules: set[str] = set()

    if channel_kind in sdp_kinds:
        rules.add("MATCH-08")

    # MATCH-01: any observation (non-garbage) exists
    non_garbage_labels = [
        lbl for lbl in classification_labels
        if lbl not in ("continuation_or_garbage", "unattributed")
    ]
    if non_garbage_labels:
        rules.add("MATCH-01")

    # MATCH-02: at least one standalone observation
    if "standalone" in non_garbage_labels:
        rules.add("MATCH-02")

    # MATCH-03: at least one reassembled observation (zero usage in v1.5 live data)
    if "reassembled" in non_garbage_labels:
        rules.add("MATCH-03")

    # MATCH-06: repeat observation (>= 2 non-garbage)
    if len(observations) >= 2 and len(non_garbage_labels) >= 2:
        rules.add("MATCH-06")

    # MATCH-07: cross-direction (walker tracks directions via the classification_labels
    # list's ordering convention; left for future refinement. Currently not emitted.)

    # Defensive assertion: MATCH-04 and MATCH-05 MUST NEVER appear
    assert not (set(EXCLUDED_MATCH_RULES) & rules), \
        f"walker tried to cite {rules & set(EXCLUDED_MATCH_RULES)} -- these are excluded"

    return sorted(rules)


def eval_nomatch_rules(
    channel_kind: str,
    observed_in_sdp: bool,
    observations: list[tuple[int, int]],
    classification_labels: list[str],
) -> list[str]:
    """Return sorted NOMATCH rules. NEVER returns NOMATCH-01 (non-claim boundary)."""
    rules: set[str] = set()

    # NOMATCH-02: observed in SDP but no message-level observations
    if observed_in_sdp and not observations:
        rules.add("NOMATCH-02")

    # NOMATCH-04: only fragment-only observations
    if observations and all(
        lbl in ("continuation_or_garbage", "unattributed")
        for lbl in classification_labels
    ):
        rules.add("NOMATCH-04")

    # NOMATCH-03: ambiguous attribution (deferred; not emitted by walker in v1.5)

    # Defensive assertion: NOMATCH-01 MUST NEVER appear
    assert not (set(FORBIDDEN_NOMATCH_RULES) & rules), \
        f"walker tried to cite {rules & set(FORBIDDEN_NOMATCH_RULES)} -- NOMATCH-01 is a non-claim boundary, not a walker citation"

    return sorted(rules)
