"""Verifier tests.

The verifier is the load-bearing piece of the data pipeline: if it lets an invented figure
through, that figure becomes training data and the model learns to state it confidently.
These tests pin down both directions -- it must catch fabrications, and it must not reject
correct answers for spurious reasons.
"""

import random

import pytest

from datagen.scenarios import SAMPLERS, sample
from datagen.verify import dollar_figures, verify


@pytest.fixture
def scenario():
    return SAMPLERS["trade_legality"](random.Random(3))


def opening(scenario, flip: bool = False) -> str:
    """A verdict line matching the scenario -- or deliberately contradicting it."""
    correct = scenario.verdict == "LEGAL"
    says_legal = not correct if flip else correct
    return f"**Verdict: {'LEGAL' if says_legal else 'ILLEGAL'}.**"


def test_extracts_comma_formatted_dollar_amounts():
    text = "They send out $14,827,471 and take back $26,055,742."
    assert dollar_figures(text) == [14_827_471, 26_055_742]


def test_ignores_years_and_bare_counts():
    """A season label is not a dollar amount."""
    assert dollar_figures("Under the 2026-27 rules, 15 players, 3 of 5 seasons.") == []


def test_ignores_per_dollar_tax_rates():
    """'$1.00 per dollar' is a rate; treating it as a claim would reject valid answers."""
    assert dollar_figures("taxed at $1.25 per dollar") == []


def test_accepts_an_answer_built_only_from_traced_figures(scenario):
    allowed = sorted(scenario.allowed_values())
    body = " ".join(f"${v:,}" for v in scenario.required_values)
    response = (
        f"{opening(scenario)} Here is the matching math in full: {body}. "
        f"That is the whole story, and it comes straight off the sheet above. "
        f"Nothing else on this roster changes it. Reference: ${allowed[0]:,}."
    )
    result = verify(scenario, response)
    assert result.ok, result.problems()


def test_rejects_an_invented_figure(scenario):
    body = " ".join(f"${v:,}" for v in scenario.required_values)
    response = (
        f"{opening(scenario)} {body}, which leaves them $99,123,456 from the line "
        "and changes the picture under any reading of the rules in force today."
    )
    result = verify(scenario, response)
    assert not result.ok
    assert 99_123_456 in result.unknown_values
    assert "never computed" in result.problems()


def test_rejects_a_missing_required_figure(scenario):
    response = (
        f"{opening(scenario)} The salary question turns on the applicable band here, so the "
        "trade reads the way it does and the front office should plan around that."
    )
    result = verify(scenario, response)
    assert not result.ok
    assert result.missing_required


def test_rejects_rounded_amounts(scenario):
    body = " ".join(f"${v:,}" for v in scenario.required_values)
    response = (
        f"{opening(scenario)} {body} -- call it about $26.1 million coming back, which is "
        "the figure that governs under the matching rules in force this league year."
    )
    result = verify(scenario, response)
    assert not result.ok
    assert result.approximations


def test_rejects_a_flipped_verdict(scenario):
    body = " ".join(f"${v:,}" for v in scenario.required_values)
    response = (
        f"{opening(scenario, flip=True)} Reading it the other way: {body}. That is the "
        "opposite of what the rules actually produce on this particular cap sheet today."
    )
    result = verify(scenario, response)
    assert not result.verdict_ok


def test_rejects_an_answer_too_short_to_show_work(scenario):
    body = " ".join(f"${v:,}" for v in scenario.required_values)
    assert not verify(scenario, f"{opening(scenario)} {body}").ok


def test_context_figures_are_allowed_even_when_untraced(scenario):
    """A model may quote a salary off the pasted cap sheet the engine never used."""
    from datagen.scenarios import _numbers_in

    context_only = _numbers_in(scenario.context) - scenario.trace.values()
    assert context_only, "the fixture should have unused cap sheet figures"
    assert context_only <= scenario.allowed_values()


@pytest.mark.parametrize("seed", range(25))
def test_every_scenario_type_produces_a_usable_whitelist(seed):
    """Required figures must always be inside the allowed set, or nothing could pass."""
    scenario = sample(random.Random(seed))
    allowed = scenario.allowed_values()
    for value in scenario.required_values:
        assert value in allowed, f"{scenario.kind}: required ${value:,} is not allowed"
