"""Generate the v2 data slices.

    python -m datagen.generate_v2 --count 3500 --out data/generated/v2.jsonl

Same contract as v1: CapEngine computes, a narrator writes, the verifier rejects anything
quoting a figure the engine never produced. Two additions:

  - Tool rows carry a real call/result exchange, so the whitelist grows to include the
    calculator's outputs. Those are exact by construction, which makes a figure quoted from
    a tool result the best-grounded kind of figure in the set.
  - Rows with no cap sheet have almost nothing on the whitelist, which is the point --
    they are training the model to answer without reaching for numbers at all.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

from datagen.narrate_v2 import narrate_v2, tool_messages
from datagen.prompts import SYSTEM_PROMPT
from datagen.scenarios import Scenario
from datagen.scenarios_v2 import V2_MIX, V2_SAMPLERS, sample_v2
from datagen.verify import verify

# Rows without a cap sheet are graded on restraint rather than recall: the verifier's
# "too short to have shown its work" rule does not apply, and neither does a verdict check.
NO_SHEET_KINDS = {"no_sheet_enumeration", "missing_data_request"}


def allowed_with_tools(scenario: Scenario) -> set[int]:
    """Whitelist, extended with whatever the calculator returned."""
    allowed = set(scenario.allowed_values())
    for turn in getattr(scenario, "tool_turns", []):
        raw = turn["result"].replace(",", "")
        try:
            allowed.add(int(float(raw)))
        except ValueError:
            continue
        # A rounded tool result is equally legitimate to quote.
        allowed.add(round(float(raw)))
    return allowed


def build_row(scenario: Scenario, response: str) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": scenario.prompt},
    ]
    turns = getattr(scenario, "tool_turns", [])
    if turns:
        messages.extend(tool_messages(scenario))
    messages.append({"role": "assistant", "content": response.strip()})

    return {
        "messages": messages,
        "kind": scenario.kind,
        "season": scenario.season,
        "verdict": scenario.verdict,
        "attempts": 1,
        "ground_truth": scenario.answer_facts,
        "allowed_values": sorted(allowed_with_tools(scenario)),
        "required_values": list(scenario.required_values),
        "uses_tools": bool(turns),
    }


def check(scenario: Scenario, response: str) -> tuple[bool, str]:
    """Verify a v2 row, relaxing only the rules that do not apply without a cap sheet."""
    allowed = allowed_with_tools(scenario)
    original = scenario.allowed_values
    scenario.allowed_values = lambda: allowed  # type: ignore[method-assign]
    try:
        result = verify(scenario, response, strict_verdict=scenario.verdict is not None)
    finally:
        scenario.allowed_values = original  # type: ignore[method-assign]

    problems = []
    if result.unknown_values:
        problems.append("invented: " + ", ".join(f"${v:,}" for v in result.unknown_values))
    if result.missing_required:
        problems.append("missing required")
    if result.approximations:
        problems.append("approximation")
    if not result.verdict_ok:
        problems.append("verdict mismatch")
    if scenario.kind not in NO_SHEET_KINDS and result.notes:
        problems.extend(result.notes)
    return not problems, "; ".join(problems)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=3500)
    parser.add_argument("--out", type=Path, default=Path("data/generated/v2.jsonl"))
    parser.add_argument("--seed", type=int, default=200)
    parser.add_argument("--kind", default=None, choices=sorted(V2_SAMPLERS) + [None])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    kept: Counter[str] = Counter()
    dropped: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    rows = []

    for index in range(args.count):
        scenario = sample_v2(rng, kind=args.kind)
        response = narrate_v2(scenario, rng)
        ok, why = check(scenario, response)
        if not ok:
            dropped[scenario.kind] += 1
            reasons[why.split(";")[0][:60]] += 1
            continue
        rows.append(build_row(scenario, response))
        kept[scenario.kind] += 1
        if (index + 1) % 1000 == 0:
            print(f"  {index + 1}/{args.count}", file=sys.stderr, flush=True)

    total = sum(kept.values())
    if not args.dry_run:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"\nWrote {total} verified v2 examples to {args.out}")
    else:
        print(f"\nDry run: {total} would be written")

    print("\nBy slice:")
    for name in sorted(kept, key=lambda k: -kept[k]):
        target = V2_MIX.get(name, 0)
        print(f"  {name:24} {kept[name]:5}  ({kept[name] / total:.1%}, target {target:.0%})"
              f"   dropped {dropped.get(name, 0)}")
    tool_rows = sum(1 for r in rows if r["uses_tools"])
    print(f"\nTool-calling rows: {tool_rows} ({tool_rows / total:.1%})")
    if sum(dropped.values()):
        print(f"\nDropped {sum(dropped.values())} total:")
        for why, count in reasons.most_common(6):
            print(f"  {count:4}  {why}")


if __name__ == "__main__":
    main()
