"""Put eval runs side by side, so "better" is a number rather than an impression.

    python -m eval.compare eval/results/base-qwen.jsonl eval/results/ft2-qwen.jsonl \\
        --labels base v1 --gates

Prints the headline metrics per run, the per-scenario-type breakdown, and -- with --gates --
whether the last run clears the v2 targets. Exits nonzero on a gate miss, so shipping
decisions can be made by a script instead of by eyeballing two reports in different windows.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

# v2 targets from the plan. Deliberately below 100%: chained arithmetic and grounding are
# hard, and a gate nobody can pass is a gate nobody uses.
GATES = {
    "verdict": 0.90,
    "arithmetic": 0.90,
    "grounding": 0.70,
    "staleness": 0.70,
    "loops": 0.0,  # maximum, not minimum
}

_LOOP_WINDOW = 6
_LOOP_THRESHOLD = 4


def looped(text: str) -> bool:
    words = (text or "").split()
    if len(words) < _LOOP_WINDOW * 2:
        return False
    counts: dict[str, int] = {}
    for i in range(len(words) - _LOOP_WINDOW):
        gram = " ".join(words[i:i + _LOOP_WINDOW])
        counts[gram] = counts.get(gram, 0) + 1
    return max(counts.values()) >= _LOOP_THRESHOLD


def metrics(rows: list[dict]) -> dict:
    def rate(values):
        return statistics.mean(values) if values else None

    verdicts = [r["verdict_correct"] for r in rows if r.get("verdict_correct") is not None]
    arithmetic = [
        (r.get("required_total", 0) == 0) or (r.get("required_hit", 0) == r["required_total"])
        for r in rows
    ]
    grounding = [not r.get("invented") for r in rows]
    staleness = [not r.get("invented") for r in rows if r.get("kind") == "anti_staleness"]
    loops = [looped(r.get("response", "")) for r in rows]
    tool_rows = [r for r in rows if r.get("tool_calls")]

    return {
        "n": len(rows),
        "verdict": rate(verdicts),
        "arithmetic": rate(arithmetic),
        "grounding": rate(grounding),
        "staleness": rate(staleness),
        "loops": rate(loops),
        "tool_use": len(tool_rows) / len(rows) if rows else 0,
    }


def pct(value) -> str:
    return "   n/a" if value is None else f"{value:6.1%}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="+", type=Path)
    parser.add_argument("--labels", nargs="*", default=None)
    parser.add_argument("--gates", action="store_true",
                        help="check the final run against the v2 targets and exit nonzero on a miss")
    args = parser.parse_args()

    runs = []
    for index, path in enumerate(args.results):
        if not path.exists():
            sys.exit(f"No results at {path}")
        rows = [json.loads(line) for line in path.open() if line.strip()]
        label = (args.labels[index] if args.labels and index < len(args.labels)
                 else path.stem)
        runs.append((label, rows, metrics(rows)))

    width = max(len(label) for label, _, _ in runs) + 2
    print(f"{'run':<{width}}{'n':>6}{'verdict':>10}{'arith':>9}{'ground':>9}"
          f"{'stale':>9}{'loops':>9}{'tools':>9}")
    for label, _, m in runs:
        print(f"{label:<{width}}{m['n']:>6}{pct(m['verdict']):>10}{pct(m['arithmetic']):>9}"
              f"{pct(m['grounding']):>9}{pct(m['staleness']):>9}{pct(m['loops']):>9}"
              f"{pct(m['tool_use']):>9}")

    # Per-type, showing where a run gained or lost against the one before it.
    print("\nverdict accuracy by scenario type")
    types: set[str] = set()
    per_run = []
    for _, rows, _ in runs:
        by_type: dict[str, list[bool]] = defaultdict(list)
        for row in rows:
            if row.get("verdict_correct") is not None:
                by_type[row.get("kind", "?")].append(row["verdict_correct"])
        types |= set(by_type)
        per_run.append(by_type)

    header = "".join(f"{label:>12}" for label, _, _ in runs)
    print(f"  {'type':<24}{header}")
    for kind in sorted(types):
        cells = "".join(
            f"{pct(statistics.mean(by_type[kind])) if by_type.get(kind) else '   n/a':>12}"
            for by_type in per_run
        )
        print(f"  {kind:<24}{cells}")

    if args.gates:
        label, _, final = runs[-1]
        print(f"\ngates for {label}")
        failures = []
        for name, target in GATES.items():
            value = final.get(name)
            if value is None:
                print(f"  {name:<12} n/a")
                continue
            ok = value <= target if name == "loops" else value >= target
            comparator = "<=" if name == "loops" else ">="
            print(f"  {name:<12}{pct(value)}  {comparator} {target:.0%}  "
                  f"{'PASS' if ok else 'FAIL'}")
            if not ok:
                failures.append(name)
        if failures:
            print("\nMissed: " + ", ".join(failures))
            print("Back to error analysis, not hyperparameters.")
            sys.exit(1)
        print("\nAll gates pass.")


if __name__ == "__main__":
    main()
