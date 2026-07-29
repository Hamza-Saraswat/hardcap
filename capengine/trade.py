"""Trade legality under the 2023 CBA.

Four things decide whether a trade is legal for a given team, and they interact:

  1. Salary matching. Below the first apron a team gets the generous "expanded" bands;
     at or above it, a flat 100% ceiling.
  2. Apron prohibitions. Over the second apron a team may not aggregate salaries or send
     cash at all -- no exception, no workaround.
  3. Hard caps. Several otherwise-legal moves (taking back more than 100%, aggregating,
     sending cash) hard-cap the team for the rest of the league year. A move that would
     push it past its own hard cap is illegal.
  4. Player-specific restrictions -- no-trade clauses, recently-signed and recently-acquired
     players who cannot be moved or re-aggregated.

Apron status is evaluated upon the conclusion of each transaction, so a team's position
*after* the trade is what the hard-cap checks are applied to.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from capengine.constants import (
    MATCH_CUSHION,
    MATCH_LARGE_MULTIPLIER,
    MATCH_SMALL_MULTIPLIER,
    MAX_STANDARD_ROSTER,
    SeasonConstants,
)
from capengine.models import Contract, HardCap, Team
from capengine.trace import Trace, usd


@dataclass
class Violation:
    team: str
    rule: str
    detail: str

    def __str__(self) -> str:
        return f"{self.team}: {self.rule} -- {self.detail}"


@dataclass
class TradeSide:
    """One team's participation in a trade."""

    team: Team
    sending: list[str] = field(default_factory=list)
    receiving: list[Contract] = field(default_factory=list)
    cash_sent: int = 0
    cash_received: int = 0
    # Set when this team is absorbing salary into a traded player exception rather than
    # matching it with outgoing salary.
    using_tpe: int | None = None
    tpe_is_prior_year: bool = False


@dataclass
class SideResult:
    team: str
    outgoing_salary: int
    incoming_salary: int
    max_incoming: int
    matching_rule: str
    aggregating: bool
    apron_salary_after: int
    hard_cap_triggered: HardCap = HardCap.NONE
    legal: bool = True


@dataclass
class TradeResult:
    legal: bool
    violations: list[Violation] = field(default_factory=list)
    sides: list[SideResult] = field(default_factory=list)
    trace: Trace = field(default_factory=Trace)

    @property
    def verdict(self) -> str:
        return "LEGAL" if self.legal else "ILLEGAL"

    def summary(self) -> str:
        if self.legal:
            return "This trade is legal under the 2023 CBA."
        reasons = "; ".join(str(v) for v in self.violations)
        return f"This trade is not legal. {reasons}"


def max_incoming_expanded(outgoing: int, k: SeasonConstants) -> tuple[int, str]:
    """Most salary a below-the-first-apron team may take back, and which band applied."""
    if outgoing <= k.trade_band_lower:
        allowed = int(outgoing * MATCH_SMALL_MULTIPLIER) + MATCH_CUSHION
        rule = f"200% + {usd(MATCH_CUSHION)} (outgoing at or below {usd(k.trade_band_lower)})"
    elif outgoing <= k.trade_band_upper:
        allowed = outgoing + k.trade_band_lower
        rule = f"outgoing + {usd(k.trade_band_lower)} (middle band)"
    else:
        allowed = int(outgoing * MATCH_LARGE_MULTIPLIER) + MATCH_CUSHION
        rule = f"125% + {usd(MATCH_CUSHION)} (outgoing above {usd(k.trade_band_upper)})"
    return allowed, rule


def evaluate_trade(sides: list[TradeSide]) -> TradeResult:
    """Check a trade of any size, team by team, and show the work."""
    trace = Trace()
    result = TradeResult(legal=True, trace=trace)

    names = ", ".join(s.team.name for s in sides)
    trace.add(f"Evaluating a {len(sides)}-team trade: {names}")

    for side in sides:
        _evaluate_side(side, result, trace)

    result.legal = not result.violations
    trace.add(f"Verdict: {result.verdict}")
    return result


def _evaluate_side(side: TradeSide, result: TradeResult, trace: Trace) -> None:
    team = side.team
    k = team.constants
    level = team.apron_level

    trace.add(
        f"--- {team.name} ({k.season}) ---",
        detail=f"apron salary {usd(team.apron_salary)}, {level.value}",
    )

    outgoing_contracts = [team.find(name) for name in side.sending]
    outgoing = sum(c.outgoing_trade_value for c in outgoing_contracts)
    incoming = sum(c.salary for c in side.receiving)
    aggregating = len(outgoing_contracts) > 1

    trace.add(f"{team.name} outgoing salary", outgoing,
              detail=", ".join(f"{c.player} {usd(c.salary)}" for c in outgoing_contracts) or "none")
    trace.add(f"{team.name} incoming salary", incoming,
              detail=", ".join(f"{c.player} {usd(c.salary)}" for c in side.receiving) or "none")

    def violate(rule: str, detail: str) -> None:
        result.violations.append(Violation(team=team.name, rule=rule, detail=detail))
        trace.add(f"VIOLATION -- {rule}", detail=detail)

    # -- player-specific restrictions ------------------------------------------------
    for contract in outgoing_contracts:
        if contract.no_trade_clause:
            violate("no-trade clause",
                    f"{contract.player} holds a no-trade clause and must consent")
        if contract.cannot_be_traded:
            violate("player cannot be traded",
                    f"{contract.player}: {contract.cannot_be_traded}")
        if aggregating and contract.cannot_be_aggregated:
            violate("player cannot be aggregated",
                    f"{contract.player}: {contract.cannot_be_aggregated}")

    # -- second-apron prohibitions ---------------------------------------------------
    if team.is_over_second_apron:
        if aggregating:
            violate(
                "second-apron aggregation ban",
                f"{team.name} is over the second apron ({usd(team.apron_salary)} vs "
                f"{usd(k.second_apron)}) and may not combine "
                f"{len(outgoing_contracts)} salaries in one trade",
            )
        if side.cash_sent > 0:
            violate(
                "second-apron cash ban",
                f"{team.name} is over the second apron and may not send cash in any trade",
            )

    # -- prior-year traded player exceptions -----------------------------------------
    if side.using_tpe is not None and side.tpe_is_prior_year and team.is_over_first_apron:
        violate(
            "prior-year TPE unavailable",
            f"{team.name} is over the first apron and may not use a traded player "
            "exception generated in a previous league year",
        )

    # -- salary matching --------------------------------------------------------------
    hard_cap_triggered = HardCap.NONE
    if side.using_tpe is not None:
        max_incoming = side.using_tpe
        matching_rule = f"absorbed into a {usd(side.using_tpe)} traded player exception"
        trace.add(f"{team.name} matching limit", max_incoming, detail=matching_rule)
    elif team.is_over_first_apron:
        max_incoming = outgoing
        matching_rule = "100% of outgoing salary (team is over the first apron)"
        trace.add(f"{team.name} matching limit", max_incoming, detail=matching_rule)
    else:
        max_incoming, band = max_incoming_expanded(outgoing, k)
        matching_rule = band
        trace.add(f"{team.name} matching limit", max_incoming, detail=band)

    if incoming > max_incoming:
        violate(
            "salary matching",
            f"{team.name} takes back {usd(incoming)} but may only absorb "
            f"{usd(max_incoming)} under {matching_rule} -- over by "
            f"{usd(incoming - max_incoming)}",
        )

    # -- hard caps triggered by this trade --------------------------------------------
    if not team.is_over_first_apron and incoming > outgoing and side.using_tpe is None:
        hard_cap_triggered = HardCap.FIRST_APRON
        trace.add(
            f"{team.name} hard-capped at the first apron",
            k.first_apron,
            detail="took back more than 100% of outgoing salary",
        )
    if aggregating and not team.is_over_second_apron:
        hard_cap_triggered = HardCap.SECOND_APRON
        trace.add(
            f"{team.name} hard-capped at the second apron",
            k.second_apron,
            detail="aggregated two or more salaries in one trade",
        )
    if side.cash_sent > 0 and not team.is_over_second_apron:
        hard_cap_triggered = HardCap.SECOND_APRON
        trace.add(
            f"{team.name} hard-capped at the second apron",
            k.second_apron,
            detail="sent cash in a trade",
        )

    # -- post-trade position ----------------------------------------------------------
    apron_after = (
        team.apron_salary
        - sum(c.apron_hit for c in outgoing_contracts)
        + sum(c.apron_hit for c in side.receiving)
    )
    trace.add(f"{team.name} apron salary after the trade", apron_after)

    effective_cap = _effective_hard_cap(team, hard_cap_triggered, k)
    if effective_cap is not None:
        label, limit = effective_cap
        if apron_after > limit:
            violate(
                "hard cap exceeded",
                f"{team.name} would sit at {usd(apron_after)}, above its {label} hard cap "
                f"of {usd(limit)} -- over by {usd(apron_after - limit)}",
            )
        else:
            trace.add(
                f"{team.name} stays under its {label} hard cap",
                limit - apron_after,
                detail=f"{usd(limit)} - {usd(apron_after)} of room to spare",
            )

    # -- roster limits ----------------------------------------------------------------
    roster_after = team.roster_count - len(outgoing_contracts) + len(side.receiving)
    if roster_after > MAX_STANDARD_ROSTER:
        violate(
            "roster limit",
            f"{team.name} would carry {roster_after} players, above the "
            f"{MAX_STANDARD_ROSTER}-man limit",
        )

    result.sides.append(
        SideResult(
            team=team.name,
            outgoing_salary=outgoing,
            incoming_salary=incoming,
            max_incoming=max_incoming,
            matching_rule=matching_rule,
            aggregating=aggregating,
            apron_salary_after=apron_after,
            hard_cap_triggered=hard_cap_triggered,
            legal=not any(v.team == team.name for v in result.violations),
        )
    )


def _effective_hard_cap(
    team: Team, triggered: HardCap, k: SeasonConstants
) -> tuple[str, int] | None:
    """The tighter of a team's existing hard cap and any this trade triggers."""
    candidates: list[tuple[str, int]] = []
    if team.hard_cap is HardCap.FIRST_APRON:
        candidates.append(("first apron", k.first_apron))
    elif team.hard_cap is HardCap.SECOND_APRON:
        candidates.append(("second apron", k.second_apron))
    if triggered is HardCap.FIRST_APRON:
        candidates.append(("first apron", k.first_apron))
    elif triggered is HardCap.SECOND_APRON:
        candidates.append(("second apron", k.second_apron))
    if not candidates:
        return None
    return min(candidates, key=lambda c: c[1])


def apply_trade(side: TradeSide) -> Team:
    """Return the team as it would look after the trade, for multi-step scenarios."""
    team = side.team
    kept = team.without(side.sending)
    return replace(
        team,
        contracts=kept + list(side.receiving),
    )
