"""Per-season salary cap constants.

PROVENANCE POLICY -- this engine produces the ground truth that trains a model, so a wrong
number here silently poisons the whole dataset. Two rules:

  1. Never invent a figure. Thresholds come from NBA press releases (see docs/research/
     cba-rules-reference.md). Anything not verified is either derived by the CBA's own
     documented indexing formula or absent -- and absent means callers get an exception,
     never a plausible guess.
  2. Derived values are marked. `SeasonConstants.derived` lists field names that were
     indexed rather than published.

The indexing formula is given in the CBA: a figure moves with the cap, i.e.
`new = round_to_1000(base * new_cap / base_cap)`. Its correctness is confirmed by
reproducing published figures exactly -- see tests/test_constants.py, which checks that
indexing the 2023-24 trade band of $7.5M yields the published 2026-27 figure of $9,096,000.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# The 2023-24 cap is the base year every indexed figure is measured against.
BASE_CAP_2023_24 = 136_021_000

# Indexed bases, all published for 2023-24.
_BASE_TRADE_BAND_LOWER = 7_500_000
_BASE_TRADE_BAND_UPPER = 29_000_000
_BASE_TAX_BRACKET_WIDTH = 5_000_000

# Salary-matching percentages for a team below the first apron ("expanded TPE" rules).
MATCH_SMALL_MULTIPLIER = 2.00
MATCH_LARGE_MULTIPLIER = 1.25
MATCH_CUSHION = 250_000

# A team over the first apron may not take back more than 100% of outgoing salary.
MATCH_APRON_MULTIPLIER = 1.00

# Luxury tax rates per bracket, in dollars owed per dollar of team salary in that bracket.
# The 2023 CBA made the first brackets cheaper and the repeater brackets far harsher,
# effective 2025-26. Rates beyond the listed brackets increase by $0.50 each.
TAX_RATES_STANDARD_THROUGH_2024_25 = (1.50, 1.75, 2.50, 3.25)
TAX_RATES_REPEATER_THROUGH_2024_25 = (2.50, 2.75, 3.50, 4.25)
TAX_RATES_STANDARD_FROM_2025_26 = (1.00, 1.25, 3.50, 4.75)
TAX_RATES_REPEATER_FROM_2025_26 = (3.00, 3.25, 5.50, 6.75)
TAX_RATE_INCREMENT_BEYOND = 0.50

# Roster rules.
MAX_STANDARD_ROSTER = 15
MIN_STANDARD_ROSTER = 14  # teams may drop to 13 for up to two weeks at a time

# Stretch provision: total stretched dead money may not exceed this share of the cap.
STRETCH_DEAD_MONEY_CAP_PCT = 0.15

# Repeater tax status: paid tax in this many of the prior four seasons.
REPEATER_LOOKBACK_SEASONS = 4
REPEATER_THRESHOLD_SEASONS = 3

# Second-apron draft penalties.
FROZEN_PICK_YEARS_OUT = 7
PICK_DEMOTION_SEASONS_OVER = 3
PICK_DEMOTION_WINDOW = 5


def round_to_1000(amount: float) -> int:
    """Round to the nearest $1,000, half away from zero, as the CBA specifies."""
    thousands = amount / 1000
    return int(thousands + 0.5 if thousands >= 0 else thousands - 0.5) * 1000


def index_from_base(base_value: int, cap: int, base_cap: int = BASE_CAP_2023_24) -> int:
    """Move a 2023-24 figure to another season's cap level."""
    return round_to_1000(base_value * cap / base_cap)


# Minimum salary scale by years of service. Published for 2026-27; other seasons are
# indexed off it. Veterans with 3+ years of service on a one-year minimum deal count
# against the cap at the 2-YOS rate, with the league reimbursing the difference.
MIN_SCALE_2026_27: dict[int, int] = {
    0: 1_357_763,
    1: 2_185_116,
    2: 2_449_421,
    3: 2_537_526,
    4: 2_625_627,
    5: 2_845_883,
    6: 3_066_143,
    7: 3_286_399,
    8: 3_506_659,
    9: 3_524_115,
    10: 3_876_529,
}
MIN_SCALE_CAP_CHARGE_YOS = 2
MAX_SCALE_YOS = 10


@dataclass(frozen=True)
class SeasonConstants:
    """Every threshold needed to evaluate transactions in one league year."""

    season: str
    cap: int
    tax_line: int
    first_apron: int
    second_apron: int
    non_taxpayer_mle: int
    taxpayer_mle: int
    room_exception: int
    tax_bracket_width: int
    min_team_salary: int
    bi_annual_exception: int | None = None
    cash_limit: int | None = None
    min_scale: dict[int, int] = field(default_factory=dict)
    derived: tuple[str, ...] = ()

    # -- derived thresholds ------------------------------------------------------------

    @property
    def trade_band_lower(self) -> int:
        """Outgoing salary at or below this matches at 200% + $250K."""
        return index_from_base(_BASE_TRADE_BAND_LOWER, self.cap)

    @property
    def trade_band_upper(self) -> int:
        """Outgoing salary above this matches at 125% + $250K."""
        return index_from_base(_BASE_TRADE_BAND_UPPER, self.cap)

    @property
    def max_salary_25(self) -> int:
        return int(self.cap * 0.25)

    @property
    def max_salary_30(self) -> int:
        return int(self.cap * 0.30)

    @property
    def max_salary_35(self) -> int:
        return int(self.cap * 0.35)

    @property
    def stretch_dead_money_limit(self) -> int:
        return int(self.cap * STRETCH_DEAD_MONEY_CAP_PCT)

    @property
    def uses_2025_26_tax_rates(self) -> bool:
        return self.season >= "2025-26"

    def tax_rates(self, repeater: bool) -> tuple[float, ...]:
        if self.uses_2025_26_tax_rates:
            return TAX_RATES_REPEATER_FROM_2025_26 if repeater else TAX_RATES_STANDARD_FROM_2025_26
        return TAX_RATES_REPEATER_THROUGH_2024_25 if repeater else TAX_RATES_STANDARD_THROUGH_2024_25

    def minimum_salary(self, years_of_service: int) -> int:
        if not self.min_scale:
            raise ValueError(
                f"No minimum salary scale on file for {self.season}. "
                "Refusing to guess -- add published figures to constants.py."
            )
        return self.min_scale[min(years_of_service, MAX_SCALE_YOS)]

    def minimum_cap_charge(self, years_of_service: int) -> int:
        """Cap hit for a one-year minimum contract (3+ YOS charged at the 2-YOS rate)."""
        if years_of_service <= MIN_SCALE_CAP_CHARGE_YOS:
            return self.minimum_salary(years_of_service)
        return self.minimum_salary(MIN_SCALE_CAP_CHARGE_YOS)

    def require(self, field_name: str) -> int:
        """Fetch a field that may be absent, failing loudly rather than guessing."""
        value = getattr(self, field_name)
        if value is None:
            raise ValueError(
                f"{field_name} is not on file for {self.season}. "
                "Refusing to guess -- add the published figure to constants.py."
            )
        return value


def _scale_min_scale(cap: int) -> dict[int, int]:
    """Index the published 2026-27 minimum scale to another season's cap."""
    return {
        yos: index_from_base(value, cap, base_cap=SEASON_CAPS["2026-27"])
        for yos, value in MIN_SCALE_2026_27.items()
    }


SEASON_CAPS = {
    "2024-25": 140_588_000,
    "2025-26": 154_647_000,
    "2026-27": 164_961_000,
}


SEASONS: dict[str, SeasonConstants] = {
    # All thresholds below published by the NBA; see docs/research/cba-rules-reference.md.
    "2024-25": SeasonConstants(
        season="2024-25",
        cap=140_588_000,
        tax_line=170_814_000,
        first_apron=178_132_000,
        second_apron=188_931_000,
        non_taxpayer_mle=12_822_000,
        taxpayer_mle=5_168_000,
        room_exception=7_983_000,
        tax_bracket_width=5_168_000,
        min_team_salary=126_529_000,
        bi_annual_exception=None,  # ~$4.7M reported but unverified; refuse to guess
        cash_limit=None,
        min_scale=_scale_min_scale(140_588_000),
        derived=("min_scale",),
    ),
    "2025-26": SeasonConstants(
        season="2025-26",
        cap=154_647_000,
        tax_line=187_895_000,
        first_apron=195_945_000,
        second_apron=207_824_000,
        non_taxpayer_mle=14_104_000,
        taxpayer_mle=5_685_000,
        room_exception=8_781_000,
        tax_bracket_width=5_685_000,
        min_team_salary=139_182_000,
        bi_annual_exception=None,  # ~$5.1M reported but unverified
        cash_limit=None,
        min_scale=_scale_min_scale(154_647_000),
        derived=("min_scale",),
    ),
    "2026-27": SeasonConstants(
        season="2026-27",
        cap=164_961_000,
        tax_line=200_428_000,
        first_apron=209_015_000,
        second_apron=221_686_000,
        non_taxpayer_mle=15_044_000,
        taxpayer_mle=6_064_000,
        room_exception=9_366_000,
        tax_bracket_width=6_064_000,
        min_team_salary=148_465_000,
        bi_annual_exception=5_477_000,
        cash_limit=8_495_000,
        min_scale=dict(MIN_SCALE_2026_27),
        derived=(),
    ),
}

DEFAULT_SEASON = "2026-27"


def get_season(season: str = DEFAULT_SEASON) -> SeasonConstants:
    try:
        return SEASONS[season]
    except KeyError:
        available = ", ".join(sorted(SEASONS))
        raise ValueError(
            f"No constants on file for season {season!r}. Available: {available}. "
            "Refusing to extrapolate -- cap growth is not predictable "
            "(2026-27 came in at +6.7%, not the +10% maximum everyone assumed)."
        ) from None
