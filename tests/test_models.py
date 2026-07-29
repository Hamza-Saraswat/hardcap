from capengine.models import ApronLevel, Contract, Team
from tests.conftest import team_at


def test_apron_levels_by_salary():
    assert team_at(150_000_000).apron_level is ApronLevel.UNDER_TAX
    assert team_at(205_000_000).apron_level is ApronLevel.OVER_TAX
    assert team_at(215_000_000).apron_level is ApronLevel.OVER_FIRST_APRON
    assert team_at(230_000_000).apron_level is ApronLevel.OVER_SECOND_APRON


def test_thresholds_are_exclusive():
    """A team sitting exactly on a threshold is not over it."""
    k = team_at(1).constants
    assert team_at(k.second_apron).apron_level is ApronLevel.OVER_FIRST_APRON
    assert team_at(k.second_apron + 1).apron_level is ApronLevel.OVER_SECOND_APRON


def test_unlikely_incentives_count_for_aprons_but_not_cap_or_tax():
    """The Toronto case: unlikely bonuses alone can put a team over the first apron.

    In 2025-26 the Raptors sat over the first apron purely on unlikely incentives for
    Barrett ($3.4M), Quickley ($2.5M), and Poeltl ($0.5M).
    """
    team = Team(
        name="Raptors",
        season="2025-26",
        contracts=[
            Contract(player="RJ Barrett", salary=28_000_000, incentives_unlikely=3_400_000),
            Contract(player="Immanuel Quickley", salary=32_000_000, incentives_unlikely=2_500_000),
            Contract(player="Jakob Poeltl", salary=19_500_000, incentives_unlikely=500_000),
            Contract(player="Filler", salary=114_000_000),
        ],
    )
    assert team.tax_salary == 193_500_000
    assert team.apron_salary == 199_900_000
    assert team.unlikely_incentives == 6_400_000

    # Below the first apron on a normal cap sheet, above it for apron purposes.
    assert team.tax_salary < team.constants.first_apron
    assert team.apron_salary > team.constants.first_apron
    assert team.is_over_first_apron


def test_likely_incentives_count_everywhere():
    team = Team(
        name="T",
        contracts=[Contract(player="P", salary=10_000_000, incentives_likely=1_000_000)],
    )
    assert team.tax_salary == 11_000_000
    assert team.apron_salary == 11_000_000


def test_cap_space_is_zero_for_an_over_the_cap_team():
    assert team_at(215_000_000).cap_space == 0
    under = team_at(140_000_000)
    assert under.cap_space == under.constants.cap - 140_000_000


def test_room_below_threshold():
    team = team_at(215_000_000)
    k = team.constants
    assert team.room_below(k.second_apron) == k.second_apron - 215_000_000
