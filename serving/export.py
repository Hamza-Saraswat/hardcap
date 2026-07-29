"""Merge the adapter, quantize to GGUF, and register the model with Ollama.

    python serving/export.py --adapter outputs/main/adapter --preset main

Q8_0 by default. Q4 would roughly double throughput, but this model's job is arithmetic on
figures a general manager is going to act on, and quantization error there is worse than
waiting. Benchmark both if you like -- the eval harness will tell you what the speed cost
bought or lost.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datagen.prompts import SYSTEM_PROMPT
from training.train_lora import PRESETS

MODELFILE_TEMPLATE = """\
FROM {gguf}

PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER num_ctx {context}

SYSTEM \"\"\"{system}\"\"\"
"""


def merge_and_quantize(adapter: Path, base_model: str, out_dir: Path, quant: str) -> Path:
    from unsloth import FastLanguageModel

    print(f"Loading {base_model} and merging {adapter}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(adapter),
        max_seq_length=8192,
        load_in_4bit=False,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Writing {quant} GGUF to {out_dir}")
    model.save_pretrained_gguf(str(out_dir), tokenizer, quantization_method=quant)

    ggufs = sorted(out_dir.glob("*.gguf"))
    if not ggufs:
        raise SystemExit(f"No GGUF was produced in {out_dir}")
    return ggufs[-1]


def write_modelfile(gguf: Path, context: int, path: Path) -> None:
    path.write_text(
        MODELFILE_TEMPLATE.format(
            gguf=gguf.resolve(),
            context=context,
            system=SYSTEM_PROMPT,
        )
    )
    print(f"Wrote {path}")


def register_with_ollama(modelfile: Path, name: str) -> None:
    print(f"Registering '{name}' with Ollama")
    try:
        subprocess.run(["ollama", "create", name, "-f", str(modelfile)], check=True)
    except FileNotFoundError:
        print("Ollama is not installed here; the Modelfile is ready to use elsewhere.")
        return
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"ollama create failed: {exc}") from exc
    print(f"\nTry it:  ollama run {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--preset", default="main", choices=sorted(PRESETS))
    parser.add_argument("--out", type=Path, default=Path("outputs/gguf"))
    parser.add_argument("--quant", default="q8_0",
                        help="q8_0 preserves arithmetic; q4_k_m is about twice as fast")
    parser.add_argument("--name", default="capologist")
    parser.add_argument("--modelfile-only", action="store_true",
                        help="skip merging and just rewrite the Modelfile for an existing GGUF")
    args = parser.parse_args()

    preset = PRESETS[args.preset]
    modelfile = args.out / "Modelfile"

    if args.modelfile_only:
        ggufs = sorted(args.out.glob("*.gguf"))
        if not ggufs:
            raise SystemExit(f"No GGUF found in {args.out}")
        gguf = ggufs[-1]
    else:
        if not args.adapter.exists():
            raise SystemExit(f"No adapter at {args.adapter}. Train one first.")
        gguf = merge_and_quantize(args.adapter, preset.model, args.out, args.quant)

    write_modelfile(gguf, preset.max_seq_length, modelfile)
    register_with_ollama(modelfile, args.name)


if __name__ == "__main__":
    main()
