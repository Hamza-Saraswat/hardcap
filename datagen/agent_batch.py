"""Hand scenario batches to writing agents, then verify what comes back.

The template narrator produces correct prose but a limited number of shapes. Mixing in
examples written freehand keeps the model from locking onto those shapes. This module is the
bridge: `export` writes a batch of scenarios as a briefing an agent can work from, `ingest`
checks every returned answer against the same verifier everything else passes through.

    python -m datagen.agent_batch export --count 60 --batch 1 --out data/agent_batches
    python -m datagen.agent_batch ingest --batches data/agent_batches --out data/generated/agent.jsonl

An agent's prose is not trusted any more than a template's. Anything quoting a figure the
engine did not compute is rejected on the way in.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from capengine.trace import usd
from datagen.prompts import SYSTEM_PROMPT
from datagen.scenarios import Scenario, sample
from datagen.verify import verify

BRIEFING = """\
# Writing batch {batch}

You are writing training examples for a basketball salary cap assistant. Each scenario below
has already been solved by a deterministic rules engine. Your job is to express the answer in
natural language -- the way a sharp front-office analyst would say it to a general manager.

## Rules

1. **Use only the figures in the trace.** Every dollar amount you write must appear in that
   scenario's trace or its cap sheet. Do not derive new numbers, even correct ones. An
   automatic checker rejects any figure the engine did not compute.
2. **Exact amounts, comma-formatted.** `$12,345,678`. Never `$12.3 million`, never "about",
   never "roughly".
3. **Include every required figure** listed for the scenario.
4. **Open with the verdict** when one is given: `**Verdict: LEGAL.**` or
   `**Verdict: ILLEGAL.**`, then explain. On a LEGAL verdict, keep negations like "cannot"
   or "not allowed" out of the first few sentences -- a checker reads the opening to confirm
   the verdict, and an early negation reads as a rejection.
5. **Vary your writing.** These examples exist to teach the model range. Do not use the same
   opening or structure twice in this batch. Some answers can lead with the number, some with
   the rule, some with the consequence. Length can vary too.
6. **Sound like an analyst, not a textbook.** Direct, specific, willing to volunteer the
   thing the GM did not ask about but needs to know. No throat-clearing, no restating the
   question back.

## Output format

Write one JSON object per line to `{out}`, nothing else in the file:

    {{"id": 0, "response": "**Verdict: ILLEGAL.** ..."}}

The `id` must match the scenario number below.

---

{scenarios}
"""

SCENARIO_BLOCK = """\
## Scenario {id} -- {kind}

**What the user said:**

```
{prompt}
```

**Ground truth:** {facts}

**Verdict:** {verdict}

**Required figures (must all appear):** {required}

**Computation trace (the only figures you may use):**

```
{trace}
```

"""


def export(count: int, batch: int, out_dir: Path, seed: int) -> None:
    rng = random.Random(seed * 1000 + batch)
    scenarios = [sample(rng) for _ in range(count)]

    out_dir.mkdir(parents=True, exist_ok=True)
    blocks = []
    records = []

    for index, scenario in enumerate(scenarios):
        blocks.append(
            SCENARIO_BLOCK.format(
                id=index,
                kind=scenario.kind,
                prompt=scenario.prompt,
                facts=json.dumps(scenario.answer_facts, default=str)[:1200],
                verdict=scenario.verdict or "(no yes/no verdict -- explain the situation)",
                required=", ".join(usd(v) for v in scenario.required_values) or "none",
                trace=scenario.trace.render(),
            )
        )
        records.append(_serialize(scenario))

    responses_path = out_dir / f"batch{batch}_responses.jsonl"
    (out_dir / f"batch{batch}_brief.md").write_text(
        BRIEFING.format(batch=batch, out=responses_path, scenarios="\n".join(blocks))
    )
    (out_dir / f"batch{batch}_scenarios.json").write_text(json.dumps(records, indent=2))
    print(f"Batch {batch}: {count} scenarios -> {out_dir}/batch{batch}_brief.md")


def _serialize(scenario: Scenario) -> dict:
    return {
        "kind": scenario.kind,
        "prompt": scenario.prompt,
        "verdict": scenario.verdict,
        "season": scenario.season,
        "answer_facts": scenario.answer_facts,
        "required_values": list(scenario.required_values),
        "allowed_values": sorted(scenario.allowed_values()),
    }


def _rehydrate(record: dict) -> Scenario:
    from capengine.trace import Trace

    scenario = Scenario(
        kind=record["kind"],
        context="",
        question=record["prompt"],
        answer_facts=record["answer_facts"],
        trace=Trace(),
        required_values=record["required_values"],
        verdict=record["verdict"],
        season=record["season"],
    )
    # allowed_values was computed at export time; preserve it exactly.
    allowed = set(record["allowed_values"])
    scenario.allowed_values = lambda: allowed  # type: ignore[method-assign]
    return scenario


def ingest(batch_dir: Path, out_path: Path) -> None:
    kept: Counter[str] = Counter()
    rejected: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    rows = []

    for scenarios_file in sorted(batch_dir.glob("batch*_scenarios.json")):
        batch = scenarios_file.name.split("_")[0]
        responses_file = batch_dir / f"{batch}_responses.jsonl"
        if not responses_file.exists():
            print(f"{batch}: no responses file yet, skipping")
            continue

        records = json.loads(scenarios_file.read_text())
        responses = {}
        for line in responses_file.open():
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                responses[int(payload["id"])] = payload["response"]
            except (json.JSONDecodeError, KeyError, ValueError):
                reasons["unparseable line"] += 1

        for index, record in enumerate(records):
            response = responses.get(index)
            if not response:
                reasons["missing response"] += 1
                continue

            scenario = _rehydrate(record)
            result = verify(scenario, response)
            if not result.ok:
                rejected[record["kind"]] += 1
                if result.unknown_values:
                    reasons["invented figure"] += 1
                if result.missing_required:
                    reasons["missing required"] += 1
                if result.approximations:
                    reasons["approximation"] += 1
                if not result.verdict_ok:
                    reasons["verdict mismatch"] += 1
                continue

            rows.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": record["prompt"]},
                    {"role": "assistant", "content": response.strip()},
                ],
                "kind": record["kind"],
                "season": record["season"],
                "verdict": record["verdict"],
                "attempts": 1,
                "ground_truth": record["answer_facts"],
                "allowed_values": record["allowed_values"],
                "required_values": record["required_values"],
            })
            kept[record["kind"]] += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")

    total = sum(kept.values())
    print(f"\nAccepted {total} agent-written examples -> {out_path}")
    if sum(rejected.values()):
        print(f"Rejected {sum(rejected.values())}: {dict(reasons)}")
    for kind, n in kept.most_common():
        print(f"  {kind:24} {n:4}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    exporter = sub.add_parser("export")
    exporter.add_argument("--count", type=int, default=60)
    exporter.add_argument("--batch", type=int, required=True)
    exporter.add_argument("--out", type=Path, default=Path("data/agent_batches"))
    exporter.add_argument("--seed", type=int, default=7)

    ingester = sub.add_parser("ingest")
    ingester.add_argument("--batches", type=Path, default=Path("data/agent_batches"))
    ingester.add_argument("--out", type=Path, default=Path("data/generated/agent.jsonl"))

    args = parser.parse_args()
    if args.command == "export":
        export(args.count, args.batch, args.out, args.seed)
    else:
        ingest(args.batches, args.out)


if __name__ == "__main__":
    main()
