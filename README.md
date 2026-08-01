# NBA Capologist

Fine-tuning a local model into an NBA salary cap specialist — the 2023 CBA, the first and
second aprons, trade legality, exceptions, and roster construction. Trained on a DGX Spark.

## The idea

Front offices live under a rule system that is stable, intricate, and genuinely hard. The
apron era has reshaped the league — Boston dismantled a title roster over it, Phoenix spent
two years trapped by it, and 21 teams were hard-capped for 2026-27. Meanwhile the canonical
free reference for these rules no longer exists: Larry Coon retired without ever updating his
CBA FAQ for the 2023 agreement.

So the rules are stable enough to be worth putting in a model's weights, complicated enough
that a general model gets them wrong, and poorly served by existing tools. Trade machines
check legality without explaining it; frontier models explain fluently while misremembering
whether the matching limit is 100% or 125%.

**What goes in the weights:** CBA terminology, apron mechanics, exception logic, matching
math, the vocabulary and instincts of a capologist.

**What does not:** current salaries. Every threshold moves each July 1, and not predictably —
the 2026-27 cap came in at 6.7% growth when everyone had budgeted the 10% maximum. So the
user pastes a current cap sheet, and the model reasons from what it is handed. No retrieval
system, no pipeline; the training data simply teaches the model that pasted figures always
win over remembered ones.

## How the training data is built

The hard part of a rules domain is that plausible-sounding cap math is usually wrong, and a
model trained on plausible-sounding cap math learns to be confidently wrong. So no figure in
this dataset comes from a language model:

1. **CapEngine** — a deterministic calculator (`capengine/`) — computes the answer and records
   a trace of every step.
2. A frontier model writes the explanation, and is given only the trace to work from.
3. **The verifier** re-extracts every dollar figure from that prose and rejects any number the
   engine did not compute. Failures are sent back with the specific complaint and retried.

Correct arithmetic, natural language, nothing invented. The pattern has precedent —
SYNTHETIC-1, CraftRTL's "correct-by-construction" data, program-trace reasoning supervision.

## Layout

```
capengine/    Deterministic 2023 CBA calculator — the ground truth
datagen/      Scenario sampling, prose generation, numeric verification
training/     Unsloth LoRA/QLoRA on the Spark, plus the runbook
eval/         Scoring against ground truth: verdicts, arithmetic, grounding, staleness
serving/      Merge to GGUF, register with Ollama, demo prompts
docs/         Research reports and the rules reference CapEngine implements
tests/        117 tests, including golden cases against real transactions
```

## Getting started

Every command below runs from the repository root — `uv run python -m datagen.…` resolves
modules relative to the working directory, so it will fail with `No module named 'datagen'`
anywhere else.

```bash
cd ~/Documents/Projects/Fine_tune
```

```bash
uv venv --python 3.12 && uv pip install -e ".[dev]"
```

```bash
uv run pytest
```

Inspect the scenario space without spending anything:

```bash
uv run python -m datagen.generate --dry-run --count 500 --show 2
```

Generate the dataset (needs `ANTHROPIC_API_KEY`; roughly $30–100 for 10k examples):

```bash
uv run python -m datagen.generate --count 10000 --out data/generated/domain.jsonl
```

```bash
uv run python -m datagen.build_dataset --domain data/generated/domain.jsonl --out data/dataset
```

Then move to the Spark — see [training/README.md](training/README.md).

## Evaluation

The fine-tune has to beat both the raw base model and the base model handed the same context.
Four measures, scored programmatically against CapEngine:

| Measure | What it catches |
|---|---|
| Verdict accuracy | Getting legality right |
| Arithmetic | Every required figure stated exactly |
| Grounding | Figures invented that the engine never computed |
| Staleness | Answering from memorized thresholds instead of the pasted ones |

Staleness is reported separately because it is the failure this whole architecture exists to
prevent. Roughly an eighth of the training set is built to defend against it: the prompt
carries thresholds from an invented future season, and the ground truth is computed from
those, so an answer quoting a real-world figure is wrong by construction.

## Model choice

Prototype on **gpt-oss-20b** (NVIDIA's own Spark playbook model, fastest loop), train the real
thing on **Qwen3.6-27B** (Apache 2.0, best open reasoning-per-parameter as of April 2026, and
262K of context for long cap sheets). **gpt-oss-120b** under QLoRA is the fallback ceiling —
being a mixture-of-experts model, it actually serves *faster* than the dense 27B on hardware
whose real constraint is 273 GB/s of memory bandwidth.

## Sourcing

Salary figures and rules are facts, and facts are not copyrightable (*Feist v. Rural*). Two
hard lines regardless: **Sports Reference forbids AI training on its content** and **Spotrac's
terms forbid scraping**, so neither is used. Grounding comes from the league's own published
CBA and CBA 101, with contract data from openly published datasets. Analyst prose is read for
understanding, never trained on — the pipeline generates its own.

## Status

CapEngine and the data pipeline are built and tested. Training, evaluation, and serving
scripts are written and ready to run on the Spark; nothing in this repo has been executed on
one yet. Details in [docs/research/](docs/research/).
