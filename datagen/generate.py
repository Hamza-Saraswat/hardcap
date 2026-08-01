"""Generate the training set.

    uv run python -m datagen.generate --count 10000 --out data/generated/domain.jsonl

Each example is sampled from CapEngine, narrated by a frontier model, and then checked
number by number against the engine's trace. Rejected answers are sent back with the
specific complaint attached and retried; anything still failing after a few attempts is
dropped and logged rather than quietly included.

Set ANTHROPIC_API_KEY before running. Use --dry-run to inspect the scenario space and the
prompts without spending anything.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from datagen.prompts import REPAIR_SUFFIX, SYSTEM_PROMPT, generation_prompt
from datagen.scenarios import MIX, Scenario, sample
from datagen.verify import Verification, verify

DEFAULT_MODEL = "claude-sonnet-5"
MAX_ATTEMPTS = 3


@dataclass
class Example:
    """One finished training row, in the messages format TRL and Unsloth both read."""

    messages: list[dict]
    kind: str
    season: str
    verdict: str | None
    attempts: int
    # Kept alongside the conversation so the eval harness and any later GRPO pass can
    # re-verify without regenerating the scenario.
    ground_truth: dict
    allowed_values: list[int]
    required_values: list[int]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def build_example(
    scenario: Scenario, response: str, attempts: int
) -> Example:
    return Example(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": scenario.prompt},
            {"role": "assistant", "content": response.strip()},
        ],
        kind=scenario.kind,
        season=scenario.season,
        verdict=scenario.verdict,
        attempts=attempts,
        ground_truth=scenario.answer_facts,
        allowed_values=sorted(scenario.allowed_values()),
        required_values=list(scenario.required_values),
    )


async def _narrate(client, model: str, scenario: Scenario) -> tuple[str | None, int, Verification | None]:
    """Ask for prose, verify it, and retry with the specific complaint if it fails."""
    prompt = generation_prompt(scenario)
    last: Verification | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        message = await client.messages.create(
            model=model,
            max_tokens=1600,
            messages=[{"role": "user", "content": prompt}],
        )
        response = "".join(block.text for block in message.content if block.type == "text")

        last = verify(scenario, response)
        if last.ok:
            return response, attempt, last

        prompt = generation_prompt(scenario) + REPAIR_SUFFIX.format(problems=last.problems())

    return None, MAX_ATTEMPTS, last


async def generate(
    count: int,
    out_path: Path,
    seed: int,
    model: str,
    concurrency: int,
    kind: str | None,
) -> None:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic()
    rng = random.Random(seed)
    scenarios = [sample(rng, kind=kind) for _ in range(count)]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_path = out_path.with_suffix(".rejected.jsonl")

    semaphore = asyncio.Semaphore(concurrency)
    kept: Counter[str] = Counter()
    dropped: Counter[str] = Counter()
    attempts_used: Counter[int] = Counter()
    done = 0

    out = out_path.open("w")
    rejects = rejected_path.open("w")

    async def worker(scenario: Scenario) -> None:
        nonlocal done
        async with semaphore:
            try:
                response, attempts, verification = await _narrate(client, model, scenario)
            except Exception as exc:  # noqa: BLE001 -- one bad call must not kill the run
                dropped[scenario.kind] += 1
                rejects.write(json.dumps({"kind": scenario.kind, "error": str(exc)}) + "\n")
                return

            if response is None:
                dropped[scenario.kind] += 1
                rejects.write(
                    json.dumps({
                        "kind": scenario.kind,
                        "prompt": scenario.prompt,
                        "problems": verification.problems() if verification else "",
                    })
                    + "\n"
                )
            else:
                out.write(build_example(scenario, response, attempts).to_json() + "\n")
                kept[scenario.kind] += 1
                attempts_used[attempts] += 1

            done += 1
            if done % 25 == 0 or done == count:
                print(
                    f"  {done}/{count} -- kept {sum(kept.values())}, "
                    f"dropped {sum(dropped.values())}",
                    file=sys.stderr,
                    flush=True,
                )

    try:
        await asyncio.gather(*(worker(s) for s in scenarios))
    finally:
        out.close()
        rejects.close()

    total_kept = sum(kept.values())
    print(f"\nWrote {total_kept} verified examples to {out_path}")
    if sum(dropped.values()):
        print(f"Dropped {sum(dropped.values())} (logged to {rejected_path})")
    print("\nBy scenario type:")
    for name in sorted(kept, key=lambda k: -kept[k]):
        share = kept[name] / total_kept if total_kept else 0
        print(f"  {name:24} {kept[name]:5}  ({share:.1%})   dropped {dropped.get(name, 0)}")
    if attempts_used:
        first_pass = attempts_used[1] / total_kept if total_kept else 0
        print(f"\nVerified on the first attempt: {first_pass:.1%}")


def generate_local(count: int, out_path: Path, seed: int, kind: str | None) -> None:
    """Generate the whole set from templates -- no API, no cost, no network.

    Correctness is identical to the API path, since both narrate figures the engine
    computed and both pass through the same verifier. Only the prose is less varied.
    """
    from datagen.narrate import narrate

    rng = random.Random(seed)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    kept: Counter[str] = Counter()
    dropped: Counter[str] = Counter()

    with out_path.open("w") as out:
        for index in range(count):
            scenario = sample(rng, kind=kind)
            response = narrate(scenario, rng)

            if not verify(scenario, response).ok:
                dropped[scenario.kind] += 1
                continue

            out.write(build_example(scenario, response, attempts=1).to_json() + "\n")
            kept[scenario.kind] += 1

            if (index + 1) % 1000 == 0:
                print(f"  {index + 1}/{count}", file=sys.stderr, flush=True)

    total = sum(kept.values())
    print(f"\nWrote {total} verified examples to {out_path}")
    if sum(dropped.values()):
        print(f"Dropped {sum(dropped.values())} that failed verification")
    print("\nBy scenario type:")
    for name in sorted(kept, key=lambda k: -kept[k]):
        print(f"  {name:24} {kept[name]:6}  ({kept[name] / total:.1%})"
              f"   dropped {dropped.get(name, 0)}")


def dry_run(count: int, seed: int, kind: str | None, show: int) -> None:
    """Inspect the scenario space without calling the API."""
    rng = random.Random(seed)
    scenarios = [sample(rng, kind=kind) for _ in range(count)]

    counts = Counter(s.kind for s in scenarios)
    seasons = Counter(s.season for s in scenarios)
    verdicts = Counter(s.verdict for s in scenarios if s.verdict)

    print(f"Sampled {count} scenarios (seed {seed})\n")
    print("By type:")
    for name, n in counts.most_common():
        target = MIX.get(name, 0)
        print(f"  {name:24} {n:5}  ({n / count:.1%}, target {target:.0%})")
    print("\nBy season:")
    for name, n in seasons.most_common():
        print(f"  {name:12} {n:5}  ({n / count:.1%})")
    if verdicts:
        print("\nVerdict balance (scenarios with a yes/no answer):")
        total = sum(verdicts.values())
        for name, n in verdicts.most_common():
            print(f"  {name:14} {n:5}  ({n / total:.1%})")

    empty_traces = [s for s in scenarios if not s.trace.steps]
    if empty_traces:
        print(f"\nWARNING: {len(empty_traces)} scenarios produced no trace")

    for scenario in scenarios[:show]:
        print("\n" + "=" * 78)
        print(f"KIND: {scenario.kind}   SEASON: {scenario.season}   "
              f"VERDICT: {scenario.verdict}")
        print("=" * 78)
        print(scenario.prompt)
        print("\n--- trace ---")
        print(scenario.trace.render())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--out", type=Path, default=Path("data/generated/domain.jsonl"))
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--kind", default=None, choices=sorted(MIX) + [None],
                        help="restrict to one scenario type")
    parser.add_argument("--dry-run", action="store_true",
                        help="sample scenarios and print stats without calling the API")
    parser.add_argument("--show", type=int, default=2,
                        help="how many full scenarios to print in a dry run")
    parser.add_argument("--local", action="store_true",
                        help="narrate from templates instead of the API: free and offline")
    args = parser.parse_args()

    if args.dry_run:
        dry_run(args.count, args.seed, args.kind, args.show)
        return

    if args.local:
        generate_local(args.count, args.out, args.seed, args.kind)
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "ANTHROPIC_API_KEY is not set.\n"
            "Export it, or run with --dry-run to inspect scenarios without calling the API."
        )

    asyncio.run(
        generate(args.count, args.out, args.seed, args.model, args.concurrency, args.kind)
    )


if __name__ == "__main__":
    main()
