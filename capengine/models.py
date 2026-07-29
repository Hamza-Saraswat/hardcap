"""Roster and team-salary data structures.

The subtlety worth knowing before reading: a team has *three* different salary totals, and
using the wrong one is the most common way to get apron questions wrong.

  - cap salary  : base salaries + likely incentives + dead money
  - tax salary  : same basis; what the luxury tax is assessed on
  - apron salary: cap salary PLUS unlikely incentives

That last line is why Toronto sat over the first apron in 2025-26 while looking comfortably
under it on a normal cap sheet -- unlikely bonuses for Barrett, Quickley, and Poeltl counted
for apron purposes only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from capengine.constants import SeasonConstants, get_season


class ApronLevel(str, Enum):
    """Where a team sits, in ascending order of restriction."""

    UNDER_TAX = "under the tax line"
    OVER_TAX = "over the tax line"
    OVER_FIRST_APRON = "over the first apron"
    OVER_SECOND_APRON = "over the second apron"

    @property
    def rank(self) -> int:
        return _APRON_ORDER.index(self)

    def at_least(self, other: ApronLevel) -> bool:
        return self.rank >= other.rank


_APRON_ORDER = [
    ApronLevel.UNDER_TAX,
    ApronLevel.OVER_TAX,
    ApronLevel.OVER_FIRST_APRON,
    ApronLevel.OVER_SECOND_APRON,
]


class HardCap(str, Enum):
    NONE = "none"
    FIRST_APRON = "first apron"
    SECOND_APRON = "second apron"


class OptionType(str, Enum):
    NONE = "none"
    PLAYER = "player option"
    TEAM = "team option"
    EARLY_TERMINATION = "early termination option"


@dataclass
class Contract:
    """One player's deal, as it appears on a cap sheet."""

    player: str
    salary: int
    years_remaining: int = 1
    incentives_likely: int = 0
    incentives_unlikely: int = 0
    option: OptionType = OptionType.NONE
    no_trade_clause: bool = False
    # Bird rights matter for re-signing over the cap.
    bird_rights: bool = False
    # Set when a rule blocks trading or aggregating this player (recently signed, recently
    # acquired, poison-pill provision). Scenarios state these explicitly rather than having
    # the engine infer them from dates.
    cannot_be_traded: str | None = None
    cannot_be_aggregated: str | None = None
    # Minimum-salary deals signed by 3+ YOS veterans hit the cap at the 2-YOS rate.
    is_minimum_deal: bool = False
    years_of_service: int = 0

    @property
    def cap_hit(self) -> int:
        """What this contract counts for cap and tax purposes."""
        return self.salary + self.incentives_likely

    @property
    def apron_hit(self) -> int:
        """What this contract counts for apron purposes -- unlikely incentives included."""
        return self.salary + self.incentives_likely + self.incentives_unlikely

    @property
    def outgoing_trade_value(self) -> int:
        """Salary usable for matching when this player is traded away."""
        return self.salary


@dataclass
class Team:
    """A team's salary situation in one league year."""

    name: str
    season: str = "2026-27"
    contracts: list[Contract] = field(default_factory=list)
    dead_money: int = 0
    cap_holds: int = 0
    hard_cap: HardCap = HardCap.NONE
    # Repeater = paid the tax in 3 of the prior 4 seasons.
    is_repeater: bool = False
    # Exceptions already spent this league year.
    used_non_taxpayer_mle: int = 0
    used_taxpayer_mle: int = 0
    used_bi_annual: bool = False
    # Traded player exceptions available, split by whether they were generated this year.
    tpes_current_year: list[int] = field(default_factory=list)
    tpes_prior_year: list[int] = field(default_factory=list)
    # Seasons already finished over the second apron, for draft-penalty questions.
    seasons_over_second_apron: int = 0
    # Lets a scenario supply its own thresholds instead of the published ones. Anti-staleness
    # training examples depend on this: they paste a constants block whose figures differ
    # from any real season, and the ground truth must be computed from those pasted numbers
    # so the model is rewarded for reading rather than recalling.
    constants_override: SeasonConstants | None = None

    @property
    def constants(self) -> SeasonConstants:
        return self.constants_override or get_season(self.season)

    @property
    def roster_count(self) -> int:
        return len(self.contracts)

    @property
    def cap_salary(self) -> int:
        return sum(c.cap_hit for c in self.contracts) + self.dead_money + self.cap_holds

    @property
    def tax_salary(self) -> int:
        return sum(c.cap_hit for c in self.contracts) + self.dead_money

    @property
    def apron_salary(self) -> int:
        """Cap salary plus unlikely incentives -- the figure apron rules are applied to."""
        return sum(c.apron_hit for c in self.contracts) + self.dead_money + self.cap_holds

    @property
    def unlikely_incentives(self) -> int:
        return sum(c.incentives_unlikely for c in self.contracts)

    @property
    def apron_level(self) -> ApronLevel:
        k = self.constants
        salary = self.apron_salary
        if salary > k.second_apron:
            return ApronLevel.OVER_SECOND_APRON
        if salary > k.first_apron:
            return ApronLevel.OVER_FIRST_APRON
        if salary > k.tax_line:
            return ApronLevel.OVER_TAX
        return ApronLevel.UNDER_TAX

    @property
    def is_over_first_apron(self) -> bool:
        return self.apron_level.at_least(ApronLevel.OVER_FIRST_APRON)

    @property
    def is_over_second_apron(self) -> bool:
        return self.apron_level is ApronLevel.OVER_SECOND_APRON

    @property
    def cap_space(self) -> int:
        """Room under the salary cap; zero for an over-the-cap team."""
        return max(0, self.constants.cap - self.cap_salary)

    @property
    def hard_cap_limit(self) -> int | None:
        k = self.constants
        if self.hard_cap is HardCap.FIRST_APRON:
            return k.first_apron
        if self.hard_cap is HardCap.SECOND_APRON:
            return k.second_apron
        return None

    def room_below(self, threshold: int) -> int:
        """Dollars of apron salary a team can add before crossing `threshold`."""
        return threshold - self.apron_salary

    def find(self, player: str) -> Contract:
        for contract in self.contracts:
            if contract.player.lower() == player.lower():
                return contract
        raise KeyError(f"{player!r} is not on {self.name}'s roster")

    def without(self, players: list[str]) -> list[Contract]:
        lowered = {p.lower() for p in players}
        return [c for c in self.contracts if c.player.lower() not in lowered]
