"""Assemble the final training and evaluation splits.

    uv run python -m datagen.build_dataset \\
        --domain data/generated/domain.jsonl \\
        --general data/generated/general.jsonl \\
        --out data/dataset

Two jobs beyond concatenation:

  1. Mix in general instruction data. A model trained only on cap questions gets worse at
     everything else, including the ordinary conversation a front office tool still needs to
     handle. Research puts the useful band at 15-20% general data; LoRA's frozen base
     already limits the damage, so we sit at the low end by default.
  2. Split by scenario type, not at random. The eval set has to contain every scenario kind
     in the same proportion as training, or the headline accuracy number quietly hides a
     category the model never learned.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    with path.open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def stratified_split(
    rows: list[dict], eval_fraction: float, rng: random.Random
) -> tuple[list[dict], list[dict]]:
    """Hold out the same share of every scenario type."""
    by_kind: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_kind[row.get("kind", "general")].append(row)

    train: list[dict] = []
    held_out: list[dict] = []
    for kind, group in sorted(by_kind.items()):
        rng.shuffle(group)
        n = max(1, round(len(group) * eval_fraction)) if len(group) > 1 else 0
        held_out.extend(group[:n])
        train.extend(group[n:])

    rng.shuffle(train)
    rng.shuffle(held_out)
    return train, held_out


def training_view(row: dict) -> dict:
    """Strip metadata the trainer does not read, keeping the conversation itself."""
    return {"messages": row["messages"]}


def report(name: str, rows: list[dict]) -> None:
    kinds = Counter(r.get("kind", "general") for r in rows)
    print(f"\n{name}: {len(rows)} examples")
    for kind, n in kinds.most_common():
        print(f"  {kind:24} {n:6}  ({n / len(rows):.1%})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", type=Path, required=True,
                        help="verified cap-domain examples from datagen.generate")
    parser.add_argument("--general", type=Path, default=None,
                        help="general instruction data in the same messages format")
    parser.add_argument("--out", type=Path, default=Path("data/dataset"))
    parser.add_argument("--general-share", type=float, default=0.15,
                        help="target share of general data in the training mix")
    parser.add_argument("--eval-fraction", type=float, default=0.08)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    domain = read_jsonl(args.domain)
    if not domain:
        raise SystemExit(f"No examples found in {args.domain}")
    for row in domain:
        row.setdefault("kind", "unknown")

    general: list[dict] = []
    if args.general and args.general.exists():
        pool = read_jsonl(args.general)
        wanted = round(len(domain) * args.general_share / (1 - args.general_share))
        if wanted > len(pool):
            print(
                f"Note: wanted {wanted} general examples for a {args.general_share:.0%} "
                f"mix but only {len(pool)} are available; using all of them."
            )
        general = rng.sample(pool, min(wanted, len(pool)))
        for row in general:
            row["kind"] = "general"
    else:
        print(
            "No general instruction data supplied. Training on domain data alone risks\n"
            "degrading everything the model could do before. Fetch a slice of an open\n"
            "instruct set into messages format and pass it with --general."
        )

    combined = domain + general
    train, held_out = stratified_split(combined, args.eval_fraction, rng)

    write_jsonl([training_view(r) for r in train], args.out / "train.jsonl")
    write_jsonl(held_out, args.out / "eval.jsonl")

    report("train", train)
    report("eval (full metadata retained for scoring)", held_out)

    actual_general = sum(1 for r in train if r.get("kind") == "general") / len(train)
    print(f"\nGeneral data share of training mix: {actual_general:.1%}")
    print(f"\nWrote {args.out}/train.jsonl and {args.out}/eval.jsonl")


if __name__ == "__main__":
    main()
