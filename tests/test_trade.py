from capengine.constants import get_season
from capengine.models import Contract, HardCap
from capengine.trade import TradeSide, evaluate_trade, max_incoming_expanded
from tests.conftest import contract, team_at

K = get_season("2026-27")


def incoming(salary: int, player: str = "Incoming Player") -> Contract:
    return Contract(player=player, salary=salary)


# -- matching bands ---------------------------------------------------------------------


def test_small_band_matches_at_200_percent_plus_cushion():
    allowed, rule = max_incoming_expanded(8_000_000, K)
    assert allowed == 16_250_000
    assert "200%" in rule


def test_middle_band_adds_the_band_amount():
    allowed, rule = max_incoming_expanded(20_000_000, K)
    assert allowed == 20_000_000 + K.trade_band_lower == 29_096_000
    assert "middle band" in rule


def test_large_band_matches_at_125_percent_plus_cushion():
    allowed, rule = max_incoming_expanded(40_000_000, K)
    assert allowed == 50_250_000
    assert "125%" in rule


def test_band_boundaries_are_inclusive_at_the_lower_edge():
    at_edge, _ = max_incoming_expanded(K.trade_band_lower, K)
    assert at_edge == K.trade_band_lower * 2 + 250_000


# -- apron-driven matching --------------------------------------------------------------


def test_below_apron_team_may_take_back_more_than_it_sends():
    team = team_at(180_000_000, name="Flexible")
    team.contracts.append(contract("Outgoing", 10_000_000))
    result = evaluate_trade(
        [TradeSide(team=team, sending=["Outgoing"], receiving=[incoming(19_000_000)])]
    )
    assert result.legal
    assert result.sides[0].hard_cap_triggered is HardCap.FIRST_APRON


def test_first_apron_team_is_capped_at_100_percent():
    team = team_at(212_000_000, name="Apron Team")
    team.contracts.append(contract("Outgoing", 20_000_000))
    result = evaluate_trade(
        [TradeSide(team=team, sending=["Outgoing"], receiving=[incoming(20_500_000)])]
    )
    assert not result.legal
    assert any("salary matching" in v.rule for v in result.violations)
    assert result.sides[0].max_incoming == 20_000_000


def test_first_apron_team_may_trade_dollar_for_dollar():
    team = team_at(212_000_000, name="Apron Team")
    team.contracts.append(contract("Outgoing", 20_000_000))
    result = evaluate_trade(
        [TradeSide(team=team, sending=["Outgoing"], receiving=[incoming(20_000_000)])]
    )
    assert result.legal


# -- second-apron prohibitions -----------------------------------------------------------


def test_second_apron_team_cannot_aggregate_salaries():
    team = team_at(228_000_000, name="Second Apron Team")
    team.contracts.extend([contract("A", 12_000_000), contract("B", 10_000_000)])
    result = evaluate_trade(
        [TradeSide(team=team, sending=["A", "B"], receiving=[incoming(22_000_000)])]
    )
    assert not result.legal
    assert any("aggregation" in v.rule for v in result.violations)


def test_second_apron_team_may_still_trade_one_for_one():
    team = team_at(215_000_000, name="Second Apron Team")
    team.contracts.append(contract("A", 12_000_000))
    assert team.is_over_second_apron
    result = evaluate_trade(
        [TradeSide(team=team, sending=["A"], receiving=[incoming(12_000_000)])]
    )
    assert result.legal


def test_second_apron_team_cannot_send_cash():
    team = team_at(228_000_000, name="Second Apron Team")
    team.contracts.append(contract("A", 12_000_000))
    result = evaluate_trade(
        [TradeSide(team=team, sending=["A"], receiving=[incoming(12_000_000)], cash_sent=1)]
    )
    assert not result.legal
    assert any("cash ban" in v.rule for v in result.violations)


def test_aggregation_below_the_second_apron_triggers_a_hard_cap():
    team = team_at(190_000_000, name="Aggregator")
    team.contracts.extend([contract("A", 12_000_000), contract("B", 10_000_000)])
    result = evaluate_trade(
        [TradeSide(team=team, sending=["A", "B"], receiving=[incoming(22_000_000)])]
    )
    assert result.legal
    assert result.sides[0].hard_cap_triggered is HardCap.SECOND_APRON


# -- hard caps ---------------------------------------------------------------------------


def test_trade_that_breaches_an_existing_hard_cap_is_illegal():
    team = team_at(205_000_000, name="Hard Capped", hard_cap=HardCap.FIRST_APRON)
    team.contracts.append(contract("Outgoing", 5_000_000))
    result = evaluate_trade(
        [TradeSide(team=team, sending=["Outgoing"], receiving=[incoming(10_000_000)])]
    )
    assert not result.legal
    assert any("hard cap" in v.rule for v in result.violations)


def test_aggregating_triggers_a_second_apron_cap_that_incentives_can_breach():
    """Salary matches dollar-for-dollar, yet the trade is still illegal.

    A team between the aprons may aggregate, but doing so hard-caps it at the second apron.
    Incoming unlikely incentives count toward apron salary even though they play no part in
    salary matching -- so a deal that balances perfectly on paper can still breach the cap
    the aggregation just imposed.
    """
    team = team_at(196_000_000, name="Between Aprons")
    team.contracts.extend([contract("A", 12_000_000), contract("B", 10_000_000)])
    assert team.is_over_first_apron and not team.is_over_second_apron

    result = evaluate_trade([
        TradeSide(
            team=team,
            sending=["A", "B"],
            receiving=[Contract(player="Bonus Guy", salary=22_000_000,
                                incentives_unlikely=5_000_000)],
        )
    ])
    assert result.sides[0].hard_cap_triggered is HardCap.SECOND_APRON
    assert result.sides[0].incoming_salary == result.sides[0].max_incoming == 22_000_000
    assert not result.legal
    assert any("hard cap" in v.rule for v in result.violations)


# -- player restrictions ------------------------------------------------------------------


def test_no_trade_clause_blocks_the_deal():
    team = team_at(180_000_000)
    team.contracts.append(contract("Star", 40_000_000, no_trade_clause=True))
    result = evaluate_trade(
        [TradeSide(team=team, sending=["Star"], receiving=[incoming(40_000_000)])]
    )
    assert not result.legal
    assert any("no-trade" in v.rule for v in result.violations)


def test_recently_acquired_player_cannot_be_re_aggregated():
    team = team_at(180_000_000)
    team.contracts.extend([
        contract("A", 12_000_000, cannot_be_aggregated="acquired by trade within two months"),
        contract("B", 10_000_000),
    ])
    result = evaluate_trade(
        [TradeSide(team=team, sending=["A", "B"], receiving=[incoming(22_000_000)])]
    )
    assert not result.legal
    assert any("aggregated" in v.rule for v in result.violations)


def test_prior_year_tpe_unusable_over_the_first_apron():
    team = team_at(212_000_000)
    result = evaluate_trade([
        TradeSide(
            team=team,
            receiving=[incoming(8_000_000)],
            using_tpe=10_000_000,
            tpe_is_prior_year=True,
        )
    ])
    assert not result.legal
    assert any("prior-year TPE" in v.rule for v in result.violations)


# -- multi-team and structure ---------------------------------------------------------------


def test_three_team_trade_flags_only_the_offending_side():
    a = team_at(180_000_000, name="Team A")
    a.contracts.append(contract("A1", 20_000_000))
    b = team_at(228_000_000, name="Team B")
    b.contracts.extend([contract("B1", 12_000_000), contract("B2", 9_000_000)])
    c = team_at(150_000_000, name="Team C")
    c.contracts.append(contract("C1", 21_000_000))

    result = evaluate_trade([
        TradeSide(team=a, sending=["A1"], receiving=[incoming(21_000_000, "B1+B2 package")]),
        TradeSide(team=b, sending=["B1", "B2"], receiving=[incoming(20_000_000, "A1")]),
        TradeSide(team=c, sending=["C1"], receiving=[incoming(21_000_000, "filler")]),
    ])
    assert not result.legal
    assert {v.team for v in result.violations} == {"Team B"}


def test_roster_limit_enforced():
    team = team_at(180_000_000, roster=15)
    result = evaluate_trade([
        TradeSide(
            team=team,
            sending=["Player 1"],
            receiving=[incoming(5_000_000, "X"), incoming(5_000_000, "Y")],
        )
    ])
    assert any("roster limit" in v.rule for v in result.violations)


def test_trace_covers_the_reported_figures():
    team = team_at(180_000_000)
    team.contracts.append(contract("Outgoing", 10_000_000))
    result = evaluate_trade(
        [TradeSide(team=team, sending=["Outgoing"], receiving=[incoming(15_000_000)])]
    )
    values = result.trace.values()
    assert 10_000_000 in values
    assert 15_000_000 in values
    assert result.sides[0].max_incoming in values
    assert result.sides[0].apron_salary_after in values
