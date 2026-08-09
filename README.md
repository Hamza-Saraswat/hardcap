# hardcap

Fine-tuning a local model into a basketball salary cap specialist — the 2023 CBA, the first
and second aprons, trade legality, exceptions, and roster construction. Trained on a DGX Spark.

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
this dataset is produced by a language model:

1. **CapEngine** — a deterministic calculator (`capengine/`) — computes the answer and records
   a trace of every step.
2. A narrator writes the explanation, working only from that trace. This is either a template
   layer (free, offline) or a frontier model (more varied prose).
3. **The verifier** re-extracts every dollar figure from the prose and rejects any number the
   engine did not compute.

Correct arithmetic, natural language, nothing invented. The pattern has precedent —
SYNTHETIC-1, CraftRTL's "correct-by-construction" data, program-trace reasoning supervision.

## Layout

```
capengine/    Deterministic 2023 CBA calculator — the ground truth
datagen/      Scenario sampling, narration, numeric verification
training/     Unsloth LoRA/QLoRA on the Spark, plus the runbook
eval/         Scoring against ground truth: verdicts, arithmetic, grounding, staleness
serving/      Merge to GGUF, register with Ollama, demo prompts
docs/         Research reports and the rules reference CapEngine implements
tests/        172 tests, including golden cases against real transactions
```

## Getting started

Every command runs from the repository root — `uv run python -m datagen.…` resolves modules
relative to the working directory and will fail with `No module named 'datagen'` anywhere else.

```bash
uv venv --python 3.12 && uv pip install -e ".[dev]"
```

```bash
uv run python -m pytest
```

Look at the scenario space, including a full example with its computation trace:

```bash
uv run python -m datagen.generate --dry-run --count 500 --show 2
```

Build the dataset. This needs no API key and no network, and takes about ten seconds:

```bash
uv run python -m datagen.generate --local --count 6000 --out data/generated/domain.jsonl
```

```bash
uv run python -m datagen.build_dataset --domain data/generated/domain.jsonl --out data/dataset
```

Because generation is seeded, the dataset reproduces exactly — which is why 15MB of it isn't
committed. A readable slice lives in `data/sample/`.

Dropping `--local` (with `ANTHROPIC_API_KEY` set) has a frontier model write the prose
instead. It reads more naturally and costs roughly $30–100 for 10k examples; the arithmetic
is identical either way, since both paths are verified against the same traces.

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
prevent. Roughly an eighth of the training set defends against it: the prompt carries
thresholds from an invented future season, and ground truth is computed from those, so an
answer quoting a real-world figure is wrong by construction.

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
CBA and CBA 101. Analyst prose is read for understanding, never trained on — the pipeline
generates its own.

Players in the training data are invented. Attaching fabricated salaries to real players
would teach the model false facts about the league, which is the exact failure this
architecture exists to avoid. Real names appear only in the tests, with their real figures.

## Results

Trained on a DGX Spark (Qwen3.6-27B, BF16 LoRA r=32, 2 epochs, ~8.5h). Scored on 499
held-out questions against CapEngine's ground truth, thinking disabled, temperature 0:

| Measure | Base Qwen3.6-27B | Fine-tune (full-seq loss) | **Fine-tune (response-masked)** |
|---|---|---|---|
| Verdict accuracy | 58.0% | 26.1% | **78.0%** |
| Arithmetic (exact figures) | 53.5% | 41.9% | **54.3%** |
| Grounding (no invented figures) | 3.8% | 35.3% | **31.7%** |
| Staleness probes | 3.4% | 32.2% | **32.2%** |

The middle column is the honest lesson: the first run spread loss over the whole rendered
text, spending ~90% of the gradient on boilerplate and random cap-sheet salaries. Masking
loss to response tokens only — one flag — was worth +52 verdict points.

Where the model is now strong: rule application (exception eligibility 97.8% verdicts / 100%
arithmetic; buyouts, draft penalties, exception surveys at or near 100%). Per-example scores
live in `eval/results/`.

### v2 in progress

Error analysis on v1's per-example results (`docs/error-analysis-v1.md`) redirected the next
round. The assumption going in was that most "invented" figures would turn out to be correct
arithmetic the whitelist simply missed, so a calculator would fix grounding. It would not —
only ~7% are derivable by simple operations, and that is a floor rather than a measurement.
Grounding is a genuine model problem across every scenario type, so v2 addresses it with its
own data slice rather than leaning on tools.

v2 adds a `calc` tool (AST-evaluated, never `eval()`), 3,500 rows across five slices each
traceable to a measured failure bucket, a GRPO pass graded by CapEngine, and a playground
with multi-turn chat, cap-sheet upload, and feedback logging.

Two known weaknesses of v1, both reproducible:

- **Chained arithmetic.** Multi-bracket tax bills score 4.7%. On a real Denver sheet it got
  every rule right and still summed the payroll $617,500 wrong. This is the familiar limit of
  doing multi-step multiplication in-weights; the fix is tool use, and CapEngine already is
  that calculator.
- **Enumeration without a cap sheet.** "Which exceptions do we have?" asked with no sheet
  pasted can collapse into a repetition loop; the same question with a sheet answers cleanly.
  Exception-survey training examples always carried a cap sheet, so the no-context version is
  out of distribution. A repetition penalty does not fix it — more varied training data would.

The three-way debugging story — including the run that took the whole machine down — is in
[docs/journey.md](docs/journey.md). Research background in [docs/research/](docs/research/).
