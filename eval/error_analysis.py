"""Bucket eval failures by cause, so the next data pass is aimed rather than guessed.

    python -m eval.error_analysis --results eval/results/ft2-qwen.jsonl --out docs/error-analysis-v1.md

The headline scores say *how much* is wrong; they never say *how*. A repetition loop and a
flipped verdict both register as one failed row, and only one of them is fixed by more
training data of the same kind. This groups every failure by scenario type and error kind,
quotes samples, and -- for invented figures -- separates genuine fabrication from arithmetic
the model derived correctly from figures it was given.

That last distinction decides the whole v2 plan. If most "invented" values are derivable
sums of whitelisted ones, the fix is a calculator tool. If they are unrelated numbers, the
fix is grounding, and a calculator would just make wrong answers faster.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

# A degenerate loop repeats a long phrase many times over. Six words is long enough that
# ordinary repetition ("the second apron ... the second apron") does not trip it.
_LOOP_WINDOW = 6
_LOOP_THRESHOLD = 4


def loop_score(text: str) -> tuple[int, str]:
    """Most-repeated six-word phrase and its count."""
    words = text.split()
    if len(words) < _LOOP_WINDOW * 2:
        return 0, ""
    grams = Counter(
        " ".join(words[i:i + _LOOP_WINDOW]) for i in range(len(words) - _LOOP_WINDOW)
    )
    phrase, count = grams.most_common(1)[0]
    return count, phrase


def derivable(target: int, allowed: set[int], tolerance: int = 0) -> str | None:
    """Could this figure have come from arithmetic on figures the model was given?

    Checks the operations that actually appear in cap work: sums and differences of two
    allowed values, and a value scaled by the rates and multipliers the CBA uses. A hit
    means the model did real arithmetic we simply did not whitelist -- a very different
    problem from inventing a number outright.
    """
    if target in allowed:
        return "already allowed"
    values = sorted(allowed)

    for a, b in combinations(values, 2):
        if abs(a + b - target) <= tolerance:
            return f"${a:,} + ${b:,}"
        if abs(abs(a - b) - target) <= tolerance:
            return f"${max(a, b):,} - ${min(a, b):,}"

    # Matching multipliers, tax rates, and the percentage bases used across the CBA.
    for value in values:
        for factor, label in (
            (2.0, "200%"), (1.25, "125%"), (1.5, "$1.50/dollar"), (1.75, "$1.75/dollar"),
            (3.0, "$3.00/dollar"), (3.25, "$3.25/dollar"), (3.5, "$3.50/dollar"),
            (4.75, "$4.75/dollar"), (5.5, "$5.50/dollar"), (6.75, "$6.75/dollar"),
            (0.25, "25% max"), (0.30, "30% max"), (0.35, "35% max"), (0.15, "15% of cap"),
            (0.9, "90% floor"),
        ):
            if abs(round(value * factor) - target) <= tolerance:
                return f"${value:,} x {label}"

    # Sum of several allowed values -- the classic multi-bracket tax total.
    if abs(sum(values) - target) <= tolerance:
        return "sum of all provided figures"
    return None


@dataclass
class Bucket:
    kind: str
    rows: list[dict] = field(default_factory=list)

    def sample(self, n: int = 3) -> list[dict]:
        return self.rows[:n]


def classify(row: dict) -> list[str]:
    """Every way this row failed. A row can fail more than one way."""
    kinds = []
    response = (row.get("response") or "").strip()

    if not response:
        kinds.append("empty response")
        return kinds

    count, _ = loop_score(response)
    if count >= _LOOP_THRESHOLD:
        kinds.append("degenerate loop")

    if row.get("verdict_correct") is False:
        kinds.append("verdict flipped")
    if row.get("required_total", 0) and row.get("required_hit", 0) < row["required_total"]:
        kinds.append("missing required figure")
    if row.get("invented"):
        kinds.append("invented figure")
    if not kinds:
        kinds.append("passed")
    return kinds


def analyze(rows: list[dict]) -> dict:
    buckets: dict[str, Bucket] = defaultdict(lambda: Bucket(kind=""))
    by_kind_and_type: Counter[tuple[str, str]] = Counter()
    derivation_hits: Counter[str] = Counter()
    derivation_examples: list[str] = []
    per_type: dict[str, Counter[str]] = defaultdict(Counter)
    invented_total = 0

    for row in rows:
        kinds = classify(row)
        for kind in kinds:
            key = kind
            buckets[key].kind = kind
            buckets[key].rows.append(row)
            by_kind_and_type[(kind, row.get("kind", "?"))] += 1

        for value in row.get("invented", []):
            invented_total += 1
            allowed = set(row.get("allowed_values", []))
            how = derivable(value, allowed)
            verdict = "derivable from provided figures" if how else "not derivable"
            derivation_hits[verdict] += 1
            per_type[row.get("kind", "?")][verdict] += 1
            if how and len(derivation_examples) < 12:
                derivation_examples.append(
                    f"${value:,} = {how}  [{row.get('kind', '?')}]"
                )

    return {
        "buckets": buckets,
        "by_kind_and_type": by_kind_and_type,
        "derivation_hits": derivation_hits,
        "derivation_examples": derivation_examples,
        "per_type": per_type,
        "invented_total": invented_total,
        "n": len(rows),
    }


def excerpt(text: str, limit: int = 320) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    return text[:limit] + ("…" if len(text) > limit else "")


def report(result: dict, label: str) -> str:
    n = result["n"]
    buckets = result["buckets"]
    lines = [
        f"# Error analysis — {label}",
        "",
        f"{n} scored examples. A row can appear in more than one bucket.",
        "",
        "## Failure kinds",
        "",
        "| Kind | Rows | Share |",
        "|---|---:|---:|",
    ]
    order = sorted(
        (k for k in buckets if k != "passed"), key=lambda k: -len(buckets[k].rows)
    )
    for kind in order:
        count = len(buckets[kind].rows)
        lines.append(f"| {kind} | {count} | {count / n:.1%} |")
    passed = len(buckets.get("passed", Bucket("passed")).rows)
    lines.append(f"| (clean) | {passed} | {passed / n:.1%} |")

    lines += ["", "## Where each kind concentrates", "",
              "| Kind | Scenario type | Rows |", "|---|---|---:|"]
    for (kind, kind_type), count in result["by_kind_and_type"].most_common(24):
        if kind == "passed":
            continue
        lines.append(f"| {kind} | {kind_type} | {count} |")

    # The question that decides v2's direction.
    hits = result["derivation_hits"]
    total = sum(hits.values())
    lines += [
        "", "## Invented figures: fabricated, or just underived arithmetic?", "",
        f"{result['invented_total']} flagged figures across all rows.", "",
        "| Verdict | Count | Share |", "|---|---:|---:|",
    ]
    for name, count in hits.most_common():
        lines.append(f"| {name} | {count} | {count / total:.1%} |" if total else "")
    if result["derivation_examples"]:
        lines += ["", "Examples the model computed correctly from figures it was given:", "",
                  "```"]
        lines += result["derivation_examples"]
        lines.append("```")

    # The actionable cut: a type whose flagged figures are mostly derivable is doing real
    # arithmetic badly, and a calculator fixes it. A type whose figures are mostly
    # undecipherable is fabricating, and no tool helps -- that needs grounding data.
    #
    # Read the "derivable" column as a FLOOR, not a measurement. The checker tries pairwise
    # sums and differences, single-value scalings, and the grand total -- it does not try
    # multi-term chains like (bracket1 x rate1) + (bracket2 x rate2), which is exactly the
    # shape of correct tax arithmetic. So genuine multi-step work is undercounted here, and
    # the honest conclusion is "grounding is a real problem across every type", not a precise
    # split between fabrication and arithmetic.
    lines += [
        "", "### By scenario type — calculator problem or grounding problem?", "",
        "*Derivable is a floor: the checker tries simple operations only, so multi-step "
        "arithmetic reads as non-derivable.*", "",
        "| Scenario type | Flagged | Derivable (floor) | Read as |", "|---|---:|---:|---|",
    ]
    for kind_type, counts in sorted(
        result["per_type"].items(), key=lambda kv: -sum(kv[1].values())
    ):
        total_type = sum(counts.values())
        derivable_n = counts.get("derivable from provided figures", 0)
        share = derivable_n / total_type if total_type else 0
        reading = (
            "some real arithmetic" if share >= 0.15 else "mostly untraceable — grounding data"
        )
        lines.append(
            f"| {kind_type} | {total_type} | {derivable_n} ({share:.0%}) | {reading} |"
        )

    lines += ["", "## Samples", ""]
    for kind in order:
        lines.append(f"### {kind}")
        lines.append("")
        for row in buckets[kind].sample(3):
            lines.append(f"- **{row.get('kind', '?')}** — expected verdict "
                         f"`{row.get('verdict_expected')}`, "
                         f"figures {row.get('required_hit')}/{row.get('required_total')}"
                         + (f", invented {', '.join(f'${v:,}' for v in row['invented'][:3])}"
                            if row.get("invented") else ""))
            lines.append(f"  > {excerpt(row.get('response', ''))}")
        lines.append("")

    return "\n".join(lines)


def backfill(rows: list[dict], eval_data: Path) -> list[dict]:
    """Attach allowed/required values to results written before the harness saved them.

    The harness scores in dataset order, so a positional join is exact. It is still checked
    against the recorded kind for every row -- a silent misalignment here would corrupt the
    very analysis meant to catch corruption.
    """
    source = [
        json.loads(line) for line in eval_data.open() if line.strip()
    ]
    source = [r for r in source if r.get("kind") != "general"]
    if len(source) != len(rows):
        raise SystemExit(
            f"Cannot backfill: {len(rows)} results vs {len(source)} eval rows. "
            "Re-run the eval instead of joining."
        )
    for result, original in zip(rows, source, strict=True):
        if result.get("kind") != original.get("kind"):
            raise SystemExit(
                "Cannot backfill: row order does not match "
                f"({result.get('kind')} vs {original.get('kind')}). Re-run the eval."
            )
        result.setdefault("allowed_values", original.get("allowed_values", []))
        result.setdefault("required_values", original.get("required_values", []))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--label", default=None)
    parser.add_argument("--eval-data", type=Path, default=None,
                        help="join this eval set to supply allowed_values for older results")
    args = parser.parse_args()

    if not args.results.exists():
        raise SystemExit(f"No results file at {args.results}")
    rows = [json.loads(line) for line in args.results.open() if line.strip()]
    if args.eval_data and not any(r.get("allowed_values") for r in rows):
        rows = backfill(rows, args.eval_data)
    result = analyze(rows)
    text = report(result, args.label or args.results.stem)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
        print(f"wrote {args.out}")
    print("\n".join(text.split("\n")[:40]))


if __name__ == "__main__":
    main()
