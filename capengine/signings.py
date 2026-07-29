"""Exceptions, signings, the stretch provision, and second-apron draft penalties.

The exception ladder is where the aprons bite hardest in free agency. Below the tax a team
has everything; over the first apron it loses the full mid-level and the bi-annual; over the
second apron it loses the mid-level entirely and is left with minimums and its own Bird
rights. Using an exception you *do* still have generally hard-caps you for the rest of the
league year, which is why the trigger is tracked alongside availability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from capengine.constants import (
    FROZEN_PICK_YEARS_OUT,
    PICK_DEMOTION_SEASONS_OVER,
    PICK_DEMOTION_WINDOW,
    STRETCH_DEAD_MONEY_CAP_PCT,
)
from capengine.models import HardCap, Team
from capengine.trace import Trace, usd


class ExceptionType(str, Enum):
    NON_TAXPAYER_MLE = "non-taxpayer mid-level exception"
    TAXPAYER_MLE = "taxpayer mid-level exception"
    BI_ANNUAL = "bi-annual exception"
    ROOM = "room exception"
    MINIMUM = "minimum salary exception"


@dataclass
class ExceptionStatus:
    exception: ExceptionType
    available: bool
    amount: int | None
    hard_cap_triggered: HardCap
    reason: str


def available_exceptions(team: Team) -> list[ExceptionStatus]:
    """Which signing exceptions a team can actually use, and what each one costs it."""
    k = team.constants
    over_first = team.is_over_first_apron
    over_second = team.is_over_second_apron
    has_room = team.cap_space > 0

    statuses: list[ExceptionStatus] = []

    statuses.append(
        ExceptionStatus(
            exception=ExceptionType.NON_TAXPAYER_MLE,
            available=not over_first and not has_room,
            amount=None if over_first else k.non_taxpayer_mle,
            hard_cap_triggered=HardCap.FIRST_APRON,
            reason=(
                "unavailable over the first apron"
                if over_first
                else "a team with cap space uses the room exception instead"
                if has_room
                else f"available at {usd(k.non_taxpayer_mle)}; using it hard-caps the team "
                "at the first apron"
            ),
        )
    )

    statuses.append(
        ExceptionStatus(
            exception=ExceptionType.TAXPAYER_MLE,
            available=not over_second and not has_room,
            amount=None if over_second else k.taxpayer_mle,
            hard_cap_triggered=HardCap.SECOND_APRON,
            reason=(
                "unavailable over the second apron -- no mid-level of any kind"
                if over_second
                else "a team with cap space uses the room exception instead"
                if has_room
                else f"available at {usd(k.taxpayer_mle)}; using it hard-caps the team at "
                "the second apron"
            ),
        )
    )

    bae_amount = k.bi_annual_exception
    statuses.append(
        ExceptionStatus(
            exception=ExceptionType.BI_ANNUAL,
            available=not over_first and not has_room and not team.used_bi_annual,
            amount=None if over_first else bae_amount,
            hard_cap_triggered=HardCap.FIRST_APRON,
            reason=(
                "unavailable over the first apron"
                if over_first
                else "already used this league year"
                if team.used_bi_annual
                else "a team with cap space uses the room exception instead"
                if has_room
                else (
                    f"available at {usd(bae_amount)}; using it hard-caps the team at the "
                    "first apron"
                    if bae_amount is not None
                    else "available, but the published amount for this season is not on file"
                )
            ),
        )
    )

    statuses.append(
        ExceptionStatus(
            exception=ExceptionType.ROOM,
            available=has_room,
            amount=k.room_exception if has_room else None,
            hard_cap_triggered=HardCap.NONE,
            reason=(
                f"available at {usd(k.room_exception)} once cap space is used; triggers no "
                "hard cap"
                if has_room
                else "only available to a team operating under the cap"
            ),
        )
    )

    statuses.append(
        ExceptionStatus(
            exception=ExceptionType.MINIMUM,
            available=True,
            amount=None,
            hard_cap_triggered=HardCap.NONE,
            reason="always available at any apron level; triggers no hard cap",
        )
    )

    return statuses


@dataclass
class SigningResult:
    legal: bool
    exception: ExceptionType
    salary: int
    hard_cap_triggered: HardCap
    reasons: list[str] = field(default_factory=list)
    apron_salary_after: int = 0
    trace: Trace = field(default_factory=Trace)

    @property
    def verdict(self) -> str:
        return "LEGAL" if self.legal else "ILLEGAL"


def evaluate_signing(
    team: Team, salary: int, exception: ExceptionType, player: str = "the player"
) -> SigningResult:
    """Can this team sign this player for this money using this exception?"""
    k = team.constants
    trace = Trace()
    reasons: list[str] = []

    trace.add(
        f"{team.name} apron salary before signing",
        team.apron_salary,
        detail=team.apron_level.value,
    )
    trace.add(f"Proposed salary for {player}", salary)
    trace.add(f"Exception: {exception.value}")

    status = next(s for s in available_exceptions(team) if s.exception is exception)
    legal = True

    if not status.available:
        legal = False
        reasons.append(f"{exception.value} is {status.reason}")
        trace.add(f"VIOLATION -- {exception.value} unavailable", detail=status.reason)
    elif status.amount is not None and salary > status.amount:
        legal = False
        reasons.append(
            f"{usd(salary)} exceeds the {exception.value} of {usd(status.amount)} by "
            f"{usd(salary - status.amount)}"
        )
        trace.add(f"{exception.value} maximum", status.amount)
        trace.add("VIOLATION -- salary exceeds the exception amount",
                  salary - status.amount)
    elif status.amount is not None:
        trace.add(f"{exception.value} maximum", status.amount)
        trace.add("Room remaining within the exception", status.amount - salary)

    apron_after = team.apron_salary + salary
    trace.add(f"{team.name} apron salary after signing", apron_after)

    hard_cap = status.hard_cap_triggered if status.available else HardCap.NONE
    limit_label, limit = None, None
    if hard_cap is HardCap.FIRST_APRON:
        limit_label, limit = "first apron", k.first_apron
    elif hard_cap is HardCap.SECOND_APRON:
        limit_label, limit = "second apron", k.second_apron
    if team.hard_cap is HardCap.FIRST_APRON:
        limit_label, limit = "first apron", k.first_apron
    elif team.hard_cap is HardCap.SECOND_APRON and limit_label is None:
        limit_label, limit = "second apron", k.second_apron

    if limit is not None:
        trace.add(f"Hard cap: {limit_label}", limit)
        if apron_after > limit:
            legal = False
            reasons.append(
                f"the signing would put {team.name} at {usd(apron_after)}, above its "
                f"{limit_label} hard cap of {usd(limit)}"
            )
            trace.add("VIOLATION -- hard cap exceeded", apron_after - limit)
        else:
            trace.add("Room below the hard cap", limit - apron_after)

    if team.roster_count >= 15:
        legal = False
        reasons.append(f"{team.name} already carries 15 players")
        trace.add("VIOLATION -- roster is full", detail="15-man limit reached")

    trace.add(f"Verdict: {'LEGAL' if legal else 'ILLEGAL'}")

    return SigningResult(
        legal=legal,
        exception=exception,
        salary=salary,
        hard_cap_triggered=hard_cap if legal else HardCap.NONE,
        reasons=reasons,
        apron_salary_after=apron_after,
        trace=trace,
    )


@dataclass
class BuyoutResult:
    allowed: bool
    reason: str
    trace: Trace = field(default_factory=Trace)


def can_sign_buyout_player(team: Team, pre_waiver_salary: int) -> BuyoutResult:
    """The first-apron buyout-market ban: no in-season waivees earning above the NTMLE."""
    k = team.constants
    trace = Trace()
    trace.add(f"{team.name} apron status", team.apron_salary, detail=team.apron_level.value)
    trace.add("Player's pre-waiver salary", pre_waiver_salary)
    trace.add(f"{k.season} non-taxpayer mid-level", k.non_taxpayer_mle)

    if not team.is_over_first_apron:
        reason = (
            f"{team.name} is not over the first apron, so the buyout restriction does not apply"
        )
        trace.add("Allowed", detail=reason)
        return BuyoutResult(allowed=True, reason=reason, trace=trace)

    if pre_waiver_salary > k.non_taxpayer_mle:
        reason = (
            f"{team.name} is over the first apron and may not sign a player waived during "
            f"the regular season whose pre-waiver salary ({usd(pre_waiver_salary)}) exceeded "
            f"the non-taxpayer mid-level ({usd(k.non_taxpayer_mle)})"
        )
        trace.add("VIOLATION -- buyout-market ban", detail=reason)
        return BuyoutResult(allowed=False, reason=reason, trace=trace)

    reason = (
        f"the player's pre-waiver salary of {usd(pre_waiver_salary)} did not exceed the "
        f"non-taxpayer mid-level, so {team.name} may sign him despite being over the first apron"
    )
    trace.add("Allowed", detail=reason)
    return BuyoutResult(allowed=True, reason=reason, trace=trace)


@dataclass
class StretchResult:
    legal: bool
    annual_dead_money: int
    stretch_years: int
    total_stretched: int
    limit: int
    givebacks_required: int
    reason: str
    trace: Trace = field(default_factory=Trace)


def compute_stretch(
    team: Team,
    remaining_salary: int,
    years_remaining: int,
    existing_stretched_dead_money: int = 0,
) -> StretchResult:
    """Apply the stretch provision, including the 15%-of-cap dead-money ceiling.

    This is the rule that stopped Phoenix from simply stretching Bradley Beal in 2025: they
    already carried stretched money, so the full amount would have blown through the limit
    and Beal had to give back roughly $13.9M for the waiver to be legal.
    """
    k = team.constants
    trace = Trace()

    stretch_years = 2 * years_remaining + 1
    annual = round(remaining_salary / stretch_years)
    limit = k.stretch_dead_money_limit
    total = existing_stretched_dead_money + annual

    trace.add("Salary remaining on the contract", remaining_salary)
    trace.add("Years remaining", detail=str(years_remaining))
    trace.add(
        "Stretch period",
        detail=f"2 x {years_remaining} + 1 = {stretch_years} seasons",
    )
    trace.add("Annual dead money if stretched", annual,
              detail=f"{usd(remaining_salary)} / {stretch_years}")
    trace.add("Dead money already stretched", existing_stretched_dead_money)
    trace.add("Total stretched dead money", total)
    trace.add(
        f"Limit ({int(STRETCH_DEAD_MONEY_CAP_PCT * 100)}% of the {k.season} cap)",
        limit,
        detail=f"{int(STRETCH_DEAD_MONEY_CAP_PCT * 100)}% x {usd(k.cap)}",
    )

    if total <= limit:
        reason = (
            f"the stretch is legal: {usd(total)} of total dead money sits below the "
            f"{usd(limit)} ceiling"
        )
        trace.add("Legal", limit - total, detail="room to spare")
        return StretchResult(
            legal=True,
            annual_dead_money=annual,
            stretch_years=stretch_years,
            total_stretched=total,
            limit=limit,
            givebacks_required=0,
            reason=reason,
            trace=trace,
        )

    overage = total - limit
    giveback = overage * stretch_years
    reason = (
        f"the stretch is not legal as structured: {usd(total)} of dead money would exceed "
        f"the {usd(limit)} ceiling by {usd(overage)} per season. The player would have to "
        f"give back roughly {usd(giveback)} for the waiver to work"
    )
    trace.add("VIOLATION -- exceeds the dead-money ceiling", overage)
    trace.add("Approximate giveback required", giveback,
              detail=f"{usd(overage)} x {stretch_years} seasons")

    return StretchResult(
        legal=False,
        annual_dead_money=annual,
        stretch_years=stretch_years,
        total_stretched=total,
        limit=limit,
        givebacks_required=giveback,
        reason=reason,
        trace=trace,
    )


@dataclass
class DraftPenaltyResult:
    pick_frozen: bool
    frozen_draft_year: int | None
    pick_demoted: bool
    reason: str
    trace: Trace = field(default_factory=Trace)


def draft_penalties(
    team: Team, current_draft_year: int, seasons_over_in_window: int | None = None
) -> DraftPenaltyResult:
    """Second-apron draft consequences: the frozen pick and the end-of-round demotion."""
    trace = Trace()
    seasons_over = (
        team.seasons_over_second_apron if seasons_over_in_window is None else seasons_over_in_window
    )

    trace.add(f"{team.name} apron salary", team.apron_salary, detail=team.apron_level.value)
    trace.add("Seasons finished over the second apron (within the window)",
              detail=str(seasons_over))

    if not team.is_over_second_apron:
        reason = f"{team.name} is not over the second apron, so no draft penalty attaches"
        trace.add("No penalty", detail=reason)
        return DraftPenaltyResult(
            pick_frozen=False, frozen_draft_year=None, pick_demoted=False,
            reason=reason, trace=trace,
        )

    frozen_year = current_draft_year + FROZEN_PICK_YEARS_OUT
    trace.add(
        "First-round pick frozen",
        detail=f"the {frozen_year} first-rounder ({FROZEN_PICK_YEARS_OUT} drafts out) "
        "becomes untradeable",
    )

    demoted = seasons_over >= PICK_DEMOTION_SEASONS_OVER
    if demoted:
        trace.add(
            "Pick demoted to the end of the first round",
            detail=f"over the second apron in {seasons_over} of {PICK_DEMOTION_WINDOW} seasons",
        )
        reason = (
            f"{team.name} finishes over the second apron, freezing its {frozen_year} first-round "
            f"pick. Having been over in {seasons_over} of {PICK_DEMOTION_WINDOW} seasons, that "
            "pick also moves to the end of the first round"
        )
    else:
        trace.add(
            "Pick not yet demoted",
            detail=f"demotion requires {PICK_DEMOTION_SEASONS_OVER} of "
            f"{PICK_DEMOTION_WINDOW} seasons over the second apron",
        )
        reason = (
            f"{team.name} finishes over the second apron, freezing its {frozen_year} first-round "
            f"pick. It unfreezes only after finishing below the second apron in 3 of the "
            "following 4 seasons"
        )

    return DraftPenaltyResult(
        pick_frozen=True,
        frozen_draft_year=frozen_year,
        pick_demoted=demoted,
        reason=reason,
        trace=trace,
    )
