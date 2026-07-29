from capengine.constants import get_season
from capengine.models import Team
from capengine.tax import bracket_rate, compute_tax
from tests.conftest import team_at


def test_no_tax_below_the_line():
    result = compute_tax(team_at(150_000_000))
    assert not result.is_taxpayer
    assert result.total == 0
    assert result.amount_over == 0


def test_first_bracket_standard_rate_2026_27():
    """$1.00 per dollar in the first bracket under the rates that began in 2025-26."""
    k = get_season("2026-27")
    team = team_at(k.tax_line + 3_000_000)
    result = compute_tax(team)
    assert result.amount_over == 3_000_000
    assert len(result.brackets) == 1
    assert result.brackets[0].rate == 1.00
    assert result.total == 3_000_000


def test_multi_bracket_decomposition():
    """$10M over in 2026-27: $6,064,000 at $1.00, then the remainder at $1.25."""
    k = get_season("2026-27")
    team = team_at(k.tax_line + 10_000_000)
    result = compute_tax(team)

    assert result.amount_over == 10_000_000
    assert len(result.brackets) == 2

    first, second = result.brackets
    assert first.amount == k.tax_bracket_width == 6_064_000
    assert first.rate == 1.00
    assert first.owed == 6_064_000

    assert second.amount == 10_000_000 - 6_064_000
    assert second.rate == 1.25
    assert second.owed == round((10_000_000 - 6_064_000) * 1.25)

    assert result.total == first.owed + second.owed


def test_repeater_rates_are_far_harsher():
    k = get_season("2026-27")
    salary = k.tax_line + 10_000_000
    standard = compute_tax(team_at(salary))
    repeater = compute_tax(team_at(salary, is_repeater=True))

    assert repeater.total > standard.total * 2
    assert repeater.brackets[0].rate == 3.00
    assert standard.brackets[0].rate == 1.00


def test_2024_25_uses_the_old_schedule():
    """The 2023 CBA's new rates took effect in 2025-26, not before."""
    old = compute_tax(team_at(get_season("2024-25").tax_line + 1_000_000, season="2024-25"))
    new = compute_tax(team_at(get_season("2025-26").tax_line + 1_000_000, season="2025-26"))
    assert old.brackets[0].rate == 1.50
    assert new.brackets[0].rate == 1.00, "first bracket got cheaper under the new schedule"


def test_rates_climb_by_fifty_cents_beyond_the_published_brackets():
    rates = get_season("2026-27").tax_rates(repeater=False)
    assert bracket_rate(0, rates) == 1.00
    assert bracket_rate(3, rates) == 4.75
    assert bracket_rate(4, rates) == 5.25
    assert bracket_rate(5, rates) == 5.75


def test_deep_taxpayer_walks_through_many_brackets():
    k = get_season("2026-27")
    result = compute_tax(team_at(k.tax_line + 40_000_000, is_repeater=True))
    assert len(result.brackets) == 7
    assert sum(b.amount for b in result.brackets) == 40_000_000
    assert result.total == sum(b.owed for b in result.brackets)


def test_dead_money_counts_toward_the_tax():
    k = get_season("2026-27")
    team = Team(name="T", dead_money=k.tax_line + 5_000_000)
    assert compute_tax(team).amount_over == 5_000_000


def test_trace_records_every_reported_figure():
    result = compute_tax(team_at(get_season("2026-27").tax_line + 10_000_000))
    values = result.trace.values()
    assert result.total in values
    assert result.amount_over in values
    for bracket in result.brackets:
        assert bracket.owed in values
