"""v2 scenario slices, each aimed at a measured failure.

Every generator here exists because `docs/error-analysis-v1.md` pointed at it:

  no_sheet_enumeration  the degenerate loop -- exception surveys were only ever trained with
                        a cap sheet, so the no-context form is out of distribution
  missing_data_request  the same gap's other half: asked about a team with nothing pasted,
                        request the sheet instead of inventing one
  concept_depth         "explain X" answers were coherent but fuzzy at the edges in live use
  tool_arithmetic       chained sums scored 4.7%; hand the multiplication to a calculator
  grounding_discipline  68% of answers invented a figure -- the largest failure bucket, and
                        the one tool use does NOT fix

Ground truth still comes from CapEngine, and everything still passes `datagen.verify`.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from capengine.calc import calc
from capengine.constants import get_season
from capengine.models import ApronLevel
from capengine.signings import available_exceptions
from capengine.tax import compute_tax
from capengine.trace import Trace, usd
from datagen.capsheet import team_context
from datagen.scenarios import Scenario, player_name, random_team


@dataclass
class ToolScenario(Scenario):
    """A scenario whose answer runs through calculator calls before the prose.

    `tool_turns` is the exact call/result sequence the assistant should produce, so the
    training row can be rendered as a real multi-turn tool exchange rather than prose that
    merely mentions arithmetic.
    """

    tool_turns: list[dict] = field(default_factory=list)


# -- the loop fix ---------------------------------------------------------------------------

_ENUM_QUESTIONS = [
    "Which exceptions does a team over the first apron lose, and which does it keep?",
    "What can a second-apron team still do in a trade?",
    "List the restrictions that attach at each apron level.",
    "What tools does a team over the tax line but under the first apron still have?",
    "Which moves trigger a hard cap, and at which level?",
    "What happens to a team's draft picks if it finishes over the second apron?",
]


def no_sheet_enumeration(rng: random.Random) -> Scenario:
    """Enumeration answered from the rules alone, with no cap sheet anywhere.

    The v1 model loops on these because every exception-survey example it saw carried a
    roster. These answers name thresholds only when the question is about a specific
    season, and otherwise stay purely qualitative -- a bounded list with a natural end.
    """
    question = rng.choice(_ENUM_QUESTIONS)
    k = get_season(rng.choice(["2025-26", "2026-27"]))

    trace = Trace()
    trace.add(f"{k.season} first apron", k.first_apron)
    trace.add(f"{k.season} second apron", k.second_apron)
    trace.add(f"{k.season} luxury tax line", k.tax_line)
    trace.add(f"{k.season} non-taxpayer mid-level", k.non_taxpayer_mle)
    trace.add(f"{k.season} taxpayer mid-level", k.taxpayer_mle)
    trace.add("Answer scope", detail="rules only; no team salary figures are in evidence")

    return Scenario(
        kind="no_sheet_enumeration",
        context="",
        question=question,
        answer_facts={
            "season": k.season,
            "first_apron": k.first_apron,
            "second_apron": k.second_apron,
            "no_team_data": True,
            "note": (
                "Answer from the rules. Name a bounded list and stop; do not enumerate "
                "beyond the rules that exist."
            ),
        },
        trace=trace,
        required_values=[],
        season=k.season,
    )


_TEAM_QUESTIONS = [
    "Are we over the second apron right now?",
    "What's our luxury tax bill this season?",
    "Can we absorb a {salary} contract in a trade?",
    "How much room do we have below the first apron?",
    "Which exceptions can we actually use at our current payroll?",
]


def missing_data_request(rng: random.Random) -> Scenario:
    """Asked about a specific team with nothing pasted -- ask for the sheet, do not guess.

    The system prompt already says to request missing figures; v1 had no examples showing
    what that looks like, so the behavior was never reinforced.
    """
    k = get_season(rng.choice(["2025-26", "2026-27"]))
    salary = usd(rng.randrange(5_000_000, 40_000_000, 100_000))
    question = rng.choice(_TEAM_QUESTIONS).format(salary=salary)

    trace = Trace()
    trace.add("No cap sheet provided", detail="team salary is not in evidence")
    trace.add(f"{k.season} first apron", k.first_apron)
    trace.add(f"{k.season} second apron", k.second_apron)
    trace.add(
        "Correct response",
        detail="state which figures are needed and ask for them; do not assume a payroll",
    )

    return Scenario(
        kind="missing_data_request",
        context="",
        question=question,
        answer_facts={
            "season": k.season,
            "must_ask_for": [
                "current team salary including likely incentives",
                "unlikely incentives (they count toward the aprons)",
                "dead money and cap holds",
                "roster count",
            ],
            "must_not": "assume or invent a payroll figure",
        },
        trace=trace,
        required_values=[],
        season=k.season,
    )


# -- tool use -------------------------------------------------------------------------------


def tool_tax_bill(rng: random.Random) -> ToolScenario:
    """A multi-bracket tax bill, computed through the calculator one bracket at a time."""
    level = rng.choice([ApronLevel.OVER_TAX, ApronLevel.OVER_FIRST_APRON,
                        ApronLevel.OVER_SECOND_APRON])
    team = random_team(rng, level=level, is_repeater=rng.random() < 0.5)
    result = compute_tax(team)
    k = team.constants

    turns: list[dict] = []

    # Sum the roster with the tool FIRST. The original version started at the brackets,
    # because CapEngine already knew the payroll -- so the model was taught to delegate the
    # multiplication and then add fifteen contracts in its head. It got that sum wrong by
    # $9,042,040 in evaluation, and since every later figure derives from it, the whole
    # slice scored 0% arithmetic. The hardest arithmetic in the answer has to be a tool call
    # too, not just the tidy part.
    salaries = [c.cap_hit for c in team.contracts]
    if team.dead_money:
        salaries.append(team.dead_money)
    payroll_expression = " + ".join(str(s) for s in salaries)
    payroll = calc(payroll_expression)
    assert round(payroll.value) == result.tax_salary, (
        payroll.value, result.tax_salary
    )
    turns.append({"expression": payroll_expression, "result": payroll.rendered})

    over_expression = f"{result.tax_salary} - {result.tax_line}"
    over = calc(over_expression)
    assert round(over.value) == result.amount_over
    turns.append({"expression": over_expression, "result": over.rendered})

    running: list[str] = []
    for bracket in result.brackets:
        expression = f"{bracket.amount} * {bracket.rate:.2f}"
        computed = calc(expression)
        # The engine rounds each bracket; the tool is exact. Trust the engine and keep the
        # expression honest by asserting they agree once rounded.
        assert round(computed.value) == bracket.owed, (expression, computed.value, bracket.owed)
        turns.append({"expression": expression, "result": computed.rendered})
        running.append(str(bracket.owed))

    if len(running) > 1:
        total_expression = " + ".join(running)
        computed_total = calc(total_expression)
        assert round(computed_total.value) == result.total
        turns.append({"expression": total_expression, "result": computed_total.rendered})

    trace = Trace()
    trace.extend(result.trace)

    return ToolScenario(
        kind="tool_tax_bill",
        context=team_context(team, rng),
        question=rng.choice([
            "What's our luxury tax bill? Show the bracket math.",
            "Ownership wants the tax number with the breakdown.",
            "How much tax do we owe at this payroll?",
        ]),
        answer_facts={
            "total": result.total,
            "amount_over": result.amount_over,
            "is_repeater": result.is_repeater,
            "brackets": [
                {"amount": b.amount, "rate": b.rate, "owed": b.owed} for b in result.brackets
            ],
        },
        trace=trace,
        required_values=[result.total, result.amount_over],
        season=k.season,
        tool_turns=turns,
    )


def tool_matching(rng: random.Random) -> ToolScenario:
    """Salary matching, with the multiplier applied by the calculator."""
    from capengine.trade import max_incoming_expanded

    team = random_team(rng, level=rng.choice([ApronLevel.UNDER_TAX, ApronLevel.OVER_TAX]))
    k = team.constants
    outgoing_contract = rng.choice(
        [c for c in team.contracts if c.salary > k.minimum_salary(2)] or team.contracts
    )
    outgoing = outgoing_contract.salary
    ceiling, rule = max_incoming_expanded(outgoing, k)
    incoming = int(ceiling * rng.uniform(0.8, 1.15))
    player = player_name(rng)

    turns = []
    if outgoing <= k.trade_band_lower:
        expression = f"{outgoing} * 2 + 250000"
    elif outgoing <= k.trade_band_upper:
        expression = f"{outgoing} + {k.trade_band_lower}"
    else:
        expression = f"{outgoing} * 1.25 + 250000"
    computed = calc(expression)
    assert round(computed.value) == ceiling, (expression, computed.value, ceiling)
    turns.append({"expression": expression, "result": computed.rendered})

    difference = f"{incoming} - {ceiling}" if incoming > ceiling else f"{ceiling} - {incoming}"
    turns.append({"expression": difference, "result": calc(difference).rendered})

    trace = Trace()
    trace.add(f"{team.name} outgoing salary", outgoing,
              detail=f"{outgoing_contract.player}")
    trace.add("Incoming salary", incoming, detail=player)
    trace.add("Matching ceiling", ceiling, detail=rule)
    trace.add(
        "Margin" if incoming <= ceiling else "Overage", abs(ceiling - incoming)
    )

    return ToolScenario(
        kind="tool_matching",
        context=team_context(team, rng),
        question=(
            f"If we send out {outgoing_contract.player} at {usd(outgoing)}, can we take back "
            f"{player} at {usd(incoming)}? Show the matching math."
        ),
        answer_facts={
            "legal": incoming <= ceiling,
            "outgoing": outgoing,
            "incoming": incoming,
            "ceiling": ceiling,
            "rule": rule,
        },
        trace=trace,
        required_values=[outgoing, incoming, ceiling],
        verdict="LEGAL" if incoming <= ceiling else "ILLEGAL",
        season=k.season,
        tool_turns=turns,
    )


# -- grounding --------------------------------------------------------------------------------


def grounding_discipline(rng: random.Random) -> Scenario:
    """Questions whose honest answer names few figures, and only provided ones.

    The single largest failure bucket is invented figures, and error analysis showed they
    are mostly not derivable from anything provided -- so the model is reaching for numbers
    it does not have. These examples reward restraint: state the two or three figures the
    sheet supports, then reason qualitatively.
    """
    team = random_team(rng, level=rng.choice(list(ApronLevel)))
    k = team.constants
    statuses = available_exceptions(team)

    trace = Trace()
    trace.add(f"{team.name} apron salary", team.apron_salary)
    trace.add(f"{k.season} first apron", k.first_apron)
    trace.add(f"{k.season} second apron", k.second_apron)
    trace.add(f"Position: {team.apron_level.value}")
    for status in statuses:
        if status.available and status.amount:
            trace.add(f"{status.exception.value} available", status.amount)

    question = rng.choice([
        "Give me the state of play in two sentences. What matters most right now?",
        "If ownership asks one question about our cap position, what's the answer?",
        "What's the single biggest constraint on us this season?",
        "Summarize where we stand without walking through every line.",
    ])

    return Scenario(
        kind="grounding_discipline",
        context=team_context(team, rng),
        question=question,
        answer_facts={
            "apron_salary": team.apron_salary,
            "apron_level": team.apron_level.value,
            "available_exceptions": [
                s.exception.value for s in statuses if s.available
            ],
            "note": (
                "Name only figures present on the sheet or the thresholds block. Reason "
                "qualitatively about everything else."
            ),
        },
        trace=trace,
        required_values=[team.apron_salary],
        season=k.season,
    )


V2_SAMPLERS = {
    "no_sheet_enumeration": no_sheet_enumeration,
    "missing_data_request": missing_data_request,
    "tool_tax_bill": tool_tax_bill,
    "tool_matching": tool_matching,
    "grounding_discipline": grounding_discipline,
}

V2_MIX = {
    "tool_tax_bill": 0.24,
    "tool_matching": 0.20,
    "grounding_discipline": 0.20,
    "no_sheet_enumeration": 0.16,
    "missing_data_request": 0.10,
    "concept_depth": 0.10,
}


def sample_v2(rng: random.Random, kind: str | None = None) -> Scenario:
    if kind is None:
        kinds = [k for k in V2_MIX if k in V2_SAMPLERS]
        weights = [V2_MIX[k] for k in kinds]
        kind = rng.choices(kinds, weights=weights, k=1)[0]
    return V2_SAMPLERS[kind](rng)
