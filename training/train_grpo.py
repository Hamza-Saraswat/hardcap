"""GRPO polish on top of the SFT checkpoint, graded by CapEngine.

    python training/train_grpo.py --adapter outputs/main-v2/adapter --steps 400

SFT is imitation: show the model good answers and it learns to write like them. GRPO is
practice with a grader -- the model writes several answers to the same prompt, each is
scored, and answers above the group average are reinforced while those below are pushed
away. It needs a grader that is fast, automatic, and never wrong, which is exactly what
CapEngine is, and why this project was a natural fit for it from the start.

What GRPO can and cannot do: it sharpens behavior the model already has. It will not install
a capability that was missing from the SFT data -- that is what the v2 slices were for. So
this runs last, on prompts where v1 measurably struggled.

Rewards are deliberately additive and small. A single dominant term invites reward hacking:
reward only "no invented figures" and the model learns to state no figures at all.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from datagen.verify import dollar_figures
from eval.harness import read_verdict, strip_thinking

# Weights sum to 1.0 so a perfect answer scores 1.0 and the numbers stay readable in logs.
W_VERDICT = 0.35
W_REQUIRED = 0.25
W_GROUNDED = 0.30
W_FORM = 0.10

_LOOP_WINDOW = 6
_LOOP_THRESHOLD = 4


def loop_penalty(text: str) -> float:
    """1.0 when the answer repeats a long phrase over and over.

    The degenerate loop was v1's most embarrassing failure and the eval could not see it.
    Here it is priced directly: a looping answer loses everything.
    """
    words = text.split()
    if len(words) < _LOOP_WINDOW * 2:
        return 0.0
    counts: dict[str, int] = {}
    for i in range(len(words) - _LOOP_WINDOW):
        gram = " ".join(words[i:i + _LOOP_WINDOW])
        counts[gram] = counts.get(gram, 0) + 1
    return 1.0 if max(counts.values()) >= _LOOP_THRESHOLD else 0.0


def score_completion(text: str, row: dict) -> tuple[float, dict]:
    """Grade one candidate answer. Returns the total and its parts, for logging."""
    answer = strip_thinking(text)
    parts = {"verdict": 0.0, "required": 0.0, "grounded": 0.0, "form": 0.0, "loop": 0.0}

    if not answer.strip():
        return 0.0, parts
    if loop_penalty(answer):
        parts["loop"] = 1.0
        return 0.0, parts

    expected = row.get("verdict")
    normalized = {"ALLOWED": "LEGAL", "NOT ALLOWED": "ILLEGAL"}.get(expected, expected)
    if normalized:
        parts["verdict"] = 1.0 if read_verdict(answer) == normalized else 0.0
    else:
        # Nothing to check, so do not punish or reward -- award the term in full and let the
        # other three carry the signal.
        parts["verdict"] = 1.0

    claimed = dollar_figures(answer)
    required = row.get("required_values") or []
    parts["required"] = (
        sum(1 for v in required if v in claimed) / len(required) if required else 1.0
    )

    allowed = set(row.get("allowed_values") or [])
    invented = [v for v in claimed if v not in allowed and v >= 1000]
    if not claimed:
        # An answer that names no figures cannot invent one. Do not pay full marks for
        # silence, or the model learns that saying nothing is the safest play.
        parts["grounded"] = 0.5 if required else 1.0
    else:
        parts["grounded"] = max(0.0, 1.0 - len(invented) / len(claimed))

    # Shape: a verdict question should open with a verdict, and answers should not trail off.
    form = 1.0
    if normalized and not re.search(r"\*\*verdict:", answer[:200], re.IGNORECASE):
        form -= 0.5
    if len(answer) < 120:
        form -= 0.5
    parts["form"] = max(0.0, form)

    total = (
        W_VERDICT * parts["verdict"]
        + W_REQUIRED * parts["required"]
        + W_GROUNDED * parts["grounded"]
        + W_FORM * parts["form"]
    )
    return total, parts


def build_reward(rows_by_prompt: dict[str, dict]):
    """TRL calls this with a batch of completions; look each prompt's ground truth back up."""

    def reward(prompts, completions, **kwargs) -> list[float]:
        scores = []
        for prompt, completion in zip(prompts, completions, strict=False):
            text = completion if isinstance(completion, str) else completion[0]["content"]
            row = rows_by_prompt.get(prompt if isinstance(prompt, str) else str(prompt), {})
            total, _ = score_completion(text, row)
            scores.append(total)
        return scores

    reward.__name__ = "capengine_reward"
    return reward


def load_prompts(
    path: Path, limit: int | None = None, exclude: Path | None = None
) -> tuple[list[dict], dict[str, dict]]:
    """Prompts GRPO will practice on, preferring the categories v1 got wrong.

    Reads the generated file rather than the built train split: the trainer's view keeps
    only `messages`, and grading needs the ground truth that sits alongside it. Anything
    appearing in the eval set is dropped, so practice never touches the exam.
    """
    rows = [json.loads(line) for line in path.open() if line.strip()]

    held_out: set[str] = set()
    if exclude and exclude.exists():
        for line in exclude.open():
            if line.strip():
                row = json.loads(line)
                user = next(
                    (m["content"] for m in row["messages"] if m["role"] == "user"), None
                )
                if user:
                    held_out.add(user)

    # Verdict-bearing and figure-heavy prompts carry the most signal per step.
    rows = [
        r for r in rows
        if (r.get("verdict") or r.get("required_values"))
        and next((m["content"] for m in r["messages"] if m["role"] == "user"), "")
        not in held_out
    ]
    if limit:
        rows = rows[:limit]

    dataset, lookup = [], {}
    for row in rows:
        user = next(m["content"] for m in row["messages"] if m["role"] == "user")
        system = row["messages"][0]["content"]
        dataset.append({"prompt": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]})
        lookup[user] = row
    return dataset, lookup


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", type=Path, default=Path("outputs/main-v2/adapter"))
    parser.add_argument("--data", type=Path,
                        default=Path("data/generated/combined_v2.jsonl"))
    parser.add_argument("--exclude", type=Path,
                        default=Path("data/dataset_v2/eval.jsonl"),
                        help="prompts to keep out of practice: the eval set")
    parser.add_argument("--output", type=Path, default=Path("outputs/grpo"))
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--generations", type=int, default=8)
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument("--dry-run", action="store_true",
                        help="score a few known answers to sanity-check the reward")
    args = parser.parse_args()

    dataset_rows, lookup = load_prompts(args.data, args.limit, args.exclude)
    print(f"{len(dataset_rows)} practice prompts loaded")

    if args.dry_run:
        # Reward functions are the easiest thing in RL to get quietly backwards, so check
        # the ordering on real training answers before spending a night on it.
        print("\nreward check on real training answers:")
        for row in list(lookup.values())[:5]:
            gold = row["messages"][-1]["content"]
            total, parts = score_completion(gold, row)
            print(f"  gold      {total:.3f}  {parts}  [{row['kind']}]")
        row = next(iter(lookup.values()))
        for label, text in (
            ("empty", ""),
            ("loop", "the second apron is the line " * 20),
            ("no figures", "It is fine. " * 20),
            ("wrong figure", "**Verdict: LEGAL.** The total is $99,999,999. " * 4),
        ):
            total, parts = score_completion(text, row)
            print(f"  {label:12} {total:.3f}  {parts}")
        return

    import torch
    from trl import GRPOConfig, GRPOTrainer
    from unsloth import FastLanguageModel  # isort: skip

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(args.adapter),
        max_seq_length=8192,
        load_in_4bit=False,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
        device_map={"": 0},
    )
    from datasets import Dataset

    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=[build_reward(lookup)],
        train_dataset=Dataset.from_list(dataset_rows),
        args=GRPOConfig(
            output_dir=str(args.output),
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            num_generations=args.generations,
            max_prompt_length=4096,
            max_completion_length=768,
            max_steps=args.steps,
            learning_rate=5e-6,
            lr_scheduler_type="cosine",
            warmup_ratio=0.03,
            optim="adamw_8bit",
            bf16=True,
            fp16=False,
            logging_steps=5,
            save_steps=50,
            save_total_limit=3,
            report_to="none",
            seed=0,
        ),
    )
    trainer.train()

    adapter_dir = args.output / "adapter"
    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))
    print(f"\nGRPO adapter saved to {adapter_dir}")
    print("Evaluate it against the SFT checkpoint before adopting it.")


if __name__ == "__main__":
    main()
