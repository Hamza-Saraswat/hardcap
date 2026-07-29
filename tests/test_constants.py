"""Constants tests.

These are the most important tests in the project. If a threshold is wrong here, every
training example built on it is wrong, and the model learns the error confidently.
"""

import pytest

from capengine.constants import (
    BASE_CAP_2023_24,
    SEASONS,
    get_season,
    index_from_base,
    round_to_1000,
)


def test_published_thresholds_2026_27():
    """Verified against the NBA's June 30, 2026 press release."""
    k = get_season("2026-27")
    assert k.cap == 164_961_000
    assert k.tax_line == 200_428_000
    assert k.first_apron == 209_015_000
    assert k.second_apron == 221_686_000
    assert k.non_taxpayer_mle == 15_044_000
    assert k.taxpayer_mle == 6_064_000
    assert k.room_exception == 9_366_000
    assert k.min_team_salary == 148_465_000


def test_published_thresholds_2025_26():
    k = get_season("2025-26")
    assert k.cap == 154_647_000
    assert k.tax_line == 187_895_000
    assert k.first_apron == 195_945_000
    assert k.second_apron == 207_824_000


def test_indexing_formula_reproduces_published_trade_band():
    """The strongest available check on both the formula and the 2023-24 base values.

    The league published the 2026-27 expanded-TPE band at $9,096,000. Indexing the
    2023-24 base of $7.5M by the cap ratio has to land exactly there.
    """
    k = get_season("2026-27")
    assert k.trade_band_lower == 9_096_000
    assert index_from_base(7_500_000, k.cap) == 9_096_000


def test_tax_bracket_width_matches_taxpayer_mle_every_season():
    """Both index off a $5,000,000 base in 2023-24, so they coincide by construction.

    Holding across all three seasons independently confirms the base cap is right.
    """
    for season, k in SEASONS.items():
        assert k.tax_bracket_width == k.taxpayer_mle, season
        assert index_from_base(5_000_000, k.cap) == k.taxpayer_mle, season


def test_max_salary_tiers_are_exact_cap_percentages():
    """Published 2026-27 maxes: $41,240,250 / $49,488,300 / $57,736,350."""
    k = get_season("2026-27")
    assert k.max_salary_25 == 41_240_250
    assert k.max_salary_30 == 49_488_300
    assert k.max_salary_35 == 57_736_350


def test_base_cap_is_the_2023_24_figure():
    assert BASE_CAP_2023_24 == 136_021_000


def test_round_to_1000_rounds_half_away_from_zero():
    assert round_to_1000(1_500) == 2_000
    assert round_to_1000(1_499) == 1_000
    assert round_to_1000(9_095_709.4) == 9_096_000


def test_2026_27_cap_grew_less_than_the_ten_percent_maximum():
    """The trap this project trains against: everyone assumed +10% and got +6.7%."""
    prior = get_season("2025-26").cap
    current = get_season("2026-27").cap
    growth = (current - prior) / prior
    assert 0.06 < growth < 0.07
    assert current < int(prior * 1.10)


def test_unknown_season_refuses_to_extrapolate():
    with pytest.raises(ValueError, match="Refusing to extrapolate"):
        get_season("2027-28")


def test_absent_figures_raise_rather_than_guess():
    """2024-25's bi-annual exception was never verified, so it must not be invented."""
    k = get_season("2024-25")
    assert k.bi_annual_exception is None
    with pytest.raises(ValueError, match="Refusing to guess"):
        k.require("bi_annual_exception")


def test_minimum_scale_published_figures():
    k = get_season("2026-27")
    assert k.minimum_salary(0) == 1_357_763
    assert k.minimum_salary(10) == 3_876_529
    assert k.minimum_salary(15) == 3_876_529, "10+ YOS all share the top rate"


def test_veteran_minimum_cap_charge_uses_two_year_rate():
    """A 10-year vet on a one-year minimum counts at the 2-YOS rate; the league pays the rest."""
    k = get_season("2026-27")
    assert k.minimum_cap_charge(10) == k.minimum_salary(2) == 2_449_421
    assert k.minimum_cap_charge(1) == k.minimum_salary(1)
