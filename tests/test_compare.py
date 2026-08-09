"""Tests for the run comparison and its gates.

This code decides whether a checkpoint ships. A gate that silently passes everything is
worse than no gate, so the tests check both directions and the one metric whose polarity is
inverted: loops are a maximum, not a minimum.
"""

import pytest

from eval.compare import GATES, looped, metrics


def row(**kwargs) -> dict:
    base = {
        "kind": "trade_legality",
        "verdict_correct": True,
        "required_hit": 2,
        "required_total": 2,
        "invented": [],
        "response": "A perfectly ordinary answer that states its reasoning at some length.",
    }
    base.update(kwargs)
    return base


def test_perfect_run_scores_everything_at_one():
    m = metrics([row(), row()])
    assert m["verdict"] == 1.0
    assert m["arithmetic"] == 1.0
    assert m["grounding"] == 1.0
    assert m["loops"] == 0.0


def test_missing_a_required_figure_costs_arithmetic_only():
    m = metrics([row(required_hit=1, required_total=2)])
    assert m["arithmetic"] == 0.0
    assert m["verdict"] == 1.0
    assert m["grounding"] == 1.0


def test_rows_with_no_required_figures_count_as_arithmetically_fine():
    """Otherwise concept questions would drag the arithmetic score down for no reason."""
    m = metrics([row(required_hit=0, required_total=0)])
    assert m["arithmetic"] == 1.0


def test_invented_figures_cost_grounding():
    m = metrics([row(invented=[99_999_999]), row()])
    assert m["grounding"] == 0.5


def test_staleness_is_measured_only_on_staleness_probes():
    rows = [
        row(kind="anti_staleness", invented=[123456]),
        row(kind="trade_legality", invented=[]),
    ]
    m = metrics(rows)
    assert m["staleness"] == 0.0
    assert m["grounding"] == 0.5


def test_verdict_ignores_rows_that_have_no_verdict():
    m = metrics([row(verdict_correct=None), row(verdict_correct=True)])
    assert m["verdict"] == 1.0


def test_loop_detection_flags_repetition_and_spares_normal_prose():
    looping = "the pick goes to the end of the round " * 10
    normal = (
        "We are over the second apron. Over the second apron we lose aggregation, and the "
        "second apron also bars sending cash in any trade."
    )
    assert looped(looping)
    assert not looped(normal)
    assert metrics([row(response=looping)])["loops"] == 1.0


def test_short_answers_are_not_mistaken_for_loops():
    assert not looped("Illegal. The salary does not match.")


def test_gate_thresholds_are_the_v2_targets():
    assert GATES["verdict"] == 0.90
    assert GATES["arithmetic"] == 0.90
    assert GATES["grounding"] == 0.70
    assert GATES["staleness"] == 0.70
    assert GATES["loops"] == 0.0


@pytest.mark.parametrize(
    "name,value,should_pass",
    [
        ("verdict", 0.91, True),
        ("verdict", 0.89, False),
        ("grounding", 0.70, True),
        ("loops", 0.0, True),
        ("loops", 0.01, False),  # inverted: a maximum, not a minimum
    ],
)
def test_gate_comparison_direction(name, value, should_pass):
    target = GATES[name]
    ok = value <= target if name == "loops" else value >= target
    assert ok is should_pass
