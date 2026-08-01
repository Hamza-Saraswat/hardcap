"""Turning computation traces into prose, without a language model.

CapEngine already knows the answer and every figure behind it. What it lacks is a voice.
This module supplies one from templates -- free, instant, and correct by construction, since
it can only ever restate numbers the engine computed.

The tradeoff is honest: templated prose is less varied than a frontier model's, and a model
trained only on this will sound a little mechanical. What it will *not* be is wrong, and the
reasoning it learns is identical either way. Mix in genuinely-written examples for variety;
the correctness comes from here.

Every narrator's output must survive datagen.verify unchanged. Two constraints follow:
figures appear only if the trace contains them, and on a LEGAL verdict no negation word may
appear early, since the verdict checker reads the opening of the answer.
"""

from __future__ import annotations

import random

from capengine.trace import usd
from datagen.scenarios import Scenario

# -- phrase banks -------------------------------------------------------------------------

_LEGAL_OPENERS = [
    "This one works.",
    "The money works here.",
    "We can do this.",
    "This clears.",
    "It fits.",
    "This is fine as constructed.",
]

_ILLEGAL_OPENERS = [
    "This does not work as constructed.",
    "We have a problem here.",
    "This one dies on the salary.",
    "This is a non-starter as written.",
    "The structure fails.",
    "This one is dead as drawn up.",
]

_CLOSERS_LEGAL = [
    "Worth walking ownership through the consequences before we sign off.",
    "I would move on it, with eyes open about what it costs us later.",
    "The math is clean. The flexibility question is the real one.",
    "No obstacle on the cap side.",
]

_CLOSERS_ILLEGAL = [
    "We would need to restructure this before it goes to the league office.",
    "Find another construction or another partner.",
    "Bring me a different framework and I will run it again.",
    "As drawn, the league would reject it.",
]


def _pick(rng: random.Random, options: list[str]) -> str:
    return rng.choice(options)


def _verdict_line(rng: random.Random, legal: bool) -> str:
    label = "LEGAL" if legal else "ILLEGAL"
    opener = _pick(rng, _LEGAL_OPENERS if legal else _ILLEGAL_OPENERS)
    return f"**Verdict: {label}.** {opener}"


# -- narrators ----------------------------------------------------------------------------


def _matching_rule_phrase(rule: str) -> str:
    """Drop the engine's parenthetical, which restates the tier we just named.

    Without this a second-apron team reads "Sitting over the second apron ... under 100% of
    outgoing salary (team is over the first apron)" -- both true, but jarring together.
    """
    return rule.split(" (")[0].strip()


def _trade_legality(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    legal = f["legal"]
    parts = [_verdict_line(rng, legal)]

    parts.append(
        f"We send out {usd(f['outgoing_salary'])} and take back "
        f"{usd(f['incoming_salary'])}."
    )
    parts.append(
        f"Sitting {f['apron_level']}, our matching limit is "
        f"{usd(f['max_incoming'])} under {_matching_rule_phrase(f['matching_rule'])}."
    )

    if legal:
        parts.append(
            f"The incoming salary lands inside that, so the money is fine. "
            f"After the deal we sit at {usd(f['apron_salary_after'])}."
        )
        if f["hard_cap_triggered"] != "none":
            parts.append(
                f"The cost is flexibility: this hard-caps us at the "
                f"{f['hard_cap_triggered']} for the rest of the league year, and every "
                "move after it has to respect that ceiling."
            )
        parts.append(_pick(rng, _CLOSERS_LEGAL))
    else:
        overage = f["incoming_salary"] - f["max_incoming"]
        for violation in f["violations"]:
            rule = violation.split(": ", 1)[-1].split(" -- ")[0]
            if rule == "salary matching":
                parts.append(
                    f"That is {usd(overage)} more than we are allowed to absorb, and "
                    "there is no exception that closes a gap that size."
                )
            else:
                # Restate the engine's own explanation for anything the matching sentence
                # above does not already cover.
                parts.append(violation.split(" -- ", 1)[-1].rstrip(".") + ".")
        # The hard-cap violation already quotes the post-trade figure; repeating it reads
        # like padding.
        already_stated = any("hard cap" in v for v in f["violations"])
        if not already_stated:
            parts.append(
                f"Had it gone through we would have been at {usd(f['apron_salary_after'])}."
            )
        parts.append(_pick(rng, _CLOSERS_ILLEGAL))

    return " ".join(parts)


def _tax_bill(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    if f["amount_over"] == 0:
        return (
            f"We are not a taxpayer this season. Team salary sits at "
            f"{usd(f['tax_salary'])} against a tax line of {usd(f['tax_line'])}, so we owe "
            "nothing and we keep our share of the distribution paid out to non-taxpaying "
            "teams. That is real money most people forget to count."
        )

    parts = [
        f"We owe {usd(f['total'])}.",
        (f"Team salary is {usd(f['tax_salary'])} against a tax line of "
         f"{usd(f['tax_line'])}, which puts us {usd(f['amount_over'])} into the tax."),
    ]

    schedule = "repeater" if f["is_repeater"] else "standard"
    parts.append(f"That is assessed in brackets on the {schedule} schedule.")

    brackets = [
        f"{'The first' if b['index'] == 1 else 'The next'} {usd(b['amount'])} is taxed at "
        f"${b['rate']:.2f} per dollar, which costs us {usd(b['owed'])}."
        for b in f["brackets"]
    ]
    parts.extend(brackets)
    parts.append(f"That adds up to {usd(f['total'])}.")

    if f["is_repeater"]:
        parts.append(
            "Repeater status is what makes this brutal -- having paid the tax in three of "
            "the last four seasons, we start at a far steeper rate than a first-time "
            "payer would."
        )
    parts.append(
        "We also forfeit our share of the distribution that goes to non-taxpaying teams."
    )
    return " ".join(parts)


def _exception_eligibility(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    legal = f["legal"]
    parts = [_verdict_line(rng, legal)]

    if legal:
        parts.append(
            f"The {f['exception']} covers {usd(f['salary'])}, and we are "
            f"{f['apron_level']}, which keeps that tool available to us."
        )
        parts.append(f"The signing puts us at {usd(f['apron_salary_after'])}.")
        if f["hard_cap_triggered"] != "none":
            parts.append(
                f"Using it hard-caps us at the {f['hard_cap_triggered']} through June 30. "
                "Everything else we want to do this year has to fit under that."
            )
        parts.append(_pick(rng, _CLOSERS_LEGAL))
    else:
        parts.append(
            f"He is asking {usd(f['salary'])}, and we would be signing him with the "
            f"{f['exception']}."
        )
        for reason in f["reasons"]:
            parts.append(reason[0].upper() + reason[1:] + ".")
        parts.append(
            f"We are {f['apron_level']}, and that is what governs here."
        )
        parts.append(_pick(rng, _CLOSERS_ILLEGAL))

    return " ".join(parts)


def _exception_survey(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    parts = [f"We are {f['apron_level']}. Here is what that leaves us."]

    available = [e for e in f["exceptions"] if e["available"]]
    gone = [e for e in f["exceptions"] if not e["available"]]

    for exception in available:
        amount = f" at {usd(exception['amount'])}" if exception["amount"] else ""
        line = f"The {exception['name']} is available{amount}."
        if exception["hard_cap"] != "none":
            line += f" Using it hard-caps us at the {exception['hard_cap']}."
        parts.append(line)

    for exception in gone:
        parts.append(f"The {exception['name']} is out -- {exception['reason']}.")

    parts.append(
        "In practice that means we build the back of the roster with minimums and our own "
        "free agents, and every dollar we add has to be worth what it forecloses."
    )
    return " ".join(parts)


def _apron_status(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    parts = [f"We are {f['apron_level']}, at {usd(f['apron_salary'])}."]

    if f["unlikely_incentives"]:
        parts.append(
            f"Worth being precise about that figure: salaries and likely incentives come "
            f"to {usd(f['tax_salary'])}, but {usd(f['unlikely_incentives'])} in unlikely "
            "incentives counts toward apron salary even though it does not count toward "
            "the cap or the tax. That gap catches people out."
        )

    room_first = f["room_to_first_apron"]
    room_second = f["room_to_second_apron"]

    parts.append(
        f"We have {usd(abs(room_first))} "
        + ("of room below the first apron." if room_first >= 0
           else "of space above the first apron.")
    )
    parts.append(
        f"Against the second apron it is {usd(abs(room_second))} "
        + ("of room." if room_second >= 0 else "over.")
    )

    if room_second < 0:
        parts.append(
            "That is the line that matters. Over the second apron we lose aggregation in "
            "trades, we lose the ability to send cash, we lose every mid-level exception, "
            "and finishing the season here freezes a first-round pick seven drafts out."
        )
    elif room_first < 0:
        parts.append(
            "Over the first apron we are limited to matching 100% of outgoing salary in "
            "trades, the full mid-level and bi-annual are gone, and we are shut out of the "
            "buyout market for anyone who was earning above the non-taxpayer mid-level."
        )
    else:
        parts.append(
            "We still have the full toolkit here. The question is which of it we want to "
            "spend, since most of these tools hard-cap us the moment we use them."
        )
    return " ".join(parts)


def _stretch_provision(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    legal = f["legal"]
    parts = [_verdict_line(rng, legal)]

    parts.append(
        f"He has {usd(f['remaining_salary'])} left over {f['years_remaining']} "
        f"{'year' if f['years_remaining'] == 1 else 'years'}, which stretches over "
        f"{f['stretch_years']} seasons at {usd(f['annual_dead_money'])} a year in dead money."
    )

    if f["existing_stretched"]:
        parts.append(
            f"We are already carrying {usd(f['existing_stretched'])} in stretched money "
            "from earlier waivers, and the two stack."
        )

    parts.append(
        f"The ceiling is {usd(f['limit'])} -- fifteen percent of the cap in any one season."
    )

    if legal:
        parts.append("We land inside it, so the waiver processes as structured.")
        parts.append(
            "Dead money is still dead money, though. That figure sits on our books every "
            "season of the stretch whether he plays a minute for us or not."
        )
    else:
        parts.append(
            f"We would need {usd(f['givebacks_required'])} back from him to get under it, "
            "which turns a cap question into a negotiation."
        )
        parts.append(_pick(rng, _CLOSERS_ILLEGAL))

    return " ".join(parts)


def _buyout_market(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    allowed = f["allowed"]
    label = "LEGAL" if allowed else "ILLEGAL"
    opener = "We can sign him." if allowed else "He is off limits to us."
    parts = [f"**Verdict: {label}.** {opener}"]

    parts.append(
        f"He was earning {usd(f['pre_waiver_salary'])} before the waiver, against a "
        f"non-taxpayer mid-level of {usd(f['non_taxpayer_mle'])}."
    )
    parts.append(f"We are {f['apron_level']}.")

    if allowed:
        parts.append(
            "The buyout restriction does not reach this one, so he is available to us at "
            "the minimum like anyone else on the market."
        )
    else:
        parts.append(
            "Over the first apron we are barred from signing anyone waived during the "
            "regular season who was earning more than the non-taxpayer mid-level before "
            "the waiver. This is the rule that hands every good buyout to teams under the "
            "line, and there is no exception to it."
        )
    return " ".join(parts)


def _draft_penalty(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    if not f["pick_frozen"]:
        return (
            "Nothing happens to our picks. The draft penalties attach only to teams that "
            "finish a season over the second apron, and we are below it. Worth keeping in "
            "mind as we look at additions, because crossing that line late in the year "
            "carries a cost that lands seven drafts from now."
        )

    parts = [
        (
            f"Finishing here freezes our {f['frozen_draft_year']} first-round pick. It "
            "becomes untradeable, and it stays that way until we finish below the second "
            "apron in three of the following four seasons."
        )
    ]
    if f["pick_demoted"]:
        parts.append(
            f"Worse than that: we have now been over the second apron in "
            f"{f['seasons_over']} of five seasons, which triggers the second penalty. That "
            "pick does not just freeze, it moves to the end of the first round regardless "
            "of our record."
        )
    else:
        parts.append(
            "The demotion penalty has not triggered yet. If we finish over the second "
            "apron in three of five seasons, that frozen pick slides to the end of the "
            "first round no matter how badly we finish."
        )
    return " ".join(parts)


def _anti_staleness(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    parts = [
        (
            f"Working from the {f['season']} figures you have given me, we are at "
            f"{usd(f['apron_salary'])}, which puts us {f['apron_level']}."
        )
    ]
    parts.append(
        f"Against a first apron of {usd(f['first_apron_provided'])} and a second apron of "
        f"{usd(f['second_apron_provided'])}, that is where the payroll falls."
    )

    if "over the second apron" in f["apron_level"]:
        parts.append(
            "That is the hard tier. No aggregating salaries in trades, no cash in either "
            "direction, no mid-level of any kind, and a first-round pick freezes if we "
            "finish the season here."
        )
    elif "over the first apron" in f["apron_level"]:
        parts.append(
            "At this tier we match 100% of outgoing salary in trades and nothing more, the "
            "full mid-level and the bi-annual are both gone, and the buyout market closes "
            "to us for anyone above the non-taxpayer mid-level."
        )
    else:
        parts.append(
            "We are in the tax but below the aprons, so the restrictions have not bitten "
            "yet. It costs money, not flexibility."
        )

    parts.append(
        "One caution: these thresholds move every July, and they do not move predictably. "
        "I am working from the numbers in front of me rather than any figure I might "
        "remember from a prior season, and you should hold me to that."
    )
    return " ".join(parts)


def _scenario_planning(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    parts = [
        (
            f"We are {usd(f['overage'])} over the second apron, at "
            f"{usd(f['apron_salary'])} against a line of {usd(f['second_apron'])}."
        )
    ]
    parts.append(
        "Start with what is closed to us. Over the second apron we cannot combine two "
        "salaries into one trade, and we cannot send cash. That rules out most of the "
        "constructions that would normally solve this, and it means every solution is a "
        "single salary going out."
    )

    solutions = f["single_salary_solutions"]
    if solutions:
        parts.append("Salaries large enough to clear the gap on their own:")
        for solution in solutions:
            parts.append(
                f"{solution['player']} at {usd(solution['salary'])} clears it with "
                f"{usd(solution['surplus'])} to spare."
            )
        parts.append(
            "Any of those gets us under, assuming nothing comes back. That assumption is "
            "the hard part -- we need a partner with room to absorb the salary outright, "
            "and they will want something for the favor. Draft compensation is the usual "
            "price."
        )
    else:
        parts.append(
            "No single contract on this sheet is large enough to clear the gap by itself, "
            "and aggregation is exactly what we are barred from. That leaves finding a "
            "partner to absorb one salary and take a second in a separate transaction, "
            "which means two deals and two sets of compensation."
        )

    parts.append(
        "The alternative is finishing the season here and accepting the pick freeze. That "
        "is a real option if the roster is good enough, and a bad one if it is not."
    )
    return " ".join(parts)


def _hard_cap_consequence(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    legal = f["legal"]
    parts = [_verdict_line(rng, legal)]

    parts.append(
        f"Our hard cap sits at {usd(f['hard_cap_limit'])} and we have "
        f"{usd(f['room_below_hard_cap'])} of room beneath it."
    )
    parts.append(f"He costs {usd(f['salary'])}.")

    if legal:
        parts.append(
            f"That fits, leaving us at {usd(f['apron_salary_after'])}. "
            "A hard cap is absolute, so I would rather bank the remaining room than spend "
            "it now unless he genuinely moves the rotation."
        )
    else:
        for reason in f["reasons"]:
            parts.append(reason[0].upper() + reason[1:] + ".")
        parts.append(
            "A hard cap is not a soft guideline. There is no exception that lets us cross "
            "it, so the only path is clearing salary first."
        )
    return " ".join(parts)


NARRATORS = {
    "trade_legality": _trade_legality,
    "tax_bill": _tax_bill,
    "exception_eligibility": _exception_eligibility,
    "exception_survey": _exception_survey,
    "apron_status": _apron_status,
    "stretch_provision": _stretch_provision,
    "buyout_market": _buyout_market,
    "draft_penalty": _draft_penalty,
    "anti_staleness": _anti_staleness,
    "scenario_planning": _scenario_planning,
    "hard_cap_consequence": _hard_cap_consequence,
}


def narrate(scenario: Scenario, rng: random.Random) -> str:
    """Write the analyst's reply for a scenario, using only figures the engine computed."""
    return NARRATORS[scenario.kind](scenario, rng)
