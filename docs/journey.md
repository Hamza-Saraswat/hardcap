# The journey: fine-tuning a salary-cap specialist, including everything that broke

A chronological, honest account of this project — kept because the failures taught more than
the successes. Dates: July 28 – August 3, 2026. Hardware: one DGX Spark (GB10, 128GB unified
memory). Model: Qwen3.6-27B, BF16 LoRA.

## The premise

Split knowledge by shelf life. CBA rules are stable until at least 2029 → bake them into the
model's weights. Salaries change daily → never bake them in; the user pastes a current cap
sheet and the model reasons over what it is handed. Every design decision follows from that
split.

## Phase 1 — ground truth before AI

Built CapEngine, a deterministic calculator for the 2023 CBA, before any model touched
anything. Rationale: wrong cap math sounds exactly like right cap math, so training data
written freehand by an AI would contain confident errors, and the model would learn them.
Validated the engine against reality — given only the rules, it independently reproduced the
~$13.8M giveback from Bradley Beal's 2025 waive-and-stretch and the draft-pick consequences
of the era's real transactions. 200+ tests.

## Phase 2 — manufacturing the textbook

6,240 examples: CapEngine invents a scenario and computes the truth → a narrator (templates
plus agent-written batches) writes the prose → a verifier re-extracts every dollar figure
and rejects anything the engine never computed. Fake player names throughout, so the model
learns reasoning rather than false facts about real people. One example in eight uses
invented future thresholds where answering from memory is wrong by construction — the
"read, don't recall" reflex, turned into homework.

Bugs found by adversarial use, not by the test suite: rosters with duplicate player names
that made trades ambiguous; generated contracts exceeding the legal maximum salary; a
whitelist parser that read CSV rows as concatenated garbage (which would have *accepted* a
hallucinated $334M figure); a verdict checker whose 400-character scan punished innocent
phrasing. The verifier needed verifying.

## Phase 3 — the baseline, taken before touching anything

The un-tuned model took the 499-question exam first. 58% on verdicts, and it invented at
least one dollar figure in 96% of answers. That number is why the project exists — and
without taking it first, nothing after it could be proven.

## Phase 4 — seven landmines before step one

The smoke test (25 minutes, 200 examples) failed four times, each a different real problem:
a Docker image whose entrypoint silently ignores your command and boots Jupyter; a
transformers too old for the model, whose "upgrade" was silently refused (PEP 668), and
which couldn't move alone anyway because unsloth pins it; a probe container run without GPU
access; a chip that reports its memory as N/A, sending layers to CPU and making the 4-bit
loader refuse; a trainer API that now demands pre-rendered text. Twenty minutes per failure
instead of a dead overnight run. Fifth attempt: loss 1.09 → 0.57. Green.

## Phase 5 — the night the machine died

Killed the eval server's terminal; the server itself kept running, holding 81GB of unified
memory. Launched training on top: 54GB of weights into a pool that didn't have them. On
unified-memory hardware, exhaustion starves the OS itself — the box dropped off the network
and needed the power button. Lessons burned in as code: servers get names and are stopped by
name; training refuses to start unless memory is verifiably free; containers run inside
hard memory caps so the worst case is a killed process. (Also: when the machine "vanished"
again later, it was the laptop having hopped wifi networks. Check the boring explanation
first.)

## Phase 6 — the fine-tune that failed its exam

First full run: loss 0.39, clean curve, and then 26% verdict accuracy — worse than base.
Reading actual failed answers showed training phrases with scrambled logic and a dropped
verdict format. Ruled out a chat-template mismatch byte-for-byte, which left the real bug:
loss had been computed over the entire rendered text, so ~90% of the gradient went into
reproducing an identical system prompt and predicting random cap-sheet salaries — literally
practicing hallucination. The proof came from the fix itself: with response-only masking,
the startup line read "10.2% of tokens carry loss."

## Phase 7 — the retrain

Same data, same steps, one flag changed. Verdicts 26% → 78% (base: 58%). Grounding 8× base,
staleness 9× base, rule-application categories at or near 100%. Chained arithmetic (tax
brackets) remains weak — the structural LLM limitation, whose real fix is handing the model
a calculator at inference. CapEngine is already that calculator; that is v2.

## The five principles

1. **Split knowledge by shelf life.** Stable → weights. Volatile → prompt.
2. **Never let the AI grade its own homework.** Ground truth comes from code.
3. **Baseline first.** No before-photo, no proof.
4. **Fail small on purpose.** Smoke tests turn overnight disasters into 20-minute fixes.
5. **Trust evidence, not vibes.** Watch step counters and memory, not "it's running."
