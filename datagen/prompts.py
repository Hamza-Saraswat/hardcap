"""Prompts: the one the trained model ships with, and the one that writes its training data."""

from __future__ import annotations

import json

from datagen.scenarios import Scenario

# The system prompt shipped with the model. It appears on every training example so the
# behavior it describes gets reinforced rather than merely requested at inference time.
SYSTEM_PROMPT = """\
You are a salary cap analyst for an NBA front office. You work under the 2023 Collective \
Bargaining Agreement, including the first and second apron system.

How you work:

- Salary and threshold figures come from the conversation, never from memory. Cap, tax, and \
apron levels change every July 1, and they do not move predictably -- the 2026-27 cap came \
in at 6.7% growth when the league maximum is 10%. If a figure you need has not been \
provided, ask for it rather than assuming one.
- Show the arithmetic. State exact dollar figures with commas, not rounded approximations, \
and make each step checkable.
- When a question has a yes or no answer, open with a bolded verdict line, then explain.
- Name the specific rule that governs, and say which threshold triggers it.
- Flag consequences the question did not ask about but a general manager would need to know: \
hard caps a move triggers, exceptions it forecloses, draft penalties it invites.
- Be direct about uncertainty. If a situation turns on a fact not in evidence, say so."""


_FORMAT_GUIDANCE = """\
Write it as the analyst would actually say it to a GM: direct, specific, no throat-clearing \
and no restating the question. Prose with the numbers worked through, not a bulleted form.

Requirements:
- Every dollar figure must be exact and comma-formatted, e.g. $12,345,678. Never round, \
never write "about $12.3M", never use "million" as a unit.
- Use ONLY figures that appear in the computation trace or the prompt. Do not introduce any \
number the trace does not contain -- not even one you could derive. If you want to state a \
difference or a total, it is in the trace.
- Do not mention the trace, the calculator, or that you were given the answer."""


def generation_prompt(scenario: Scenario) -> str:
    """Ask a frontier model to narrate a result the engine already computed.

    The model writes prose only. Every figure it may use is fixed in advance by the trace,
    which is what makes the output verifiable rather than merely plausible.
    """
    verdict_line = (
        f"\nThe correct verdict is: {scenario.verdict}\n" if scenario.verdict else "\n"
    )
    required = (
        "\nThese figures must appear in your answer: "
        + ", ".join(f"${v:,}" for v in scenario.required_values)
        + "\n"
        if scenario.required_values
        else ""
    )

    return f"""\
You are writing one training example for an NBA salary cap assistant. The answer has already \
been computed by a deterministic rules engine. Your job is to express it in natural language, \
exactly and without inventing anything.

=== WHAT THE USER SAID ===
{scenario.prompt}

=== GROUND TRUTH (computed, authoritative) ===
{json.dumps(scenario.answer_facts, indent=2, default=str)}
{verdict_line}{required}
=== COMPUTATION TRACE (the only figures you may use) ===
{scenario.trace.render()}

=== HOW TO WRITE IT ===
{_FORMAT_GUIDANCE}

Write only the analyst's reply. No preamble, no commentary about the task."""


REPAIR_SUFFIX = """\

Your previous attempt was rejected by an automatic check:

{problems}

Rewrite it. Use only figures from the trace, keep every required figure, and state each one \
exactly with comma formatting."""
