from __future__ import annotations

from analysis.tools.promotion_walker.rule_eval import (
    eval_match_rules, eval_nomatch_rules,
    ALLOWED_MATCH_RULES, EXCLUDED_MATCH_RULES, FORBIDDEN_NOMATCH_RULES,
)


def test_match_08_baseline() -> None:
    """MATCH-08 fires when channel_kind is in sdp_kinds with zero wire observations."""
    rules = eval_match_rules("av_channel", None, [], [], {"av_channel"})
    assert "MATCH-08" in rules
    # No wire observations so MATCH-01/02/03/06/07 do not fire
    assert "MATCH-01" not in rules
    assert "MATCH-02" not in rules


def test_match_04_excluded() -> None:
    """MATCH-04 is NEVER cited -- walker doesn't do field-level decoding."""
    # No input can cause MATCH-04 to appear
    rules = eval_match_rules("av_channel", 32771, [(1, 5), (2, 10), (3, 15)],
                             ["standalone", "standalone", "reassembled"],
                             {"av_channel"})
    assert "MATCH-04" not in rules
    assert "MATCH-04" not in ALLOWED_MATCH_RULES
    assert "MATCH-04" in EXCLUDED_MATCH_RULES


def test_match_05_excluded() -> None:
    """MATCH-05 (enum value match) is NEVER cited -- special case of MATCH-04."""
    rules = eval_match_rules("av_channel", 32771, [(1, 5)], ["standalone"], {"av_channel"})
    assert "MATCH-05" not in rules
    assert "MATCH-05" not in ALLOWED_MATCH_RULES
    assert "MATCH-05" in EXCLUDED_MATCH_RULES


def test_nomatch_01_never_emitted() -> None:
    """NOMATCH-01 (non-claim boundary) is NEVER cited as evidence."""
    # No input can cause NOMATCH-01 to appear
    rules = eval_nomatch_rules("av_channel", True, [], [])
    assert "NOMATCH-01" not in rules
    rules2 = eval_nomatch_rules("av_channel", False, [], [])
    assert "NOMATCH-01" not in rules2
    assert "NOMATCH-01" in FORBIDDEN_NOMATCH_RULES


def test_allowed_match_rules_is_6_rules() -> None:
    """ALLOWED_MATCH_RULES contains exactly MATCH-01, 02, 03, 06, 07, 08 -- no 04 or 05."""
    assert set(ALLOWED_MATCH_RULES) == {"MATCH-01", "MATCH-02", "MATCH-03", "MATCH-06", "MATCH-07", "MATCH-08"}


def test_match_06_fires_on_repeat() -> None:
    """MATCH-06 fires when >= 2 non-garbage observations exist."""
    rules = eval_match_rules("av_channel", 32771,
                             [(1, 5), (2, 10)],
                             ["standalone", "standalone"],
                             {"av_channel"})
    assert "MATCH-06" in rules


def test_nomatch_02_fires_when_observed_in_sdp_but_no_wire() -> None:
    """NOMATCH-02: in SDP but no observations."""
    rules = eval_nomatch_rules("av_channel", True, [], [])
    assert "NOMATCH-02" in rules


def test_nomatch_04_fires_on_garbage_only() -> None:
    """NOMATCH-04: only fragment/garbage observations (rejected as evidence)."""
    rules = eval_nomatch_rules("av_channel", True,
                               [(1, 5)], ["continuation_or_garbage"])
    assert "NOMATCH-04" in rules
