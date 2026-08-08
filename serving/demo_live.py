"""The live demo, end to end, with verification.

Builds a real-world scenario -- the 2026-27 Nuggets, reported ~$1.9M over the second apron
after matching Spencer Jones's offer sheet -- asks the served fine-tune the deadline
question, and then checks every dollar figure in its answer against CapEngine.

    python -m serving.demo_live --base-url http://localhost:8000/v1 --model capologist

Thresholds are the league's published 2026-27 figures. The team total and Jones's salary are
the reported ones; the rest of the roster is reconstructed (this project never scrapes
contract sites), which the prompt is honest about.
"""

from __future__ import annotations

import argparse
import json
import random
import urllib.request

from capengine.constants import get_season
from capengine.models import Contract
from capengine.tax import compute_tax
from capengine.trace import Trace, usd
from datagen.capsheet import team_context
from datagen.prompts import SYSTEM_PROMPT
from datagen.scenarios import Scenario, random_team
from datagen.verify import verify

QUESTION = (
    "We're a repeater and we just matched Spencer Jones's offer sheet, which put us over "
    "the second apron. Ownership wants a path back under before the deadline. What are our "
    "options, and can we package two of the smaller contracts together to do it?"
)


def build_scenario(seed: int = 7) -> Scenario:
    rng = random.Random(seed)
    k = get_season("2026-27")

    # Reported: ~$1.9M over the 2026-27 second apron after the Jones match.
    target_total = k.second_apron + 1_900_000
    jones = Contract(player="Spencer Jones", salary=6_000_000, years_remaining=2)

    team = random_team(rng, season="2026-27", roster=14, is_repeater=True)
    filler_total = target_total - jones.apron_hit
    scale = (filler_total - sum(0 for _ in team.contracts)) / max(
        sum(c.salary for c in team.contracts), 1
    )
    minimum = k.minimum_salary(2)
    for contract in team.contracts:
        contract.salary = max(minimum, int(contract.salary * scale))
    # Land exactly on the reported total.
    team.contracts[0].salary += target_total - (
        sum(c.apron_hit for c in team.contracts) + jones.apron_hit
    )
    team.contracts.append(jones)
    team.name = "Denver"

    overage = team.apron_salary - k.second_apron
    trace = Trace()
    trace.add(f"{team.name} apron salary", team.apron_salary)
    trace.add(f"{k.season} second apron", k.second_apron)
    trace.add("Amount over the second apron", overage)
    trace.add("Aggregation unavailable",
              detail="over the second apron, two salaries cannot be combined in one trade")
    trace.add("Cash unavailable", detail="no cash may be sent in any trade")
    for contract in sorted(team.contracts, key=lambda c: c.salary):
        if contract.salary > overage:
            trace.add(
                f"Moving {contract.player} alone clears it",
                contract.salary - overage,
                detail=f"{usd(contract.salary)} out with nothing back",
            )
    tax = compute_tax(team)
    trace.extend(tax.trace)

    return Scenario(
        kind="scenario_planning",
        context=team_context(team),
        question=QUESTION,
        answer_facts={"overage": overage, "aggregation_banned": True},
        trace=trace,
        required_values=[overage],
        season="2026-27",
    )


def ask(base_url: str, model: str, scenario: Scenario) -> str:
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": scenario.prompt},
        ],
        "temperature": 0,
        "max_tokens": 1600,
        "chat_template_kwargs": {"enable_thinking": False},
    }).encode()
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.loads(response.read())["choices"][0]["message"]["content"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000/v1")
    parser.add_argument("--model", default="capologist")
    args = parser.parse_args()

    scenario = build_scenario()
    print("=" * 78)
    print("PROMPT (what a GM would paste)")
    print("=" * 78)
    print(scenario.prompt)

    answer = ask(args.base_url, args.model, scenario)
    print()
    print("=" * 78)
    print("CAPOLOGIST ANSWER")
    print("=" * 78)
    print(answer)

    result = verify(scenario, answer, strict_verdict=False)
    print()
    print("=" * 78)
    print("VERIFICATION AGAINST CAPENGINE")
    print("=" * 78)
    print("all figures grounded:", "YES" if result.ok or not result.unknown_values else "NO")
    if result.unknown_values:
        print("figures not computable from the sheet:",
              ", ".join(f"${v:,}" for v in result.unknown_values))
    if result.missing_required:
        print("missed the key figure:", ", ".join(f"${v:,}" for v in result.missing_required))
    print()
    print("ground truth for comparison:")
    print(scenario.trace.render())


if __name__ == "__main__":
    main()
