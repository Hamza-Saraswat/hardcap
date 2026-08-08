"""Publish the trained adapter to the Hugging Face Hub.

    HF_TOKEN=hf_... python -m serving.push_to_hub --repo HamzaSaraswat/hardcap-qwen3.6-27b-lora

Uploads the LoRA adapter (~640MB) plus a model card carrying the real eval numbers. The
adapter alone is useless without the base model, which is the point -- it is a small diff
against `unsloth/Qwen3.6-27B`, and anyone who wants it pulls both.

Needs a token with **write** permission from https://huggingface.co/settings/tokens.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

BASE_MODEL = "unsloth/Qwen3.6-27B"

CARD = """\
---
base_model: {base}
library_name: peft
license: apache-2.0
tags:
  - lora
  - basketball
  - salary-cap
  - domain-adaptation
---

# hardcap — NBA salary cap analyst (LoRA)

A LoRA adapter turning [`{base}`]({base_url}) into a specialist on the NBA's 2023
Collective Bargaining Agreement: trade legality, the first and second aprons, exceptions,
the stretch provision, and roster construction.

Trained on an NVIDIA DGX Spark. Source, dataset generator, and evaluation harness:
<https://github.com/Hamza-Saraswat/hardcap>

## The design bet

Rules are stable until at least 2029; salary figures change daily. So the rules go in the
weights and **the numbers stay in the prompt** — you paste a current cap sheet and the model
reasons over what it is handed. About an eighth of the training data uses invented future
thresholds where answering from memory is wrong by construction, specifically to train the
"read, don't recall" reflex.

## Results

499 held-out questions, graded programmatically against a deterministic CBA calculator
(temperature 0, thinking disabled):

| Measure | Base {base_short} | **This adapter** |
|---|---|---|
| Verdict accuracy (legal / illegal) | 58.0% | **78.0%** |
| Arithmetic (every required figure exact) | 53.5% | **54.3%** |
| Grounding (no invented figures) | 3.8% | **31.7%** |
| Staleness probes (pasted figures must win) | 3.4% | **32.2%** |

Strong on rule application — exception eligibility 97.8% verdicts / 100% arithmetic; buyout
market, draft penalties, and exception surveys at or near 100%. Weak on long chained
arithmetic (multi-bracket tax bills), the familiar limit of doing multi-step multiplication
in-weights; the fix is tool use, not more training.

## Training data

6,240 examples, none of them written freehand by a language model. A deterministic engine
computes each answer and records every step; a narrator writes the prose; a verifier rejects
any output containing a figure the engine never computed. Players are invented — attaching
fabricated salaries to real people would teach false facts, which is the exact failure this
design avoids.

## Usage

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base = AutoModelForCausalLM.from_pretrained("{base}", dtype="bfloat16", device_map="auto")
model = PeftModel.from_pretrained(base, "{repo}")
tokenizer = AutoTokenizer.from_pretrained("{repo}")
```

Or serve it with vLLM, which hot-swaps adapters without reloading the base:

```bash
vllm serve {base} --enable-lora \\
  --lora-modules capologist={repo} --max-lora-rank 32
```

Use the system prompt from the repository (`datagen/prompts.py`) — the behavior described
there is what the model was trained against.

## Limitations

- Verify multi-step sums; single-figure arithmetic is reliable, long chains drift.
- Knows the **2023** CBA. A future agreement makes it wrong, by design — retraining is cheap.
- Not affiliated with or endorsed by the NBA.

## Training details

LoRA r=32, alpha=64, BF16, on q/k/v/o and gate/up/down projections. 2 epochs, lr 1e-4 cosine,
effective batch 16, sequence length 8192, ~8.5h on one DGX Spark (GB10).

Loss is masked to response tokens only. An earlier run without that masking scored **26%**
on verdicts — worse than the base model — because most of the gradient went into reproducing
an identical system prompt and predicting random cap-sheet salaries. That one flag was worth
52 points.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="e.g. HamzaSaraswat/hardcap-qwen3.6-27b-lora")
    parser.add_argument("--adapter", type=Path, default=Path("outputs/main/adapter"))
    parser.add_argument("--private", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="write the card, upload nothing")
    args = parser.parse_args()

    if not args.adapter.exists():
        sys.exit(f"No adapter at {args.adapter}")

    card = CARD.format(
        base=BASE_MODEL,
        base_url=f"https://huggingface.co/{BASE_MODEL}",
        base_short=BASE_MODEL.split("/")[-1],
        repo=args.repo,
    )
    (args.adapter / "README.md").write_text(card)
    print(f"model card written to {args.adapter}/README.md")

    if args.dry_run:
        print("\n--- card preview ---\n")
        print(card[:1500])
        return

    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit(
            "HF_TOKEN is not set.\n"
            "Create a token with WRITE permission at https://huggingface.co/settings/tokens\n"
            "then rerun with:  HF_TOKEN=hf_... python -m serving.push_to_hub --repo ..."
        )

    from huggingface_hub import HfApi

    api = HfApi(token=token)
    api.create_repo(args.repo, repo_type="model", private=args.private, exist_ok=True)
    print(f"uploading {args.adapter} -> {args.repo} …")
    api.upload_folder(
        folder_path=str(args.adapter),
        repo_id=args.repo,
        repo_type="model",
        commit_message="Add hardcap LoRA adapter: NBA salary cap analyst",
    )
    print(f"\ndone: https://huggingface.co/{args.repo}")


if __name__ == "__main__":
    main()
