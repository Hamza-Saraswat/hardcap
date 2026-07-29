"""Golden tests: CapEngine reproducing real transactions.

Synthetic scenarios prove the code is self-consistent. These prove it matches what actually
happened in the league, which is a much stronger claim. Figures are the publicly reported
ones and are approximate where reporting was approximate, so a few assertions use tolerances
rather than exact equality -- the point is that the engine lands on the reported answer, not
that press accounts were penny-precise.
"""

from capengine.constants import get_season
from capengine.models import Contract, HardCap, Team
from capengine.signings import ExceptionType, available_exceptions, compute_stretch
from capengine.tax import compute_tax
from capengine.trade import TradeSide, evaluate_trade
from tests.conftest import contract, team_at, team_with


def test_beal_waive_and_stretch_reproduces_the_reported_giveback():
    """Phoenix, July 2025 -- the marquee validation of the stretch rules.

    Bradley Beal had roughly $110.8M left over two years. Phoenix already carried about
    $3.8M in stretched dead money for Little and Liddell, so stretching Beal in full would
    have blown through the 15%-of-cap ceiling. Reporting at the time said he gave back
    $13.8-13.9M to make the waiver legal, leaving about $19.4M per year in dead cap through
    2029-30. The engine should land on those same numbers from the rules alone.
    """
    suns = Team(name="Suns", season="2025-26")
    result = compute_stretch(
        suns,
        remaining_salary=110_800_000,
        years_remaining=2,
        existing_stretched_dead_money=3_800_000,
    )

    assert result.stretch_years == 5, "2 years remaining stretches over 2 x 2 + 1"
    assert not result.legal, "the full amount breaches the ceiling"

    # 15% of the 2025-26 cap.
    assert result.limit == 23_197_050

    # Reported giveback was $13.8-13.9M.
    assert 13_700_000 < result.givebacks_required < 14_000_000

    # After the giveback, the annual dead money should land near the reported $19.4M.
    after = compute_stretch(
        suns,
        remaining_salary=110_800_000 - result.givebacks_required,
        years_remaining=2,
        existing_stretched_dead_money=3_800_000,
    )
    assert after.legal
    assert 19_200_000 < after.annual_dead_money < 19_600_000


def test_a_stretch_with_no_prior_dead_money_would_have_been_legal():
    """Isolating why Beal's stretch failed: the pre-existing dead money, not the size."""
    suns = Team(name="Suns", season="2025-26")
    clean = compute_stretch(suns, remaining_salary=110_800_000, years_remaining=2)
    assert clean.legal
    assert clean.annual_dead_money == 22_160_000


def test_cavaliers_2025_26_were_the_only_second_apron_team():
    """Cleveland finished 2025-26 over the second apron at roughly $211.7M."""
    cavs = team_at(211_700_000, name="Cavaliers", season="2025-26")
    k = get_season("2025-26")

    assert cavs.is_over_second_apron
    assert cavs.apron_salary - k.second_apron == 3_876_000

    # Which is why their 2033 first-rounder froze.
    from capengine.signings import draft_penalties

    penalty = draft_penalties(cavs, current_draft_year=2026)
    assert penalty.pick_frozen
    assert penalty.frozen_draft_year == 2033


def test_knicks_stayed_deliberately_just_under_the_second_apron():
    """New York sat about $370K below the second apron in 2025-26 -- by design.

    The margin is what matters: still a heavy taxpayer, but with aggregation, cash, and the
    taxpayer mid-level all preserved.
    """
    k = get_season("2025-26")
    knicks = team_at(k.second_apron - 370_000, name="Knicks", season="2025-26")

    assert not knicks.is_over_second_apron
    assert knicks.is_over_first_apron

    # The taxpayer mid-level survives; it would not have one dollar higher.
    tmle = next(
        s for s in available_exceptions(knicks) if s.exception is ExceptionType.TAXPAYER_MLE
    )
    assert tmle.available

    over = team_at(k.second_apron + 1, name="Knicks (hypothetical)", season="2025-26")
    tmle_over = next(
        s for s in available_exceptions(over) if s.exception is ExceptionType.TAXPAYER_MLE
    )
    assert not tmle_over.available

    # And they still owed a substantial tax bill.
    assert compute_tax(knicks).total > 40_000_000


def test_celtics_dropped_below_the_second_apron_via_the_porzingis_trade():
    """Boston, June 2025: the trade that moved them roughly $4.5M under the second apron."""
    k = get_season("2025-26")
    celtics = team_with(
        k.second_apron + 18_000_000,
        [contract("Kristaps Porzingis", 30_700_000)],
        name="Celtics",
        season="2025-26",
        is_repeater=True,
    )

    before = celtics.apron_salary
    assert celtics.is_over_second_apron

    # A one-for-one salary dump into a third team's cap room: legal even over the apron,
    # because nothing is aggregated and no cash changes hands.
    result = evaluate_trade([
        TradeSide(
            team=celtics,
            sending=["Kristaps Porzingis"],
            receiving=[Contract(player="Georges Niang", salary=8_200_000)],
        )
    ])
    assert result.legal

    after = result.sides[0].apron_salary_after
    assert after == before - 30_700_000 + 8_200_000
    assert after < k.second_apron
    assert k.second_apron - after == 4_500_000


def test_repeater_status_is_what_made_boston_bill_catastrophic():
    """Same salary, repeater or not -- the 2025-26 schedule roughly triples the first bracket."""
    k = get_season("2025-26")
    salary = k.tax_line + 30_000_000
    standard = compute_tax(team_at(salary, season="2025-26"))
    repeater = compute_tax(team_at(salary, season="2025-26", is_repeater=True))

    assert repeater.total > standard.total
    assert repeater.brackets[0].rate == 3.00
    assert standard.brackets[0].rate == 1.00


def test_suns_sending_cash_hard_capped_them_at_the_second_apron():
    """Phoenix, July 2026. Sending any cash at all triggers the cap."""
    suns = team_at(190_000_000, name="Suns")
    suns.contracts.append(contract("Rotation Piece", 8_000_000))

    result = evaluate_trade([
        TradeSide(
            team=suns,
            sending=["Rotation Piece"],
            receiving=[Contract(player="Return", salary=8_000_000)],
            cash_sent=1_000_000,
        )
    ])
    assert result.legal
    assert result.sides[0].hard_cap_triggered is HardCap.SECOND_APRON


def test_timberwolves_aggregating_randle_and_reid_hard_capped_them():
    """Minnesota, July 2026: two salaries combined in one trade caps them at the second apron."""
    wolves = team_with(
        210_000_000,
        [contract("Julius Randle", 32_000_000), contract("Naz Reid", 15_000_000)],
        name="Timberwolves",
    )
    assert wolves.is_over_first_apron and not wolves.is_over_second_apron

    result = evaluate_trade([
        TradeSide(
            team=wolves,
            sending=["Julius Randle", "Naz Reid"],
            receiving=[Contract(player="LaMelo Ball", salary=47_000_000)],
        )
    ])
    assert result.legal
    assert result.sides[0].aggregating
    assert result.sides[0].hard_cap_triggered is HardCap.SECOND_APRON


def test_celtics_mid_level_on_mitchell_robinson_hard_capped_at_the_first_apron():
    """Boston, July 2026: 3yr/$47.4M via the non-taxpayer mid-level, first-year salary."""
    from capengine.signings import evaluate_signing

    celtics = team_at(180_000_000, name="Celtics")
    result = evaluate_signing(celtics, 15_000_000, ExceptionType.NON_TAXPAYER_MLE,
                              player="Mitchell Robinson")
    assert result.legal
    assert result.hard_cap_triggered is HardCap.FIRST_APRON
    assert result.salary <= get_season("2026-27").non_taxpayer_mle


def test_denver_matching_an_offer_sheet_pushed_them_barely_over():
    """Denver, July 2026: about $1.9M over the second apron after matching Spencer Jones."""
    k = get_season("2026-27")
    nuggets = team_at(k.second_apron - 4_100_000, name="Nuggets", is_repeater=True)
    assert not nuggets.is_over_second_apron

    nuggets.contracts.append(contract("Spencer Jones", 6_000_000))
    assert nuggets.is_over_second_apron
    assert nuggets.apron_salary - k.second_apron == 1_900_000

    # Over the second apron, the aggregation ban now applies to any cleanup trade.
    nuggets.contracts.append(contract("Salary Filler", 5_000_000))
    result = evaluate_trade([
        TradeSide(
            team=nuggets,
            sending=["Spencer Jones", "Salary Filler"],
            receiving=[Contract(player="Cheaper Player", salary=10_000_000)],
        )
    ])
    assert not result.legal
    assert any("aggregation" in v.rule for v in result.violations)
