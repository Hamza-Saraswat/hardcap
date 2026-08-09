"""Tests for the calculator tool.

Two jobs: get arithmetic exactly right, and refuse everything that is not arithmetic. The
second matters more than it looks -- these expressions arrive from a language model today
and, once the playground is public, from strangers.
"""

import pytest

from capengine.calc import CalcError, calc, run_tool


def test_basic_arithmetic():
    assert calc("6064000 * 1.25").value == 7_580_000
    assert calc("59033114 + 50105628").value == 109_138_742
    assert calc("221686000 - 223720249").value == -2_034_249


def test_accepts_money_formatting_the_model_will_produce():
    assert calc("$59,033,114 + $50,105,628").value == 109_138_742


def test_parentheses_and_chained_terms():
    """The multi-bracket tax sum in one call -- the shape that scored 4.7% without tools.

    Written first with a hand-computed expectation that was itself wrong, which is the
    whole argument for the tool: 6,064,000 + 7,580,000 + 7,480,753.50.
    """
    assert calc("(6064000 * 1.00) + (6064000 * 1.25) + (1360137 * 5.50)").value == 21_124_753.5


def test_whole_dollar_results_stay_integers():
    result = calc("6064000 * 1.25")
    assert isinstance(result.value, int)
    assert result.rendered == "7,580,000"


def test_genuine_fractions_survive():
    assert calc("10 / 3").rendered.startswith("3.33")


def test_rejects_names_and_calls():
    with pytest.raises(CalcError):
        calc("__import__('os').system('ls')")
    with pytest.raises(CalcError):
        calc("open('/etc/passwd').read()")
    with pytest.raises(CalcError):
        calc("cap * 2")


def test_rejects_dunder_and_attribute_access():
    with pytest.raises(CalcError):
        calc("(1).__class__")


def test_rejects_power_operator_as_a_cheap_dos():
    """9**9**9 would hang the process; only + - * / are permitted."""
    with pytest.raises(CalcError):
        calc("9**9**9")


def test_rejects_oversized_and_empty_input():
    with pytest.raises(CalcError):
        calc("1+" * 200 + "1")
    with pytest.raises(CalcError):
        calc("   ")


def test_division_by_zero_is_reported_not_raised_as_crash():
    with pytest.raises(CalcError, match="division by zero"):
        calc("5 / 0")


def test_run_tool_returns_errors_as_text_for_the_model_to_read():
    """A tool error must come back as a message, not an exception that kills the turn."""
    assert run_tool({"expression": "5 / 0"}).startswith("error:")
    assert run_tool({"expression": "6064000 * 2"}) == "12,128,000"
    assert run_tool({}).startswith("error:")
