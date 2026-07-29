# Data Sources & Dataset-Construction Prior Art

Research date: 2026-07-28.

## ⛔ Hard sourcing rules

- **Never train on Sports Reference / Basketball-Reference.** Their
  [Data Use page](https://www.sports-reference.com/data_use.html) explicitly forbids using site
  content "for purposes of training, fine-tuning, prompting, or instructing artificial intelligence
  models." Their bot policy also caps at 20 req/min.
- **Do not scrape Spotrac.** [ToS](https://www.spotrac.com/service) bans "data mining, robots, or
  similar data gathering and extraction tools" and commercial reuse. Reference/manual lookup only.
- **Analyst prose is copyrighted** (Hoops Rumors, Third Apron, Coon). Extract the *rules* they
  describe; generate our own prose. This is exactly what the verified-synthetic pipeline does.
- **Facts are free.** *Feist v. Rural*, 499 U.S. 340 (1991): facts are not copyrightable and
  "sweat of the brow" was rejected. Salary figures and rule content are facts.

## ✅ Clean grounding stack

| Source | URL | Use |
|---|---|---|
| Official 2023 CBA PDF (676 pp, verified live) | [ak-static.cms.nba.com](https://ak-static.cms.nba.com/wp-content/uploads/sites/4/2023/06/2023-NBA-Collective-Bargaining-Agreement.pdf) | Primary rule text; generator grounding |
| NBPA mirror | [nbpa.com/cba](https://nbpa.com/cba) | Backup |
| **CBA 101** (league's own ~60 pp plain-English summary) | [cms.nba.com 2024-25 ed.](https://cms.nba.com/wp-content/uploads/sites/4/2024/11/2024-25-CBA-101.pdf) | Best rulebook→readable bridge; league-authored |
| Hoops Rumors glossary series | [glossary](https://www.hoopsrumors.com/hoops-rumors-glossary) | Edge-case interpretation (read, don't copy) |

## ✅ Clean constants / salary data

- **`Mr-Bridge/nba-salary-cap-contracts-2016-2026`** (HF, updated 2026-07-15) — includes
  `cap_tax_aprons.csv`, `max_salaries.csv`, `min_salaries.csv`, `rookie_scale.csv`,
  `cap_projections.csv` through 2031-32. License tag "other" — use, don't redistribute.
- **`gabriel1200/site_Data`** (GitHub, pushed 2026-07-05) — `salary.csv` (contracts through 2030-31),
  `option.csv`, `cap.csv`, `nba_salaries_master.csv` (1991-present, ~35k rows). Scraped from
  Spotrac/RealGM, so don't redistribute.
- Cross-check thresholds by hand against the NBA.com press releases (authoritative).

## Prior art to mine (rule coverage + test cases, not dependencies)

| Repo | Notes |
|---|---|
| [Isingla/nba-trade-analyzer](https://github.com/Isingla/nba-trade-analyzer) | July 2026. Deterministic legality checker for all four tiers under 2025-26 rules, incl. second-apron aggregation bans. **405 tests** — the best source of test cases. |
| [Pieismath/NBA_gm](https://github.com/Pieismath/NBA_gm) | SAT/CP-SAT trade feasibility with hard cap, no-trade clauses, roster limits. |
| [mckaywrigley/nba-cba-ai-chat](https://github.com/mckaywrigley/nba-cba-ai-chat) | 124★, Aug 2023. RAG over the CBA PDF — the best-known prior art, and its limits (can quote Article VII, can't compute a TPE) define our gap. Bundles the CBA PDF. |
| [atlhawksfanatic/NBA-CBA](https://github.com/atlhawksfanatic/NBA-CBA) | Bookdown-structured 2017 CBA — good template for chunking the 2023 text. |

**No mature open-source apron-era cap engine exists.** Building CapEngine is justified.

## Dataset construction — validated prior art

Our pipeline (deterministic calculator → ground truth → LLM prose → programmatic re-verification) is
a published pattern:

- **SYNTHETIC-1** (Prime Intellect, 2025) — 1.4M tasks with programmatic verifiers; reasoning traces
  kept only when verified. [blog](https://www.primeintellect.ai/blog/synthetic-1)
- **Code Execution as Grounded Supervision** ([arXiv:2506.10343](https://arxiv.org/html/2506.10343))
  and **Think Like You Execute** ([arXiv:2512.00127](https://arxiv.org/html/2512.00127)) — ground
  truth from deterministic execution, LLM narrates the trace. Literally our design.
- **CraftRTL** ([arXiv:2409.12993](https://arxiv.org/pdf/2409.12993)) — "correct-by-construction"
  synthetic data for a rule-heavy formal domain.
- **RAFT** ([arXiv:2403.10131](https://arxiv.org/abs/2403.10131)) — train with source chunks +
  distractors and citation-bearing CoT. Informs our rules-QA slice.
- **Logic-RL** ([arXiv:2502.14768](https://arxiv.org/abs/2502.14768)) — 5K procedurally generated,
  auto-checkable puzzles produced out-of-domain generalization. The precedent for our optional GRPO
  phase, with CapEngine as the reward function.

### Format
OpenAI-style `messages` JSONL — TRL-native, Unsloth-convertible. TRL's `SFTTrainer` accepts
`messages` or `prompt`/`completion`; `GRPOTrainer` takes prompt-only. Ground-truth metadata lives in
**extra columns** trainers ignore but our verifier reads.

### Size and mixing
- Unsloth guidance: ≥100 rows minimum, **1,000+ optimal**, quality over quantity.
- LIMA (1k examples) proved *style* transfers cheaply — but we need *procedural correctness*.
- Practitioner evidence favors **5k–20k verified examples** for procedural domains; start ~10k.
- **Catastrophic forgetting:** mix **15–20% general instruct data** (a Dec 2025 study found 1:1
  eliminated forgetting entirely; 5–20% is the common band). LoRA already limits forgetting vs full
  fine-tuning.

## Sports/rules LLM prior art
- **SportQA** (NAACL 2024, [arXiv:2402.15862](https://arxiv.org/abs/2402.15862)) — 70k questions;
  headline finding: LLMs handle trivia but **struggle with scenario-based rules reasoning**. That is
  precisely our target capability.
- **SportR** ([arXiv:2511.06499](https://arxiv.org/html/2511.06499)) — SFT-then-GRPO on sports rules.
- No published fine-tune targets salary-cap/CBA reasoning. **The niche is open.**
