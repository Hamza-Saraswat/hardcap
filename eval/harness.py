"""Evaluation harness.

    uv run python -m eval.harness --data data/dataset/eval.jsonl --model capologist
    uv run python -m eval.harness --data data/dataset/eval.jsonl --baseline claude-sonnet-5

Scores a model against CapEngine's ground truth on four things:

  accuracy    -- did it reach the right verdict on yes/no questions?
  arithmetic  -- did it state every required dollar figure, exactly?
  grounding   -- did it avoid inventing figures the engine never computed?
  staleness   -- on anti-staleness probes, did it use the pasted thresholds rather than
                 memorized ones? This is scored separately because it is the failure mode
                 the whole architecture is built to prevent.

Run it against the base model first. A fine-tune is only worth shipping if it beats both the
base model and the base model handed the same context.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from datagen.verify import dollar_figures

# Reasoning models (Qwen3.6 among them) emit <think>...</think> before the answer. Scoring
# must see only the answer: a verdict stated inside the thinking is not a verdict given to
# the user, and thinking routinely explores the wrong branch before landing on the right
# one. An unterminated block (generation cut off mid-think) leaves no answer at all -- that
# strips to empty and fails scoring, which is the correct outcome, visible per-example.
_THINK_BLOCK = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)
_THINK_OPEN = re.compile(r"<think>.*\Z", re.DOTALL | re.IGNORECASE)


def strip_thinking(text: str) -> str:
    return _THINK_OPEN.sub("", _THINK_BLOCK.sub("", text)).strip()


_LEGAL_WORDS = ("legal", "allowed", "permitted", "can do", "works", "yes")
_ILLEGAL_WORDS = (
    "illegal", "not legal", "cannot", "can't", "not allowed", "not permitted",
    "blocked", "prohibited", "barred", "no,",
)


@dataclass
class Score:
    kind: str
    verdict_expected: str | None = None
    verdict_correct: bool | None = None
    required_hit: int = 0
    required_total: int = 0
    invented: list[int] = field(default_factory=list)
    response: str = ""
    prompt: str = ""

    @property
    def arithmetic_ok(self) -> bool:
        return self.required_total == 0 or self.required_hit == self.required_total

    @property
    def grounded(self) -> bool:
        return not self.invented


def read_verdict(text: str) -> str | None:
    """Read the verdict off the opening of an answer.

    Only the first stretch is considered: a correct answer often goes on to explain what
    *would* have been illegal, and that discussion should not be mistaken for the verdict.
    """
    head = text[:400].lower()
    explicit = re.search(r"verdict[:\s*]*\**\s*(legal|illegal|allowed|not allowed)", head)
    if explicit:
        value = explicit.group(1)
        return "ILLEGAL" if value in {"illegal", "not allowed"} else "LEGAL"

    first_illegal = min(
        (head.find(w) for w in _ILLEGAL_WORDS if head.find(w) != -1), default=-1
    )
    first_legal = min((head.find(w) for w in _LEGAL_WORDS if head.find(w) != -1), default=-1)
    if first_illegal == -1 and first_legal == -1:
        return None
    if first_illegal == -1:
        return "LEGAL"
    if first_legal == -1:
        return "ILLEGAL"
    return "ILLEGAL" if first_illegal <= first_legal else "LEGAL"


def score_response(row: dict, response: str) -> Score:
    response = strip_thinking(response)
    expected = row.get("verdict")
    normalized = (
        {"ALLOWED": "LEGAL", "NOT ALLOWED": "ILLEGAL"}.get(expected, expected)
        if expected
        else None
    )

    claimed = dollar_figures(response)
    allowed = set(row.get("allowed_values", []))
    required = row.get("required_values", [])

    return Score(
        kind=row.get("kind", "unknown"),
        verdict_expected=normalized,
        verdict_correct=(read_verdict(response) == normalized) if normalized else None,
        required_hit=sum(1 for v in required if v in claimed),
        required_total=len(required),
        invented=sorted({v for v in claimed if v not in allowed and v >= 1000}),
        response=response,
        prompt=row["messages"][1]["content"],
    )


# -- model clients -------------------------------------------------------------------------


def call_openai_compatible(
    base_url: str, model: str, system: str, user: str, disable_thinking: bool = False
) -> str:
    """Works with Ollama, vLLM, llama.cpp server -- anything speaking the chat API."""
    body: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
        "max_tokens": 1600,
    }
    if disable_thinking:
        # vLLM extension honored by Qwen-family chat templates. Baselines run with
        # thinking off so base and fine-tune are compared on the same footing -- the
        # training data contains no thinking blocks, so the fine-tune answers directly.
        body["chat_template_kwargs"] = {"enable_thinking": False}
    payload = json.dumps(body).encode()

    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        body = json.loads(response.read())
    return body["choices"][0]["message"]["content"]


def call_anthropic(model: str, system: str, user: str) -> str:
    from anthropic import Anthropic

    client = Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=1600,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in message.content if b.type == "text")


# -- reporting -----------------------------------------------------------------------------


def summarize(scores: list[Score]) -> dict:
    def rate(values: list[bool]) -> float | None:
        return statistics.mean(values) if values else None

    verdicts = [s.verdict_correct for s in scores if s.verdict_correct is not None]
    staleness = [s for s in scores if s.kind == "anti_staleness"]

    return {
        "n": len(scores),
        "verdict_accuracy": rate(verdicts),
        "arithmetic_accuracy": rate([s.arithmetic_ok for s in scores]),
        "grounding": rate([s.grounded for s in scores]),
        "staleness_grounding": rate([s.grounded for s in staleness]),
        "required_figure_recall": (
            sum(s.required_hit for s in scores) / sum(s.required_total for s in scores)
            if sum(s.required_total for s in scores)
            else None
        ),
    }


def print_report(scores: list[Score], label: str) -> None:
    overall = summarize(scores)

    def pct(value: float | None) -> str:
        return "  n/a " if value is None else f"{value:6.1%}"

    print(f"\n{'=' * 72}\n{label} -- {overall['n']} examples\n{'=' * 72}")
    print(f"  Verdict accuracy       {pct(overall['verdict_accuracy'])}")
    print(f"  Arithmetic (all figures exact) {pct(overall['arithmetic_accuracy'])}")
    print(f"  Grounding (no invented figures) {pct(overall['grounding'])}")
    print(f"  Required-figure recall {pct(overall['required_figure_recall'])}")
    if overall["staleness_grounding"] is not None:
        print(f"  Staleness probes       {pct(overall['staleness_grounding'])}"
              "   <- must use pasted thresholds")

    by_kind: dict[str, list[Score]] = defaultdict(list)
    for score in scores:
        by_kind[score.kind].append(score)

    print(f"\n  {'scenario type':<24}{'n':>5}{'verdict':>10}{'arith':>9}{'grounded':>10}")
    for kind in sorted(by_kind):
        group = by_kind[kind]
        stats = summarize(group)
        print(
            f"  {kind:<24}{stats['n']:>5}"
            f"{pct(stats['verdict_accuracy']):>10}"
            f"{pct(stats['arithmetic_accuracy']):>9}"
            f"{pct(stats['grounding']):>10}"
        )

    worst = [s for s in scores if s.verdict_correct is False or s.invented][:3]
    if worst:
        print("\n  Sample failures:")
        for score in worst:
            problem = (
                f"said {read_verdict(score.response)}, expected {score.verdict_expected}"
                if score.verdict_correct is False
                else f"invented {', '.join(f'${v:,}' for v in score.invented[:3])}"
            )
            print(f"    [{score.kind}] {problem}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/dataset/eval.jsonl"))
    parser.add_argument("--model", default=None,
                        help="model name on an OpenAI-compatible endpoint (e.g. Ollama)")
    parser.add_argument("--base-url", default="http://localhost:11434/v1")
    parser.add_argument("--baseline", default=None,
                        help="Anthropic model id to score as a baseline instead")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out", type=Path, default=None, help="write per-example scores")
    parser.add_argument("--label", default=None)
    parser.add_argument("--concurrency", type=int, default=8,
                        help="parallel requests; vLLM batches these efficiently")
    parser.add_argument("--disable-thinking", action="store_true",
                        help="ask Qwen-style chat templates not to emit thinking blocks")
    args = parser.parse_args()

    if not args.model and not args.baseline:
        sys.exit("Pass --model (local endpoint) or --baseline (Anthropic model id).")
    if args.baseline and not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set, so the baseline cannot be scored.")
    if not args.data.exists():
        sys.exit(f"No eval set at {args.data}. Build one with datagen.build_dataset first.")

    rows = [json.loads(line) for line in args.data.open() if line.strip()]
    rows = [r for r in rows if r.get("kind") != "general"]
    if args.limit:
        rows = rows[: args.limit]

    label = args.label or args.model or args.baseline

    # Sequential decode on a 27B dense model runs about a minute per answer; the box
    # serves concurrent requests far more efficiently than serial ones, so fan out.
    # Order is preserved by index; a persistent connection failure aborts the run rather
    # than silently scoring a partial set.
    from concurrent.futures import ThreadPoolExecutor

    def answer(row: dict) -> Score:
        system = row["messages"][0]["content"]
        user = row["messages"][1]["content"]
        response = (
            call_anthropic(args.baseline, system, user)
            if args.baseline
            else call_openai_compatible(
                args.base_url, args.model, system, user,
                disable_thinking=args.disable_thinking,
            )
        )
        return score_response(row, response)

    scores_by_index: dict[int, Score] = {}
    done = 0
    try:
        with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
            futures = {pool.submit(answer, row): i for i, row in enumerate(rows)}
            from concurrent.futures import as_completed

            for future in as_completed(futures):
                scores_by_index[futures[future]] = future.result()
                done += 1
                if done % 20 == 0 or done == len(rows):
                    print(f"  scored {done}/{len(rows)}", file=sys.stderr, flush=True)
    except (urllib.error.URLError, TimeoutError) as exc:
        sys.exit(
            f"Could not reach {args.base_url}: {exc}\n"
            "Is the model being served?"
        )

    scores = [scores_by_index[i] for i in range(len(rows))]
    print_report(scores, label)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w") as handle:
            for score, row in zip(scores, rows, strict=True):
                handle.write(json.dumps({
                    "kind": score.kind,
                    "verdict_expected": score.verdict_expected,
                    "verdict_correct": score.verdict_correct,
                    "required_hit": score.required_hit,
                    "required_total": score.required_total,
                    "invented": score.invented,
                    # Carried through so error analysis can ask whether a flagged figure was
                    # fabricated or merely derived from figures the model was handed. Without
                    # it every flagged value looks equally invented, which is how the first
                    # analysis pass reported a meaningless 100% "not derivable".
                    "allowed_values": row.get("allowed_values", []),
                    "required_values": row.get("required_values", []),
                    "prompt": score.prompt,
                    "response": score.response,
                }) + "\n")
        print(f"\nPer-example scores written to {args.out}")


if __name__ == "__main__":
    main()
