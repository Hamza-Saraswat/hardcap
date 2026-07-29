"""Luxury tax computation.

The tax is assessed in brackets: each slice of salary above the tax line is taxed at a
progressively higher rate. The 2023 CBA rewrote these rates effective 2025-26, making the
first brackets *cheaper* and the repeater brackets far harsher -- a deliberate push to make
brief trips into the tax survivable and permanent residence ruinous.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from capengine.constants import TAX_RATE_INCREMENT_BEYOND
from capengine.models import Team
from capengine.trace import Trace, usd


def bracket_rate(index: int, rates: tuple[float, ...]) -> float:
    """Rate for bracket `index` (0-based); beyond the published brackets, +$0.50 each."""
    if index < len(rates):
        return rates[index]
    return rates[-1] + TAX_RATE_INCREMENT_BEYOND * (index - len(rates) + 1)


@dataclass
class TaxBracket:
    index: int
    amount: int
    rate: float
    owed: int


@dataclass
class TaxResult:
    team: str
    season: str
    tax_salary: int
    tax_line: int
    amount_over: int
    is_repeater: bool
    brackets: list[TaxBracket] = field(default_factory=list)
    total: int = 0
    trace: Trace = field(default_factory=Trace)

    @property
    def is_taxpayer(self) -> bool:
        return self.amount_over > 0


def compute_tax(team: Team) -> TaxResult:
    """Compute a team's luxury tax bill, showing the work bracket by bracket."""
    k = team.constants
    trace = Trace()

    tax_salary = team.tax_salary
    amount_over = tax_salary - k.tax_line

    trace.add(f"{team.name} tax salary", tax_salary)
    trace.add(f"{k.season} luxury tax line", k.tax_line)

    result = TaxResult(
        team=team.name,
        season=k.season,
        tax_salary=tax_salary,
        tax_line=k.tax_line,
        amount_over=max(0, amount_over),
        is_repeater=team.is_repeater,
        trace=trace,
    )

    if amount_over <= 0:
        trace.add(
            "Amount over the tax line",
            0,
            f"{usd(tax_salary)} is {usd(-amount_over)} below the line -- no tax owed",
        )
        return result

    trace.add(
        "Amount over the tax line",
        amount_over,
        f"{usd(tax_salary)} - {usd(k.tax_line)}",
    )

    rates = k.tax_rates(repeater=team.is_repeater)
    schedule = "repeater" if team.is_repeater else "standard"
    trace.add(
        f"Rate schedule: {schedule} ({k.season})",
        detail="rates rise $0.50 per bracket beyond the published four",
    )

    remaining = amount_over
    index = 0
    total = 0
    while remaining > 0:
        slice_amount = min(remaining, k.tax_bracket_width)
        rate = bracket_rate(index, rates)
        owed = round(slice_amount * rate)
        total += owed
        result.brackets.append(
            TaxBracket(index=index, amount=slice_amount, rate=rate, owed=owed)
        )
        trace.add(
            f"Bracket {index + 1}: {usd(slice_amount)} at ${rate:.2f} per dollar",
            owed,
        )
        remaining -= slice_amount
        index += 1

    result.total = total
    trace.add("Total luxury tax owed", total)

    if team.is_repeater:
        trace.add(
            "Repeater status applies",
            detail="paid the tax in 3 of the prior 4 seasons",
        )
    trace.add(
        "Tax distribution forfeited",
        detail="taxpayers receive no share of the 50% distributed to non-taxpaying teams",
    )

    return result
