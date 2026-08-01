"""Print training examples for a human to read.

    python -m datagen.review --data data/dataset/train.jsonl --count 20
    python -m datagen.review --data data/generated/agent.jsonl --kind tax_bill

The verifier guarantees that every dollar figure in an example was computed by CapEngine. It
does not and cannot check *prose claims about the rules* -- a sentence like "repeater brackets
step up by $0.25 each" uses no forbidden figure but is still false. Only reading catches that.

So this is not optional tooling. Read fifty examples before training on them; a dataset that
is subtly wrong is the most expensive mistake available here, because the model will learn
the error and state it confidently.
"""

from __future__ import annotations

import argparse
import json
import random
import textwrap
from collections import Counter
from pathlib import Path

RULE_CLAIM_FLAGS = [
    # Phrases that tend to precede a generalization the verifier cannot check.
    ("always", "absolute claim"),
    ("never", "absolute claim"),
    ("double", "quantitative comparison"),
    ("triple", "quantitative comparison"),
    ("each bracket", "bracket-progression claim"),
    ("every bracket", "bracket-progression claim"),
    ("steps up by", "bracket-progression claim"),
    ("twice", "quantitative comparison"),
]


def flag_rule_claims(text: str) -> list[str]:
    """Surface sentences worth a second look. Advisory only -- these are not errors."""
    found = []
    lowered = text.lower()
    for phrase, why in RULE_CLAIM_FLAGS:
        if phrase in lowered:
            for sentence in text.replace("\n", " ").split(". "):
                if phrase in sentence.lower():
                    found.append(f"[{why}] {sentence.strip()}")
                    break
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/dataset/train.jsonl"))
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--kind", default=None)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--prompts", action="store_true",
                        help="show the full pasted cap sheet, not just the question")
    parser.add_argument("--flags-only", action="store_true",
                        help="scan everything and print only sentences worth checking")
    args = parser.parse_args()

    if not args.data.exists():
        raise SystemExit(f"No dataset at {args.data}")

    rows = [json.loads(line) for line in args.data.open() if line.strip()]
    if args.kind:
        rows = [r for r in rows if r.get("kind") == args.kind]
    if not rows:
        raise SystemExit("No matching examples.")

    if args.flags_only:
        counts: Counter[str] = Counter()
        for row in rows:
            for flag in flag_rule_claims(row["messages"][-1]["content"]):
                counts[flag] += 1
        if not counts:
            print(f"Scanned {len(rows)} examples. Nothing flagged.")
            return
        print(f"Scanned {len(rows)} examples. Sentences worth checking by hand:\n")
        for flag, n in counts.most_common(40):
            print(f"({n}x) {textwrap.shorten(flag, 150)}")
        return

    rng = random.Random(args.seed)
    for row in rng.sample(rows, min(args.count, len(rows))):
        messages = row["messages"]
        print("=" * 78)
        print(f"{row.get('kind', '?')}   season {row.get('season', '?')}   "
              f"verdict {row.get('verdict') or '--'}")
        print("=" * 78)

        user = messages[1]["content"]
        print(user if args.prompts else user.split("\n\n")[-1])
        print()
        print(textwrap.fill(messages[-1]["content"], width=94))

        flags = flag_rule_claims(messages[-1]["content"])
        if flags:
            print("\n  worth checking:")
            for flag in flags:
                print(f"    {textwrap.shorten(flag, 150)}")
        print()


if __name__ == "__main__":
    main()
