"""Scenario sampling.

Each sampler builds a random-but-plausible cap situation, asks a question about it, and gets
the answer from CapEngine rather than from a model. The resulting `Scenario` carries
everything the rest of the pipeline needs: the prompt a user would type, the ground truth,
and the trace of every figure the engine actually computed.

A note on names. Synthetic scenarios use invented players. Attaching fabricated salaries to
real players would teach the model false facts about the league -- exactly the failure mode
this architecture exists to avoid, since the model is supposed to read salary data from the
prompt rather than recall it. Real names appear only in the case-study slice, where the
figures are the real ones.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from capengine.constants import SEASONS, SeasonConstants, get_season
from capengine.models import ApronLevel, Contract, HardCap, Team
from capengine.signings import (
    ExceptionType,
    available_exceptions,
    can_sign_buyout_player,
    compute_stretch,
    draft_penalties,
    evaluate_signing,
)
from capengine.tax import compute_tax
from capengine.trace import Trace, usd
from capengine.trade import TradeSide, evaluate_trade
from datagen.capsheet import constants_block, team_context

FIRST_NAMES = [
    "Marcus", "Trey", "Darnell", "Kellen", "Amari", "Julian", "Devonte", "Rashad",
    "Corey", "Jalil", "Tobias", "Brennan", "Malik", "Isaiah", "Cam", "Dante",
    "Zion", "Kobe", "Terrance", "Andre", "Jaylen", "Micah", "Elijah", "Nico",
    "Bogdan", "Luka", "Goran", "Kristaps", "Nikola", "Alperen", "Deni", "Santi",
]
LAST_NAMES = [
    "Whitfield", "Okoro", "Brantley", "Vasquez", "Ellington", "Marsh", "Boateng",
    "Kearns", "Dumont", "Ferreira", "Nakamura", "Osei", "Halvorsen", "Petrov",
    "Cordero", "Amadi", "Lindqvist", "Rees", "Stavros", "Ibarra", "Duval",
    "Beauchamp", "Kalinic", "Novak", "Sabonis", "Jokubaitis", "Achiuwa", "Reddish",
]

CITIES = [
    "Portland", "Sacramento", "Charlotte", "Orlando", "Memphis", "Detroit",
    "Indiana", "Utah", "Atlanta", "Houston", "Toronto", "Chicago", "Washington",
    "Brooklyn", "New Orleans", "San Antonio", "Oklahoma City", "Miami",
]


@dataclass
class Scenario:
    """One training example, before the prose is written."""

    kind: str
    context: str
    question: str
    answer_facts: dict
    trace: Trace
    required_values: list[int] = field(default_factory=list)
    verdict: str | None = None
    season: str = "2026-27"
    notes: str = ""

    @property
    def prompt(self) -> str:
        return f"{self.context}\n\n{self.question}" if self.context else self.question

    def allowed_values(self) -> set[int]:
        """Every figure the answer is permitted to state.

        Three sources, all grounded: values the engine computed, figures embedded in the
        engine's own explanatory detail strings, and numbers the user pasted in.
        """
        return (
            self.trace.values()
            | _numbers_in(self.trace.render())
            | _numbers_in(self.context)
        )


def _numbers_in(text: str) -> set[int]:
    """Pull dollar figures out of pasted context so the verifier accepts them."""
    import re

    values: set[int] = set()
    for match in re.finditer(r"\$?([\d,]{4,})", text):
        raw = match.group(1).replace(",", "")
        if raw.isdigit():
            values.add(int(raw))
    return values


# -- roster construction ----------------------------------------------------------------


def player_name(rng: random.Random) -> str:
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def _salary_ladder(rng: random.Random, target: int, count: int, k: SeasonConstants) -> list[int]:
    """Split a payroll into a plausible star/mid/minimum distribution."""
    minimum = k.minimum_salary(2)
    salaries: list[int] = []
    remaining = target
    remaining_slots = count

    stars = rng.randint(1, 2)
    for _ in range(stars):
        if remaining_slots <= 1:
            break
        salary = rng.randint(int(k.max_salary_25 * 0.75), k.max_salary_35)
        salary = min(salary, remaining - minimum * (remaining_slots - 1))
        if salary < minimum:
            break
        salaries.append(salary)
        remaining -= salary
        remaining_slots -= 1

    mids = rng.randint(2, 4)
    for _ in range(mids):
        if remaining_slots <= 1:
            break
        ceiling = max(minimum, remaining - minimum * (remaining_slots - 1))
        salary = min(rng.randint(8_000_000, 30_000_000), ceiling)
        if salary < minimum:
            break
        salaries.append(salary)
        remaining -= salary
        remaining_slots -= 1

    while remaining_slots > 1:
        ceiling = max(minimum, remaining - minimum * (remaining_slots - 1))
        salary = min(rng.randint(minimum, max(minimum + 1, 9_000_000)), ceiling)
        salaries.append(salary)
        remaining -= salary
        remaining_slots -= 1

    salaries.append(max(remaining, 0))
    rng.shuffle(salaries)
    return salaries


def random_team(
    rng: random.Random,
    level: ApronLevel | None = None,
    season: str | None = None,
    roster: int | None = None,
    constants: SeasonConstants | None = None,
    with_unlikely_incentives: bool = False,
    **kwargs,
) -> Team:
    """Build a plausible roster sitting at a chosen apron tier."""
    season = season or rng.choice(list(SEASONS))
    k = constants or get_season(season)
    level = level or rng.choice(list(ApronLevel))
    roster = roster or rng.randint(13, 15)

    bands = {
        ApronLevel.UNDER_TAX: (int(k.cap * 0.88), k.tax_line - 1_000_000),
        ApronLevel.OVER_TAX: (k.tax_line + 500_000, k.first_apron - 500_000),
        ApronLevel.OVER_FIRST_APRON: (k.first_apron + 500_000, k.second_apron - 500_000),
        ApronLevel.OVER_SECOND_APRON: (k.second_apron + 500_000, k.second_apron + 25_000_000),
    }
    low, high = bands[level]
    target = rng.randint(low, high)

    unlikely_total = 0
    if with_unlikely_incentives:
        unlikely_total = rng.randrange(1_000_000, 7_000_000, 100_000)
        target -= unlikely_total

    salaries = _salary_ladder(rng, target, roster, k)
    contracts = [
        Contract(
            player=player_name(rng),
            salary=salary,
            years_remaining=rng.randint(1, 4),
        )
        for salary in salaries
    ]

    if unlikely_total:
        # Spread the incentives across two or three deals, as real cap sheets do.
        holders = rng.sample(contracts, k=min(3, len(contracts)))
        per = unlikely_total // len(holders)
        for c in holders[:-1]:
            c.incentives_unlikely = per
        holders[-1].incentives_unlikely = unlikely_total - per * (len(holders) - 1)

    team = Team(
        name=f"{rng.choice(CITIES)}",
        season=season,
        contracts=contracts,
        constants_override=constants,
        **kwargs,
    )
    return team


# -- scenario samplers -------------------------------------------------------------------


def trade_legality(rng: random.Random) -> Scenario:
    """The largest slice: is this trade legal for this team?"""
    level = rng.choice(list(ApronLevel))
    team = random_team(rng, level=level)
    k = team.constants

    # Aim for a roughly even split of legal and illegal trades. An unbalanced set teaches a
    # prior rather than a rule -- a model fed mostly rejections learns to reject. The engine
    # still decides the actual verdict; this only steers where the proposal lands.
    aim_legal = rng.random() < 0.5

    # Aggregating is itself illegal over the second apron, so only reach for it when the
    # scenario is meant to fail there.
    if level is ApronLevel.OVER_SECOND_APRON:
        aggregate = not aim_legal and rng.random() < 0.7
    else:
        aggregate = rng.random() < 0.35

    tradeable = [c for c in team.contracts if c.salary > k.minimum_salary(2)]
    if len(tradeable) < 2:
        tradeable = team.contracts
    sending = rng.sample(tradeable, k=2 if aggregate and len(tradeable) >= 2 else 1)
    outgoing = sum(c.salary for c in sending)

    # Land near the legal boundary either way, so the dataset is full of close calls rather
    # than obvious answers.
    if team.is_over_first_apron:
        ceiling = outgoing
    else:
        from capengine.trade import max_incoming_expanded

        ceiling, _ = max_incoming_expanded(outgoing, k)
    span = rng.uniform(0.72, 0.99) if aim_legal else rng.uniform(1.02, 1.30)
    incoming_salary = int(ceiling * span)

    incoming = [Contract(player=player_name(rng), salary=incoming_salary,
                         years_remaining=rng.randint(1, 4))]
    side = TradeSide(team=team, sending=[c.player for c in sending], receiving=incoming)
    result = evaluate_trade([side])

    names = " and ".join(c.player for c in sending)
    question = (
        f"We're discussing a trade that sends {names} to another team for "
        f"{incoming[0].player} at {usd(incoming_salary)}. Is that legal for us, "
        "and what does it do to our cap situation?"
    )

    facts = {
        "legal": result.legal,
        "outgoing_salary": result.sides[0].outgoing_salary,
        "incoming_salary": result.sides[0].incoming_salary,
        "max_incoming": result.sides[0].max_incoming,
        "matching_rule": result.sides[0].matching_rule,
        "apron_level": team.apron_level.value,
        "apron_salary_after": result.sides[0].apron_salary_after,
        "hard_cap_triggered": result.sides[0].hard_cap_triggered.value,
        "violations": [str(v) for v in result.violations],
    }
    required = [outgoing, incoming_salary, result.sides[0].max_incoming]

    return Scenario(
        kind="trade_legality",
        context=team_context(team, rng),
        question=question,
        answer_facts=facts,
        trace=result.trace,
        required_values=required,
        verdict=result.verdict,
        season=team.season,
    )


def tax_bill(rng: random.Random) -> Scenario:
    level = rng.choice([ApronLevel.OVER_TAX, ApronLevel.OVER_FIRST_APRON,
                        ApronLevel.OVER_SECOND_APRON])
    repeater = rng.random() < 0.5
    team = random_team(rng, level=level, is_repeater=repeater)
    result = compute_tax(team)

    question = rng.choice([
        "What's our luxury tax bill this season? Walk me through the brackets.",
        "Ownership wants the tax number. What do we owe, and how does it break down?",
        "How much tax are we paying at this payroll?",
    ])

    facts = {
        "tax_salary": result.tax_salary,
        "tax_line": result.tax_line,
        "amount_over": result.amount_over,
        "is_repeater": result.is_repeater,
        "total": result.total,
        "brackets": [
            {"index": b.index + 1, "amount": b.amount, "rate": b.rate, "owed": b.owed}
            for b in result.brackets
        ],
    }
    return Scenario(
        kind="tax_bill",
        context=team_context(team, rng),
        question=question,
        answer_facts=facts,
        trace=result.trace,
        required_values=[result.total, result.amount_over],
        season=team.season,
    )


def exception_eligibility(rng: random.Random) -> Scenario:
    team = random_team(rng, level=rng.choice(list(ApronLevel)))
    k = team.constants

    # Half the time, ask about an exception the team actually has -- otherwise every
    # apron-team example is a refusal and the model learns to refuse rather than to check.
    aim_legal = rng.random() < 0.5
    usable = [
        s.exception
        for s in available_exceptions(team)
        if s.available and s.exception is not ExceptionType.ROOM
    ]
    candidates = [
        ExceptionType.NON_TAXPAYER_MLE,
        ExceptionType.TAXPAYER_MLE,
        ExceptionType.BI_ANNUAL,
        ExceptionType.MINIMUM,
    ]
    exception = rng.choice(usable) if aim_legal and usable else rng.choice(candidates)

    reference = {
        ExceptionType.NON_TAXPAYER_MLE: k.non_taxpayer_mle,
        ExceptionType.TAXPAYER_MLE: k.taxpayer_mle,
        ExceptionType.BI_ANNUAL: k.bi_annual_exception or 5_000_000,
        ExceptionType.MINIMUM: k.minimum_salary(rng.randint(0, 10)),
    }[exception]
    salary = int(reference * (rng.uniform(0.6, 0.98) if aim_legal else rng.uniform(0.8, 1.25)))

    player = player_name(rng)
    result = evaluate_signing(team, salary, exception, player=player)

    question = (
        f"Can we sign {player} for {usd(salary)} using the {exception.value}? "
        "If it works, tell me what it costs us in flexibility."
    )
    facts = {
        "legal": result.legal,
        "exception": exception.value,
        "salary": salary,
        "hard_cap_triggered": result.hard_cap_triggered.value,
        "apron_level": team.apron_level.value,
        "apron_salary_after": result.apron_salary_after,
        "reasons": result.reasons,
    }
    return Scenario(
        kind="exception_eligibility",
        context=team_context(team, rng),
        question=question,
        answer_facts=facts,
        trace=result.trace,
        required_values=[salary],
        verdict=result.verdict,
        season=team.season,
    )


def exception_survey(rng: random.Random) -> Scenario:
    """What tools does this team still have? A staple front-office question."""
    team = random_team(rng, level=rng.choice(list(ApronLevel)))
    statuses = available_exceptions(team)
    trace = Trace()
    trace.add(f"{team.name} apron salary", team.apron_salary, detail=team.apron_level.value)
    k = team.constants
    trace.add(f"{k.season} first apron", k.first_apron)
    trace.add(f"{k.season} second apron", k.second_apron)
    for s in statuses:
        trace.add(
            f"{s.exception.value}: {'available' if s.available else 'unavailable'}",
            s.amount,
            detail=s.reason,
        )

    question = rng.choice([
        "What signing exceptions do we still have available, and what does using each one cost us?",
        "Run me through our tools in free agency this summer.",
        "Which exceptions can we actually use at this payroll?",
    ])
    facts = {
        "apron_level": team.apron_level.value,
        "exceptions": [
            {
                "name": s.exception.value,
                "available": s.available,
                "amount": s.amount,
                "reason": s.reason,
                "hard_cap": s.hard_cap_triggered.value,
            }
            for s in statuses
        ],
    }
    return Scenario(
        kind="exception_survey",
        context=team_context(team, rng),
        question=question,
        answer_facts=facts,
        trace=trace,
        season=team.season,
    )


def apron_status(rng: random.Random) -> Scenario:
    """Where do we sit -- including the unlikely-incentive trap."""
    with_incentives = rng.random() < 0.6
    team = random_team(
        rng,
        level=rng.choice(list(ApronLevel)),
        with_unlikely_incentives=with_incentives,
    )
    k = team.constants
    trace = Trace()
    trace.add(f"{team.name} salaries plus likely incentives", team.tax_salary)
    if team.unlikely_incentives:
        trace.add("Unlikely incentives", team.unlikely_incentives,
                  detail="counts toward apron salary only, not cap or tax salary")
    trace.add("Apron salary", team.apron_salary)
    trace.add(f"{k.season} luxury tax line", k.tax_line)
    trace.add(f"{k.season} first apron", k.first_apron)
    trace.add(f"{k.season} second apron", k.second_apron)
    trace.add(f"Position: {team.apron_level.value}")
    for label, threshold in (
        ("tax line", k.tax_line),
        ("first apron", k.first_apron),
        ("second apron", k.second_apron),
    ):
        room = threshold - team.apron_salary
        trace.add(
            f"{'Room below' if room >= 0 else 'Amount above'} the {label}",
            abs(room),
        )

    question = rng.choice([
        "Where do we sit relative to the tax and the aprons right now?",
        "Are we over the second apron? How much room do we have?",
        "Give me our apron position and what it means for the rest of the offseason.",
    ])
    facts = {
        "tax_salary": team.tax_salary,
        "unlikely_incentives": team.unlikely_incentives,
        "apron_salary": team.apron_salary,
        "apron_level": team.apron_level.value,
        "room_to_first_apron": k.first_apron - team.apron_salary,
        "room_to_second_apron": k.second_apron - team.apron_salary,
    }
    return Scenario(
        kind="apron_status",
        context=team_context(team, rng),
        question=question,
        answer_facts=facts,
        trace=trace,
        required_values=[team.apron_salary],
        season=team.season,
    )


def stretch_provision(rng: random.Random) -> Scenario:
    team = random_team(rng, level=rng.choice(list(ApronLevel)))
    k = team.constants
    years = rng.randint(1, 3)
    remaining = rng.randrange(20_000_000, 120_000_000, 100_000)
    existing = rng.choice([0, rng.randrange(1_000_000, 16_000_000, 100_000)])
    player = player_name(rng)

    result = compute_stretch(team, remaining, years, existing)
    question = (
        f"If we waive and stretch {player} -- {usd(remaining)} left over {years} "
        f"{'year' if years == 1 else 'years'} -- what does the dead money look like, "
        "and is it even allowed?"
    )
    facts = {
        "legal": result.legal,
        "remaining_salary": remaining,
        "years_remaining": years,
        "stretch_years": result.stretch_years,
        "annual_dead_money": result.annual_dead_money,
        "existing_stretched": existing,
        "limit": result.limit,
        "givebacks_required": result.givebacks_required,
        "reason": result.reason,
    }
    return Scenario(
        kind="stretch_provision",
        context=constants_block(k),
        question=question,
        answer_facts=facts,
        trace=result.trace,
        required_values=[result.annual_dead_money, result.limit],
        verdict="LEGAL" if result.legal else "ILLEGAL",
        season=team.season,
    )


def buyout_market(rng: random.Random) -> Scenario:
    team = random_team(rng, level=rng.choice(list(ApronLevel)))
    k = team.constants
    pre_waiver = rng.randrange(3_000_000, 45_000_000, 100_000)
    player = player_name(rng)
    result = can_sign_buyout_player(team, pre_waiver)

    question = (
        f"{player} is about to be bought out -- he was making {usd(pre_waiver)} "
        "before the waiver. Can we sign him?"
    )
    facts = {
        "allowed": result.allowed,
        "pre_waiver_salary": pre_waiver,
        "non_taxpayer_mle": k.non_taxpayer_mle,
        "apron_level": team.apron_level.value,
        "reason": result.reason,
    }
    return Scenario(
        kind="buyout_market",
        context=team_context(team, rng),
        question=question,
        answer_facts=facts,
        trace=result.trace,
        required_values=[pre_waiver, k.non_taxpayer_mle],
        verdict="ALLOWED" if result.allowed else "NOT ALLOWED",
        season=team.season,
    )


def draft_penalty(rng: random.Random) -> Scenario:
    level = rng.choice([ApronLevel.OVER_FIRST_APRON, ApronLevel.OVER_SECOND_APRON,
                        ApronLevel.OVER_SECOND_APRON])
    seasons_over = rng.randint(0, 4)
    team = random_team(rng, level=level, seasons_over_second_apron=seasons_over)
    draft_year = int(team.season[:4])
    result = draft_penalties(team, current_draft_year=draft_year)

    question = (
        "If we finish the season at this payroll, what happens to our draft picks?"
        + (f" We've been over the second apron in {seasons_over} of the last five seasons."
           if seasons_over else "")
    )
    facts = {
        "pick_frozen": result.pick_frozen,
        "frozen_draft_year": result.frozen_draft_year,
        "pick_demoted": result.pick_demoted,
        "seasons_over": seasons_over,
        "reason": result.reason,
    }
    return Scenario(
        kind="draft_penalty",
        context=team_context(team, rng),
        question=question,
        answer_facts=facts,
        trace=result.trace,
        season=team.season,
    )


def anti_staleness(rng: random.Random) -> Scenario:
    """Pasted thresholds that differ from any real season -- the model must read, not recall.

    This is the slice that protects against the model's single most likely failure: answering
    from a memorized 2026-27 cap sheet after the numbers have moved. The scenario invents a
    future league year, and the ground truth is computed from the invented figures. An answer
    that quotes a real threshold is wrong by construction.
    """
    base = get_season(rng.choice(list(SEASONS)))
    growth = rng.uniform(1.03, 1.10)

    def bump(value: int) -> int:
        return int(round(value * growth / 1000) * 1000)

    season_label = rng.choice(["2027-28", "2028-29", "2029-30"])
    hypothetical = SeasonConstants(
        season=season_label,
        cap=bump(base.cap),
        tax_line=bump(base.tax_line),
        first_apron=bump(base.first_apron),
        second_apron=bump(base.second_apron),
        non_taxpayer_mle=bump(base.non_taxpayer_mle),
        taxpayer_mle=bump(base.taxpayer_mle),
        room_exception=bump(base.room_exception),
        tax_bracket_width=bump(base.tax_bracket_width),
        min_team_salary=bump(base.min_team_salary),
        bi_annual_exception=bump(base.bi_annual_exception or 5_000_000),
        min_scale={yos: bump(v) for yos, v in base.min_scale.items()},
    )

    team = random_team(
        rng,
        level=rng.choice([ApronLevel.OVER_TAX, ApronLevel.OVER_FIRST_APRON,
                          ApronLevel.OVER_SECOND_APRON]),
        season=season_label,
        constants=hypothetical,
    )

    # Confirm the pasted figures actually change the answer; otherwise the example proves
    # nothing about whether the model read them.
    shadow = Team(
        name=team.name,
        season=base.season,
        contracts=team.contracts,
        constants_override=base,
    )
    if shadow.apron_level is team.apron_level:
        return anti_staleness(rng)

    trace = Trace()
    trace.add(f"{team.name} apron salary", team.apron_salary)
    trace.add(f"{season_label} first apron (from the figures provided)",
              hypothetical.first_apron)
    trace.add(f"{season_label} second apron (from the figures provided)",
              hypothetical.second_apron)
    trace.add(f"Position: {team.apron_level.value}")
    trace.add("Room below the second apron",
              hypothetical.second_apron - team.apron_salary)

    question = (
        f"Using the {season_label} thresholds above, where does this payroll put us, "
        "and which restrictions apply?"
    )
    facts = {
        "season": season_label,
        "apron_salary": team.apron_salary,
        "apron_level": team.apron_level.value,
        "first_apron_provided": hypothetical.first_apron,
        "second_apron_provided": hypothetical.second_apron,
        "would_be_wrong_using_published_figures": shadow.apron_level.value,
        "note": (
            "The thresholds in the prompt are the only valid source. Answering from any "
            "memorized season's figures gives the wrong tier here."
        ),
    }
    return Scenario(
        kind="anti_staleness",
        context=team_context(team, rng),
        question=question,
        answer_facts=facts,
        trace=trace,
        required_values=[team.apron_salary, hypothetical.second_apron],
        season=season_label,
        notes="pasted-figures-must-win",
    )


def scenario_planning(rng: random.Random) -> Scenario:
    """The hardest slice: get under a threshold, and say what it costs."""
    team = random_team(rng, level=ApronLevel.OVER_SECOND_APRON, roster=15)
    k = team.constants
    target = k.second_apron
    overage = team.apron_salary - target

    # Which single salaries would clear the gap on their own?
    candidates = sorted(
        (c for c in team.contracts if c.salary > overage),
        key=lambda c: c.salary,
    )

    trace = Trace()
    trace.add(f"{team.name} apron salary", team.apron_salary)
    trace.add(f"{k.season} second apron", target)
    trace.add("Amount over the second apron", overage)
    trace.add(
        "Aggregation unavailable",
        detail="over the second apron, salaries cannot be combined in a trade",
    )
    trace.add("Cash unavailable", detail="over the second apron, no cash may be sent")
    for c in candidates[:4]:
        trace.add(
            f"Moving {c.player} alone clears the gap",
            c.salary - overage,
            detail=f"{usd(c.salary)} out against {usd(overage)} of overage, "
            "assuming no salary comes back",
        )
    if not candidates:
        trace.add(
            "No single salary clears the gap",
            detail="every contract on the sheet is smaller than the overage, and "
            "aggregation is banned over the second apron",
        )

    question = rng.choice([
        ("We need to get under the second apron before the deadline. What are our options, "
         "and what are we giving up?"),
        "Ownership wants us out of the second apron. Walk me through how we do it.",
        "What's the cleanest path under the second apron from here?",
    ])
    facts = {
        "apron_salary": team.apron_salary,
        "second_apron": target,
        "overage": overage,
        "aggregation_banned": True,
        "cash_banned": True,
        "single_salary_solutions": [
            {"player": c.player, "salary": c.salary, "surplus": c.salary - overage}
            for c in candidates[:4]
        ],
    }
    return Scenario(
        kind="scenario_planning",
        context=team_context(team, rng),
        question=question,
        answer_facts=facts,
        trace=trace,
        required_values=[overage],
        season=team.season,
    )


def hard_cap_consequence(rng: random.Random) -> Scenario:
    """A team already hard-capped tries another move."""
    hard_cap = rng.choice([HardCap.FIRST_APRON, HardCap.SECOND_APRON])
    level = (
        ApronLevel.OVER_TAX if hard_cap is HardCap.FIRST_APRON else ApronLevel.OVER_FIRST_APRON
    )
    team = random_team(rng, level=level, hard_cap=hard_cap)
    limit = team.hard_cap_limit
    room = limit - team.apron_salary

    salary = int(max(room, 1) * rng.uniform(0.45, 1.45))
    player = player_name(rng)
    result = evaluate_signing(team, salary, ExceptionType.MINIMUM, player=player)

    question = (
        f"We're hard-capped at the {hard_cap.value}. Can we add {player} at {usd(salary)}?"
    )
    facts = {
        "legal": result.legal,
        "hard_cap": hard_cap.value,
        "hard_cap_limit": limit,
        "room_below_hard_cap": room,
        "salary": salary,
        "apron_salary_after": result.apron_salary_after,
        "reasons": result.reasons,
    }
    return Scenario(
        kind="hard_cap_consequence",
        context=team_context(team, rng),
        question=question,
        answer_facts=facts,
        trace=result.trace,
        required_values=[salary, limit],
        verdict=result.verdict,
        season=team.season,
    )


# -- taxonomy ------------------------------------------------------------------------------

SAMPLERS = {
    "trade_legality": trade_legality,
    "tax_bill": tax_bill,
    "exception_eligibility": exception_eligibility,
    "exception_survey": exception_survey,
    "apron_status": apron_status,
    "stretch_provision": stretch_provision,
    "buyout_market": buyout_market,
    "draft_penalty": draft_penalty,
    "anti_staleness": anti_staleness,
    "scenario_planning": scenario_planning,
    "hard_cap_consequence": hard_cap_consequence,
}

# Target mix. Trade legality dominates because it is the core capability and has the widest
# space of distinct situations; anti-staleness is deliberately heavy because it defends the
# model's single biggest failure mode.
MIX = {
    "trade_legality": 0.24,
    "apron_status": 0.12,
    "anti_staleness": 0.12,
    "exception_eligibility": 0.10,
    "tax_bill": 0.09,
    "exception_survey": 0.08,
    "scenario_planning": 0.07,
    "hard_cap_consequence": 0.06,
    "stretch_provision": 0.05,
    "buyout_market": 0.04,
    "draft_penalty": 0.03,
}


def sample(rng: random.Random, kind: str | None = None) -> Scenario:
    if kind is None:
        kinds = list(MIX)
        weights = [MIX[k] for k in kinds]
        kind = rng.choices(kinds, weights=weights, k=1)[0]
    return SAMPLERS[kind](rng)
