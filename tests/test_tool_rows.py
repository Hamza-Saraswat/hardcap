"""Tests for tool-calling training rows.

The bug these exist to prevent was invisible: passing `arguments` as a JSON string (the
OpenAI convention) let Qwen's chat template render `<function=calc>` with no parameters
inside. It produced no error anywhere -- the rows just silently taught the model to emit
calls that carry no expression. Only reading the rendered text caught it.
"""

import random

import pytest

from capengine.calc import calc
from datagen.narrate_v2 import narrate_v2, tool_messages
from datagen.scenarios_v2 import V2_SAMPLERS


def tool_scenario(kind: str, seed: int = 5):
    return V2_SAMPLERS[kind](random.Random(seed))


@pytest.mark.parametrize("kind", ["tool_tax_bill", "tool_matching"])
def test_arguments_are_a_dict_not_a_json_string(kind):
    """Qwen's template iterates the argument mapping; a string renders no parameters."""
    messages = tool_messages(tool_scenario(kind))
    calls = [m for m in messages if m.get("tool_calls")]
    assert calls, "tool scenario produced no calls"
    for message in calls:
        arguments = message["tool_calls"][0]["function"]["arguments"]
        assert isinstance(arguments, dict), f"arguments must be a dict, got {type(arguments)}"
        assert "expression" in arguments


@pytest.mark.parametrize("kind", ["tool_tax_bill", "tool_matching"])
def test_every_call_is_paired_with_its_result(kind):
    messages = tool_messages(tool_scenario(kind))
    roles = [m["role"] for m in messages]
    assert roles == ["assistant", "tool"] * (len(messages) // 2)


@pytest.mark.parametrize("kind", ["tool_tax_bill", "tool_matching"])
def test_recorded_results_match_the_calculator(kind):
    """A stale or hand-typed result would train the model to trust a wrong tool."""
    scenario = tool_scenario(kind)
    for turn in scenario.tool_turns:
        assert calc(turn["expression"]).rendered == turn["result"]


def test_tax_bracket_calls_sum_to_the_engine_total():
    """The point of the slice: the tool's arithmetic reproduces CapEngine exactly."""
    scenario = tool_scenario("tool_tax_bill", seed=11)
    facts = scenario.answer_facts
    per_bracket = [b["owed"] for b in facts["brackets"]]
    assert sum(per_bracket) == facts["total"]
    # And the final call, when there is one, is that same sum.
    if len(per_bracket) > 1:
        final = scenario.tool_turns[-1]
        assert round(calc(final["expression"]).value) == facts["total"]


@pytest.mark.parametrize("kind", sorted(V2_SAMPLERS))
def test_every_v2_slice_narrates_without_crashing(kind):
    rng = random.Random(3)
    scenario = V2_SAMPLERS[kind](rng)
    text = narrate_v2(scenario, rng)
    assert len(text) > 120, f"{kind} narration is too thin"


def test_no_sheet_slices_carry_no_cap_sheet():
    """These exist precisely to train the empty-context case."""
    for kind in ("no_sheet_enumeration", "missing_data_request"):
        scenario = V2_SAMPLERS[kind](random.Random(1))
        assert scenario.context == ""


def test_missing_data_answer_asks_rather_than_guesses():
    rng = random.Random(2)
    scenario = V2_SAMPLERS["missing_data_request"](rng)
    text = narrate_v2(scenario, rng).lower()
    assert any(word in text for word in ("send me", "i need", "paste"))
