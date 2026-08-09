# hardcap — a note for testers

Thanks for trying this. It's an experimental model, and honest feedback about where it's
wrong is worth more to me than praise about where it's right.

## What it is

A language model trained specifically on the 2023 CBA — the aprons, trade legality,
exceptions, the stretch provision, the tax. It runs on hardware in my apartment, not a
frontier lab's cluster, and it's a 27-billion-parameter open model rather than something the
size of GPT-5.

**The one design idea worth knowing:** the *rules* live in the model's weights; the *numbers*
do not. Salaries change with every transaction, so a model that memorized them would be
confidently out of date by August. Instead you hand it a cap sheet — from the picker, an
upload, or a paste — and it reasons over what you gave it. Change a threshold in the box and
the answer changes with it. That's the bet, and telling me whether it holds up is the most
useful thing you can do.

## How to use it

**Rules and concept questions need no cap sheet.** Clear the box and ask:

- "Can a team over the second apron aggregate salaries in a trade?"
- "What's the difference between the tax line and the first apron?"
- "Which exceptions does a first-apron team lose?"
- "What happens to draft picks if a team finishes over the second apron?"

**Team-specific questions need a sheet.** Use the picker (30 teams, 2024-25 through 2026-27),
or upload a PDF/CSV of your own:

- "Are we over the second apron, and by how much?"
- "If we send out [player] for a $22M contract, does the money work?"
- "Get us under the second apron before the deadline — what are the options?"
- "Which exceptions can we actually use at this payroll?"

**It's conversational.** Follow up. "What if we renounce the hold instead?" works.

There's a bank of 100 graded test questions in `docs/test-questions.md` if you'd like a
structured pass rather than poking at it.

## Where it's good, and where it isn't

I'd rather you hear this from me than discover it and assume I didn't know.

**Good at:** applying rules to a situation. On our internal exam it gets **78%** of
legal/illegal verdicts right, against **58%** for the same model before training. Exception
eligibility, buyout rules, draft penalties, and hard-cap triggers are near-perfect.

**Weak at:** long chained arithmetic. Adding up a fifteen-contract payroll or a multi-bracket
tax bill, it can drift — in one live demo it got every rule right and still landed
**$617,500** off on a sum. It now has a calculator it can call, and the interface shows a
badge when it used one. **Verify any large total you'd act on.**

**Also worth knowing:** it does not look anything up. If you ask about a team without giving
it a sheet, the right behavior is to ask you for one. If it invents a payroll instead, that's
a bug — please flag it.

## Flagging things

Thumbs up/down on any answer, and the thumbs-down asks what went wrong. Those go into a log I
read directly — a bad answer with a one-line note about *why* it's bad is genuinely the most
valuable thing you can send me, because it becomes a training example.

Most useful of all: **a case where it sounds confident and is wrong.** Those are the ones I
can't find by testing myself, because I don't know the league the way you do.

## Fine print

Not affiliated with, endorsed by, or sponsored by the NBA. Rules reflect the 2023 CBA. This
is a research project — verify anything you'd act on.
