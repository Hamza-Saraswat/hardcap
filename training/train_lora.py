"""LoRA / QLoRA fine-tuning on a DGX Spark, via Unsloth.

Run this inside the Unsloth DGX Spark container, not on bare metal -- see training/README.md.

    python training/train_lora.py --preset prototype   # gpt-oss-20b, QLoRA, fast loop
    python training/train_lora.py --preset main        # Qwen3.6-27B, BF16 LoRA

Hardware notes that shaped the defaults, all specific to GB10:

  - BF16 only. FP16 has produced inf/NaN on this chip.
  - SDPA attention. Upstream flash-attn has no aarch64 wheels and its CUDA 12 linkage
    breaks against CUDA 13; SDPA is reportedly faster on Blackwell regardless.
  - Small per-device batches with gradient accumulation. Memory use on unified LPDDR5X
    scales super-linearly with batch size -- one report went from 47 GB at batch 8 to
    81 GB at batch 16 on a 0.6B model.
  - Frequent checkpoints. The 128 GB of unified memory has no ECC, so a long unattended
    run is worth protecting against a silent corruption forcing a restart.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Preset:
    name: str
    model: str
    load_in_4bit: bool
    max_seq_length: int
    lora_r: int
    lora_alpha: int
    learning_rate: float
    per_device_batch_size: int
    gradient_accumulation_steps: int
    epochs: float
    chat_template: str | None = None
    target_modules: list[str] = field(
        default_factory=lambda: [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ]
    )


PRESETS = {
    # Validates the whole loop cheaply. This is NVIDIA's own Spark playbook model, so the
    # stack is known-good, and it serves at 58-82 tok/s for quick manual inspection.
    "prototype": Preset(
        name="prototype",
        model="unsloth/gpt-oss-20b-unsloth-bnb-4bit",
        load_in_4bit=True,
        max_seq_length=4096,
        lora_r=16,
        lora_alpha=32,
        learning_rate=2e-4,
        per_device_batch_size=2,
        gradient_accumulation_steps=8,
        epochs=2,
        chat_template="harmony",
    ),
    # The quality run. Dense 27B fits comfortably in BF16 with LoRA, and the long context
    # matters because a pasted cap sheet plus a multi-team trade gets long.
    "main": Preset(
        name="main",
        model="unsloth/Qwen3.6-27B",
        load_in_4bit=False,
        max_seq_length=8192,
        lora_r=32,
        lora_alpha=64,
        learning_rate=1e-4,
        per_device_batch_size=1,
        gradient_accumulation_steps=16,
        epochs=2,
    ),
    # Fallback if 27B evals fall short. MoE means it serves faster than the dense 27B
    # despite being four times larger -- exactly what 273 GB/s of bandwidth rewards.
    "ceiling": Preset(
        name="ceiling",
        model="unsloth/gpt-oss-120b-unsloth-bnb-4bit",
        load_in_4bit=True,
        max_seq_length=4096,
        lora_r=16,
        lora_alpha=32,
        learning_rate=1e-4,
        per_device_batch_size=1,
        gradient_accumulation_steps=16,
        epochs=1,
        chat_template="harmony",
    ),
    # Proves the loop on the exact model the main run uses -- 4-bit so it loads fast and
    # peaks low. Meant to be invoked with --limit 200 --max-steps 40: not for quality, for
    # finding container/template/OOM problems in 25 minutes instead of hour 4.
    "smoke": Preset(
        name="smoke",
        model="unsloth/Qwen3.6-27B",
        load_in_4bit=True,
        max_seq_length=4096,
        lora_r=16,
        lora_alpha=32,
        learning_rate=2e-4,
        per_device_batch_size=1,
        gradient_accumulation_steps=8,
        epochs=1,
    ),
}


def load_dataset(path: Path, limit: int | None = None):
    from datasets import Dataset

    rows = [json.loads(line) for line in path.open() if line.strip()]
    if not rows:
        raise SystemExit(f"No training rows in {path}")
    if limit:
        rows = rows[:limit]
    return Dataset.from_list([{"messages": r["messages"]} for r in rows])


def train(
    preset: Preset,
    data_path: Path,
    output_dir: Path,
    resume: bool,
    limit: int | None = None,
    max_steps: int | None = None,
) -> None:
    # Imported here so --list-presets and --help work outside the training container.
    # Unsloth must come first: it patches transformers/trl at import time, and importing
    # them before it silently drops the optimizations.
    from unsloth import FastLanguageModel  # isort: skip

    import torch
    from trl import SFTConfig, SFTTrainer

    print(f"Preset '{preset.name}': {preset.model}")
    print(f"  {'QLoRA (4-bit)' if preset.load_in_4bit else 'LoRA (BF16 base)'}, "
          f"r={preset.lora_r}, seq={preset.max_seq_length}")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=preset.model,
        max_seq_length=preset.max_seq_length,
        load_in_4bit=preset.load_in_4bit,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
        # GB10 reports its memory as N/A to nvidia-smi, so automatic device mapping
        # concludes the GPU has no room and spills layers to CPU -- which the 4-bit
        # quantizer then refuses. Unified memory means everything fits on device 0 by
        # definition; say so explicitly.
        device_map={"": 0},
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=preset.lora_r,
        lora_alpha=preset.lora_alpha,
        lora_dropout=0.0,
        target_modules=preset.target_modules,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=0,
    )

    if preset.chat_template:
        from unsloth.chat_templates import get_chat_template

        tokenizer = get_chat_template(tokenizer, chat_template=preset.chat_template)

    dataset = load_dataset(data_path, limit=limit)
    print(f"  {len(dataset)} training examples"
          + (" (limited from the full set)" if limit else ""))
    if max_steps:
        print(f"  capped at {max_steps} steps")

    effective_batch = preset.per_device_batch_size * preset.gradient_accumulation_steps
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            output_dir=str(output_dir),
            per_device_train_batch_size=preset.per_device_batch_size,
            gradient_accumulation_steps=preset.gradient_accumulation_steps,
            num_train_epochs=preset.epochs,
            max_steps=max_steps or -1,
            learning_rate=preset.learning_rate,
            lr_scheduler_type="cosine",
            warmup_ratio=0.03,
            optim="adamw_8bit",
            weight_decay=0.01,
            bf16=True,
            fp16=False,
            logging_steps=5,
            save_strategy="steps",
            save_steps=50,
            save_total_limit=3,
            max_seq_length=preset.max_seq_length,
            dataset_num_proc=2,
            report_to="none",
            seed=0,
        ),
    )

    print(f"  effective batch size {effective_batch}, "
          f"checkpointing every 50 steps to {output_dir}")
    trainer.train(resume_from_checkpoint=resume or None)

    adapter_dir = output_dir / "adapter"
    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))
    print(f"\nAdapter saved to {adapter_dir}")
    print("Next: python serving/export.py --adapter", adapter_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", default="main", choices=sorted(PRESETS))
    parser.add_argument("--data", type=Path, default=Path("data/dataset/train.jsonl"))
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--list-presets", action="store_true")
    parser.add_argument("--limit", type=int, default=None,
                        help="train on only the first N examples (smoke tests)")
    parser.add_argument("--max-steps", type=int, default=None,
                        help="stop after N optimizer steps regardless of epochs")
    args = parser.parse_args()

    if args.list_presets:
        for name, preset in PRESETS.items():
            mode = "QLoRA 4-bit" if preset.load_in_4bit else "LoRA BF16"
            print(f"{name:12} {preset.model:45} {mode:12} seq={preset.max_seq_length}")
        return

    preset = PRESETS[args.preset]
    output = args.output or Path(f"outputs/{preset.name}")
    if not args.data.exists():
        raise SystemExit(
            f"No training data at {args.data}.\n"
            "Generate it first:  python -m datagen.generate --count 10000 ...\n"
            "then                python -m datagen.build_dataset ..."
        )
    train(preset, args.data, output, args.resume, limit=args.limit,
          max_steps=args.max_steps)


if __name__ == "__main__":
    main()
