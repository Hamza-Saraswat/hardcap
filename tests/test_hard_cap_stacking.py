from capengine.models import Contract, HardCap
from capengine.trade import TradeSide, evaluate_trade
from tests.conftest import contract, team_with


def test_two_triggers_means_the_tighter_cap_governs():
    """Taking back over 100% AND aggregating fires both caps -- the first apron wins.

    Caught by a smoke test over generated scenarios: the engine used to let whichever
    trigger fired last set the cap, so a trade that breached the first apron read as legal
    because the second-apron cap had overwritten it.
    """
    team = team_with(
        202_000_000,
        [contract("A", 8_000_000), contract("B", 6_000_000)],
        name="Aggregator",
    )
    k = team.constants
    assert not team.is_over_first_apron

    result = evaluate_trade([
        TradeSide(
            team=team,
            sending=["A", "B"],
            receiving=[Contract(player="Big Return", salary=23_000_000)],
        )
    ])

    assert result.sides[0].hard_cap_triggered is HardCap.FIRST_APRON
    assert result.sides[0].apron_salary_after > k.first_apron
    assert not result.legal
    assert any("hard cap" in v.rule for v in result.violations)


def test_a_single_aggregation_trigger_still_caps_at_the_second_apron():
    team = team_with(
        195_000_000,
        [contract("A", 8_000_000), contract("B", 6_000_000)],
        name="Even Swap",
    )
    result = evaluate_trade([
        TradeSide(
            team=team,
            sending=["A", "B"],
            receiving=[Contract(player="Return", salary=14_000_000)],
        )
    ])
    assert result.sides[0].hard_cap_triggered is HardCap.SECOND_APRON
    assert result.legal
