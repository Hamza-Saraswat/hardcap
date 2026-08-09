"""Tests for the GRPO reward.

A reward function that is quietly backwards trains the model to be worse, and the loss
curve looks fine the whole time. These pin the ordering that matters -- a correct answer
must outscore every degenerate one -- and check the specific hacks the shape invites.
"""

import pytest

from training.train_grpo import loop_penalty, score_completion

ROW = {
    "verdict": "ILLEGAL",
    "required_values": [14_827_471, 23_923_471],
    "allowed_values": [14_827_471, 23_923_471, 209_015_000, 2_132_271],
}

GOOD = (
    "**Verdict: ILLEGAL.** We send out $14,827,471 and may absorb $23,923,471 under the "
    "middle band, so the incoming salary is over the limit and the trade cannot be "
    "processed as constructed. Restructure it or find a third team."
)


def test_a_correct_answer_scores_full_marks():
    total, parts = score_completion(GOOD, ROW)
    assert total == pytest.approx(1.0)
    assert parts["verdict"] == 1.0
    assert parts["grounded"] == 1.0


def test_correct_answer_outscores_every_degenerate_one():
    good, _ = score_completion(GOOD, ROW)
    for bad in ("", "the second apron is the line " * 20, "Illegal.",
                "**Verdict: LEGAL.** $14,827,471 and $23,923,471 both check out here fine."):
        worse, _ = score_completion(bad, ROW)
        assert worse < good, f"{bad[:30]!r} scored {worse} against {good}"


def test_flipped_verdict_loses_the_verdict_term_but_keeps_the_rest():
    flipped = GOOD.replace("ILLEGAL", "LEGAL")
    total, parts = score_completion(flipped, ROW)
    assert parts["verdict"] == 0.0
    assert parts["required"] == 1.0
    assert 0 < total < 1.0


def test_inventing_a_figure_costs_grounding():
    invented = GOOD.replace("$23,923,471", "$99,999,999")
    total, parts = score_completion(invented, ROW)
    assert parts["grounded"] < 1.0
    assert total < score_completion(GOOD, ROW)[0]


def test_saying_nothing_is_not_the_safest_play():
    """Reward only 'no invented figures' and silence wins. It must not."""
    silent = (
        "**Verdict: ILLEGAL.** The trade does not work under the applicable band, so it "
        "cannot be processed as constructed and the front office needs another framework."
    )
    silent_score, parts = score_completion(silent, ROW)
    assert parts["grounded"] == 0.5, "naming no figures should not earn full grounding"
    assert silent_score < score_completion(GOOD, ROW)[0]


def test_a_loop_scores_zero_outright():
    looping = GOOD + " " + "the pick goes to the end of the round " * 12
    total, parts = score_completion(looping, ROW)
    assert parts["loop"] == 1.0
    assert total == 0.0


def test_loop_detector_ignores_ordinary_repetition():
    normal = (
        "The second apron matters here. Over the second apron we lose aggregation. "
        "That is what the second apron does."
    )
    assert loop_penalty(normal) == 0.0


def test_missing_the_verdict_line_costs_form_not_correctness():
    no_marker = GOOD.replace("**Verdict: ILLEGAL.** ", "This one is illegal. ")
    total, parts = score_completion(no_marker, ROW)
    assert parts["verdict"] == 1.0
    assert parts["form"] < 1.0
    assert total < 1.0


def test_rows_without_a_verdict_are_not_penalized_for_lacking_one():
    row = {"required_values": [5_000_000], "allowed_values": [5_000_000]}
    text = "We have $5,000,000 of room below the line, which is the number that matters here."
    _, parts = score_completion(text, row)
    assert parts["verdict"] == 1.0
