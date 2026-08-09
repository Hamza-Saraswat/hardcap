"""Narrators for the v2 slices, including tool-calling rows.

Tool rows are not prose that mentions arithmetic -- they are real multi-turn exchanges:
assistant emits a `calc` call, a tool message returns the result, and only the final
assistant turn writes the answer. Rendered through the model's own chat template at
training time, this teaches the model to *delegate* the multiplication rather than attempt
it, which is the whole point of adding the tool.

Figures produced by the calculator join the verifier's whitelist. They are exact by
construction, so an answer quoting them is grounded in the strongest possible sense.
"""

from __future__ import annotations

import random

from capengine.trace import usd
from datagen.narrate import _pick
from datagen.scenarios import Scenario

_ENUM_OPENERS = [
    "Here is the list, and it is a short one.",
    "There are only a handful, so let me name them.",
    "The rules here are finite, which helps.",
    "Straightforward enough to answer in full.",
]

_ASK_OPENERS = [
    "I can answer that, but not from here.",
    "I need the cap sheet before I can give you a real number.",
    "That one turns on figures I do not have.",
    "Happy to work it out -- send me the numbers first.",
]


def _no_sheet_enumeration(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    season = f["season"]
    q = s.question.lower()
    parts = [_pick(rng, _ENUM_OPENERS)]

    if "first apron" in q and "lose" in q:
        parts.append(
            f"Over the first apron ({usd(f['first_apron'])} in {season}) a team loses four "
            "things: the full non-taxpayer mid-level, the bi-annual exception, the ability "
            "to acquire a player by sign-and-trade, and access to the buyout market for "
            "anyone whose pre-waiver salary exceeded the non-taxpayer mid-level. It is also "
            "capped at taking back 100% of outgoing salary in a trade, and it cannot use a "
            "traded player exception generated in a prior league year."
        )
        parts.append(
            "What it keeps: the taxpayer mid-level, the ability to aggregate salaries in a "
            "trade, the ability to send cash, minimum contracts, and its own Bird rights. "
            "That is the whole list."
        )
    elif "second-apron" in q or "second apron" in q:
        parts.append(
            f"Over the second apron ({usd(f['second_apron'])} in {season}) a team can still "
            "trade one salary for another at 100% matching, sign minimum contracts, and "
            "re-sign its own free agents using Bird rights. That is genuinely all."
        )
        parts.append(
            "What it cannot do: aggregate two salaries into one trade, send cash in any "
            "trade, use any mid-level exception including the taxpayer version, acquire "
            "anyone by sign-and-trade, or sign a mid-season waivee who was earning above the "
            "non-taxpayer mid-level."
        )
    elif "hard cap" in q:
        parts.append(
            "Six moves hard-cap a team at the first apron: using the non-taxpayer mid-level, "
            "using the bi-annual exception, acquiring a player by sign-and-trade, taking "
            "back more than 100% of outgoing salary, using a prior-year traded player "
            "exception, and signing a mid-season waivee who was earning above the "
            "non-taxpayer mid-level."
        )
        parts.append(
            "Four hard-cap a team at the second apron: using the taxpayer mid-level, "
            "aggregating salaries in a trade, sending cash in a trade, and using an outgoing "
            "sign-and-traded player's salary for matching. The room exception triggers no "
            "hard cap at all. Whichever applies runs through June 30 and is never retroactive."
        )
    elif "draft" in q:
        parts.append(
            "Finishing a season over the second apron freezes the team's first-round pick "
            "seven drafts out -- it becomes untradeable, and it unfreezes only after the "
            "team finishes below the second apron in three of the following four seasons."
        )
        parts.append(
            "Finish over the second apron in three of five seasons and that frozen pick "
            "moves to the end of the first round regardless of record. Multiple demoted "
            "picks order by reverse winning percentage."
        )
    elif "tax line" in q:
        parts.append(
            f"Between the tax line ({usd(f.get('tax_line', 0)) if f.get('tax_line') else 'the tax line'}) "
            f"and the first apron ({usd(f['first_apron'])}), a team keeps everything. The full "
            "non-taxpayer mid-level, the bi-annual exception, sign-and-trades, aggregation, "
            "cash, expanded salary matching -- all of it survives."
        )
        parts.append(
            "The tax line costs money, not flexibility: the bill itself, forfeiting the "
            "share distributed to non-taxpaying teams, and accruing toward repeater status. "
            "The restrictions start at the first apron, not here."
        )
    else:
        parts.append(
            f"At the tax line a team pays but keeps every tool. Over the first apron "
            f"({usd(f['first_apron'])}) it loses the full mid-level, the bi-annual, "
            "sign-and-trade acquisitions, the buyout market above the mid-level, and "
            "expanded salary matching. Over the second apron "
            f"({usd(f['second_apron'])}) it additionally loses aggregation, cash in trades, "
            "and every mid-level, and it starts losing draft picks."
        )
        parts.append(
            "Those are the three tiers. Each one is a strictly smaller set of options than "
            "the one below it."
        )

    parts.append(
        "If you tell me where a specific team sits, I can say which of these actually bind."
    )
    return " ".join(parts)


def _missing_data_request(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    parts = [_pick(rng, _ASK_OPENERS)]
    parts.append(
        "Nothing about a team's payroll is something I should be recalling -- salary figures "
        "change with every transaction, and a number I produce from memory would be wrong "
        "in a way that looks right."
    )
    wanted = "; ".join(f["must_ask_for"])
    parts.append(f"Send me the cap sheet and I can answer immediately. What I need: {wanted}.")
    parts.append(
        f"The {f['season']} thresholds I do have — first apron {usd(f['first_apron']) if f.get('first_apron') else ''}"
        if f.get("first_apron")
        else "Paste the sheet and the thresholds block along with it."
    )
    return " ".join(p for p in parts if p.strip())


def _grounding_discipline(s: Scenario, rng: random.Random) -> str:
    f = s.answer_facts
    parts = [
        f"We sit at {usd(f['apron_salary'])}, which puts us {f['apron_level']}.",
    ]
    level = f["apron_level"]
    if "second apron" in level:
        parts.append(
            "That is the constraint that matters, and everything else is downstream of it. "
            "No aggregation, no cash, no mid-level, and a first-round pick freezes if we "
            "finish here. Every addition is a minimum contract, and every subtraction is "
            "worth more than it looks."
        )
    elif "first apron" in level:
        parts.append(
            "The binding constraint is trade flexibility: we match dollar-for-dollar and "
            "nothing more, which means any upgrade has to be salary-neutral. We keep the "
            "taxpayer mid-level, and spending it would hard-cap us at the second apron."
        )
    elif "tax line" in level:
        parts.append(
            "We are paying, but we are not restricted. The full toolkit is intact — the "
            "question is which tool we want to spend, since most of them hard-cap us the "
            "moment we use one."
        )
    else:
        parts.append(
            "We are below the tax entirely, so nothing restricts us. The question is not "
            "what we are allowed to do, it is what we want to commit to."
        )
    parts.append(
        "I would not put a number on anything beyond that without the specific contracts in "
        "front of me."
    )
    return " ".join(parts)


def _tool_final(s: Scenario, rng: random.Random) -> str:
    """The closing prose after the calculator has done the arithmetic."""
    f = s.answer_facts
    if s.kind == "tool_tax_bill":
        parts = [f"The bill is {usd(f['total'])}."]
        parts.append(
            f"We are {usd(f['amount_over'])} into the tax, assessed on the "
            f"{'repeater' if f['is_repeater'] else 'standard'} schedule."
        )
        for i, b in enumerate(f["brackets"]):
            lead = "The first" if i == 0 else "The next"
            parts.append(
                f"{lead} {usd(b['amount'])} at ${b['rate']:.2f} per dollar is "
                f"{usd(b['owed'])}."
            )
        parts.append(f"Those add to {usd(f['total'])}.")
        if f["is_repeater"]:
            parts.append(
                "Repeater rates are doing the damage here — the same overage on the standard "
                "schedule would cost substantially less."
            )
        return " ".join(parts)

    legal = f["legal"]
    label = "LEGAL" if legal else "ILLEGAL"
    parts = [f"**Verdict: {label}.**"]
    parts.append(
        f"Sending out {usd(f['outgoing'])} sets our ceiling at {usd(f['ceiling'])} under "
        f"{f['rule'].split(' (')[0]}."
    )
    if legal:
        parts.append(
            f"Taking back {usd(f['incoming'])} fits inside that with "
            f"{usd(f['ceiling'] - f['incoming'])} to spare, so the money works."
        )
        parts.append(
            "Worth noting that taking back more than we send would hard-cap us at the first "
            "apron for the rest of the league year."
        )
    else:
        parts.append(
            f"Taking back {usd(f['incoming'])} is {usd(f['incoming'] - f['ceiling'])} more "
            "than we can absorb, and no exception closes a gap of that size."
        )
        parts.append("Find a third team or trim the incoming salary.")
    return " ".join(parts)


V2_NARRATORS = {
    "no_sheet_enumeration": _no_sheet_enumeration,
    "missing_data_request": _missing_data_request,
    "grounding_discipline": _grounding_discipline,
    "tool_tax_bill": _tool_final,
    "tool_matching": _tool_final,
}


def narrate_v2(scenario: Scenario, rng: random.Random) -> str:
    return V2_NARRATORS[scenario.kind](scenario, rng)


def tool_messages(scenario) -> list[dict]:
    """Render a tool scenario's call/result sequence as chat messages.

    `arguments` must be a dict, not the JSON string the OpenAI API uses. Qwen's chat
    template iterates the argument mapping to emit `<parameter=...>` tags, so a string
    silently renders `<function=calc>` with no parameters at all -- a call the model would
    learn to make and that would never do anything.
    """
    messages: list[dict] = []
    for index, turn in enumerate(scenario.tool_turns):
        messages.append({
            "role": "assistant",
            "content": "",
            "tool_calls": [{
                "id": f"call_{index}",
                "type": "function",
                "function": {
                    "name": "calc",
                    "arguments": {"expression": turn["expression"]},
                },
            }],
        })
        messages.append({
            "role": "tool",
            "tool_call_id": f"call_{index}",
            "name": "calc",
            "content": turn["result"],
        })
    return messages
