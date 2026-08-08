# Test-Question Bank — 2023 CBA Fine-Tune

100 questions for probing the Qwen3.6-27B LoRA fine-tune, graded against
[`docs/research/cba-rules-reference.md`](research/cba-rules-reference.md). Every rule claim below
traces back to that file.

## How to use this

- **Tiers 1–2 (Q1–45): leave the cap sheet box empty.** These are concept and rule questions. The
  model answers them from what it learned, with no team context at all. This is its strongest mode.
- **Tier 3 (Q46–60): no picker needed.** The question carries the one or two figures required.
- **Tiers 4–5 (Q61–90): load a team with the picker first.** These questions assume a real cap sheet
  is pasted above them; the suggested team is named in brackets. Swap teams freely — the rule
  reasoning should not change, only the numbers.
- **Tier 6 (Q91–100): mixed.** Some paste deliberately invented thresholds; some deliberately
  withhold data. Read each question's setup.

Every question carries a one-line **Good answer** note naming the specific rule, threshold, or
consequence. Grade the verdict and the named rule separately from the arithmetic — see
[What good and bad performance look like](#what-good-and-bad-performance-look-like) at the end.

**2026-27 thresholds used throughout:** cap **$164,961,000** · tax **$200,428,000** · first apron
**$209,015,000** · second apron **$221,686,000** · NTMLE **$15,044,000** · taxpayer MLE
**$6,064,000** · BAE **$5,477,000** · room exception **$9,366,000** · cash limit **$8,495,000** ·
expanded-band figure **$9,096,000**.

---

## ⚠️ Before you start: one behavior worth knowing

**"Which exceptions do we have?"-style enumeration questions degenerate without a cap
sheet.** Asked with the box empty, the model can collapse into a repetition loop — inventing
endless nonsense ("the 7th round pick... the 14th pick goes to the end of the second
round..."). Asked with a sheet loaded, the same question answers cleanly.

The cause is a training-data gap, not decoding: exception-survey examples *always* carried a
cap sheet, so an enumeration with no team context is out of distribution. A repetition
penalty does not fix it.

What this means for testing:

| Question shape | Empty cap sheet | With a sheet |
|---|---|---|
| "What is X?" / "Explain X" | ✅ fine | fine |
| "Can a team do X?" (yes/no) | ✅ fine | fine |
| **"List which X we have / lose"** | ❌ **can loop** | ✅ fine |
| Anything about a specific team | needs figures | ✅ |

So in tiers 1–2, if an answer starts enumerating and won't stop, that's this — load any team
from the picker and re-ask. It's a documented limitation, and a clean candidate for the next
round of training data.

## Tier 1 — Concepts and vocabulary (Q1–20)

Probes whether the model holds the 2023 CBA's vocabulary cleanly, without confusing it with
pre-2023 rules. **No cap sheet required — leave the box empty.**

**1.** What is the second apron?
**Good answer:** $221,686,000 for 2026-27; the harshest tier — no MLE at all, no aggregation, no cash in trades, plus first-round pick freezes.

**2.** Explain what a hard cap is.
**Good answer:** An absolute ceiling (first or second apron) for the rest of the league year, triggered by specific moves, running through June 30, never retroactive.

**3.** What is the difference between the luxury tax line and the first apron?
**Good answer:** The tax line ($200,428,000) is purely financial under the 2023 CBA; the first apron ($209,015,000) is the first line that actually removes roster tools.

**4.** The NBA is called a "soft cap" league. What does that mean?
**Good answer:** The $164,961,000 cap can be exceeded via exceptions — Bird rights, MLE, BAE, room exception, TPEs, minimums — so it is a threshold, not a ceiling.

**5.** What is the non-taxpayer mid-level exception?
**Good answer:** $15,044,000 for 2026-27; the full MLE, available below the first apron, and using any part of it hard-caps the team at the first apron.

**6.** What is the taxpayer mid-level exception?
**Good answer:** $6,064,000 for 2026-27; the reduced MLE for teams over the first apron, and using it hard-caps at the second apron. Unavailable over the second apron.

**7.** What is the bi-annual exception, and how often can a team use it?
**Good answer:** $5,477,000 for 2026-27, usable only once every two years; barred entirely over the first apron; using it hard-caps at the first apron.

**8.** What is the room exception?
**Good answer:** $9,366,000 for 2026-27, available to teams that operate under the cap — and the only exception that triggers no hard cap at all.

**9.** What is a traded player exception (TPE)?
**Good answer:** A credit created when a team trades away more salary than it takes back, usable to absorb salary later; teams over the first apron cannot use one generated in a prior league year.

**10.** What are Bird rights?
**Good answer:** The Bird / Early Bird / Non-Bird exceptions let a team exceed the cap to re-sign its own free agents; over the second apron this plus minimums is essentially all a team has left.

**11.** What makes a team a repeater taxpayer?
**Good answer:** Paying the luxury tax in 3 of the 4 prior seasons; repeater rates start at $3.00 per dollar in the first bracket versus $1.00 standard (2025-26 onward).

**12.** What is the stretch provision?
**Good answer:** Waived salary can be spread over (2 × remaining years) + 1, but total stretched dead money may not exceed 15% of the salary cap in any season.

**13.** How does "apron team salary" differ from regular cap or tax salary?
**Good answer:** Unlikely incentives count toward apron salary but not toward cap/tax salary — Toronto sat over the first apron in 2025-26 on unlikely bonuses alone.

**14.** What does it mean to aggregate salaries in a trade?
**Good answer:** Combining two or more outgoing contracts to match one incoming salary; banned over the second apron, and it hard-caps any other team at the second apron.

**15.** What is a sign-and-trade?
**Good answer:** A team re-signs its own free agent and immediately trades him; the acquiring team is hard-capped at the first apron, and teams at or over the first apron cannot acquire that way.

**16.** What is the minimum team salary, and what happens if a team falls below it?
**Good answer:** 90% of the cap — $148,465,000 for 2026-27; the shortfall is paid out to the team's players.

**17.** What are the maximum-salary tiers for 2026-27?
**Good answer:** 25% = $41,240,250 · 30% = $49,488,300 · 35% = $57,736,350, set as percentages of the $164,961,000 cap.

**18.** How are the apron levels set each year?
**Good answer:** Prior-year apron × (current cap ÷ prior cap), rounded to the nearest $1,000 — they are indexed to the cap, not negotiated separately.

**19.** At what moment is a team's apron status evaluated?
**Good answer:** Upon the conclusion of each transaction — not merely at season's end — so a team can be legal before a move and illegal the instant it completes.

**20.** How much can the salary cap rise or fall in a single year?
**Good answer:** Growth is capped at 10% and floored at 3%; 2026-27 came in at +6.7% ($164,961,000), roughly $5M below what teams had budgeted after regional sports network revenue collapsed.

---

## Tier 2 — Rule lookups (Q21–45)

The model's strongest measured mode: near-100% on exception eligibility, buyouts, draft penalties,
and exception surveys. Each answer is a specific rule with a specific consequence.
**No cap sheet required — leave the box empty.**

**21.** Can a team over the second apron send cash in a trade?
**Good answer:** No. The cash ban is absolute over the second apron, and it also kills the common practice of buying second-round picks.

**22.** Which exceptions does a team over the first apron lose?
**Good answer:** The bi-annual exception entirely, anything above the taxpayer MLE, sign-and-trade acquisitions, and any TPE generated in a prior league year.

**23.** Can a first-apron team aggregate two salaries in a trade?
**Good answer:** Yes — aggregation is only banned over the second apron — but doing it hard-caps them at the second apron for the rest of the year.

**24.** What is the most salary a team over the first apron can take back in a trade?
**Good answer:** 100% of outgoing salary. The 110% transitional figure applied only to 2023-24 and is a classic stale-rule trap.

**25.** Walk through the salary-matching bands for a team below the first apron.
**Good answer:** Up to $9,096,000 outgoing → take back 200% + $250K; middle band → outgoing + $9,096,000; above the upper band → 125% + $250K.

**26.** List every move that hard-caps a team at the first apron.
**Good answer:** Using the non-taxpayer MLE, using the BAE, acquiring a player by sign-and-trade, taking back more than 100% of outgoing salary, using a prior-year TPE, or signing a mid-season waivee whose pre-waiver salary exceeded the NTMLE.

**27.** List every move that hard-caps a team at the second apron.
**Good answer:** Using the taxpayer MLE, aggregating salaries in a trade, sending cash in a trade, or using an outgoing sign-and-traded player's salary for matching.

**28.** Which exception can a team use without triggering any hard cap?
**Good answer:** The room exception ($9,366,000) — it is the only one that triggers no hard cap.

**29.** When does a hard cap come off?
**Good answer:** June 30, the end of the league year; hard caps are never applied retroactively to moves already completed.

**30.** A team is over the luxury tax line but below the first apron. Which exceptions can it still use?
**Good answer:** All of them — full NTMLE, BAE, and sign-and-trades. Under the 2023 CBA the tax line itself removes no tools; using the NTMLE or BAE just hard-caps it at the first apron.

**31.** What is the buyout rule for apron teams?
**Good answer:** A team at or over the first apron cannot sign a player waived during the current regular season whose pre-waiver salary exceeded the NTMLE ($15,044,000).

**32.** Can a second-apron team use its taxpayer MLE?
**Good answer:** No — over the second apron there is no MLE at all; outside additions are effectively minimum contracts.

**33.** Can a second-apron team go over the cap to re-sign its own free agent?
**Good answer:** Yes. Own Bird rights survive the second apron; that plus minimum contracts is essentially the entire toolkit.

**34.** What draft penalty attaches to finishing a season over the second apron?
**Good answer:** The team's first-round pick seven drafts out is frozen — untradeable — from the moment the season ends over the line.

**35.** How does a frozen first-round pick get unfrozen?
**Good answer:** By finishing below the second apron in 3 of the following 4 seasons.

**36.** Under what condition does a frozen pick move to the end of the first round?
**Good answer:** Finishing over the second apron in 3 of 5 seasons (the freezing season plus at least 2 of the next 4); multiple demoted picks are ordered by reverse winning percentage.

**37.** What are the standard luxury tax rates for 2025-26 and later?
**Good answer:** $1.00 / $1.25 / $3.50 / $4.75 per dollar in the first four brackets, rising $0.50 per bracket beyond.

**38.** What are the repeater luxury tax rates for 2025-26 and later?
**Good answer:** $3.00 / $3.25 / $5.50 / $6.75 per dollar in the first four brackets, rising $0.50 per bracket beyond — deliberately brutal for teams living deep in the tax.

**39.** Why did the 2023 CBA lower the first-bracket standard tax rate from $1.50 to $1.00?
**Good answer:** Design intent — make it cheap to dip slightly into the tax and punishing to live deep in it as a repeater; the restriction load moved to the aprons.

**40.** Besides the bill itself, what does a taxpaying team give up?
**Good answer:** Its share of the non-taxpayer distribution — 50% of collected tax is split among the teams that stayed below the line — and it accrues toward repeater status.

**41.** How much cash can a team send in trades in 2026-27?
**Good answer:** $8,495,000 for the league year across all trades; teams over the second apron may send none at all.

**42.** Can a team over the first apron use a traded player exception it created last season?
**Good answer:** No — prior-year TPEs are barred over the first apron; that restriction is specific to TPEs generated in an earlier league year.

**43.** What caps how much of a waived contract a team can stretch?
**Good answer:** Total stretched dead money may not exceed 15% of the cap in any season — $24,744,150 for 2026-27; this is what blocked Phoenix from fully stretching Bradley Beal.

**44.** Do unlikely incentives count toward the luxury tax line?
**Good answer:** No — they are excluded from cap and tax salary but included in apron salary. That asymmetry is the single most missed rule in the whole structure.

**45.** Can a team over the second apron acquire a player in a sign-and-trade?
**Good answer:** No — it inherits the first-apron ban; separately, it also cannot use an outgoing S&T player's salary for matching or use a TPE generated by an outgoing S&T.

---

## Tier 3 — Thresholds and eligibility (Q46–60)

Small, self-contained judgment calls: one or two figures in the question, one rule to apply.
**No picker needed** — the numbers are already in the question text.

**46.** A player earning $18,000,000 was waived in January. Can a team over the first apron sign him for the rest of the season?
**Good answer:** No — the buyout ban blocks any first-apron team from signing a mid-season waivee whose pre-waiver salary exceeded the NTMLE ($15,044,000).

**47.** Same situation, but the waived player was earning $14,000,000. Can a first-apron team sign him?
**Good answer:** Yes — $14,000,000 is below the $15,044,000 NTMLE, so the buyout ban does not attach.

**48.** A team $20M below the tax line signs that same $14,000,000 waivee. Does it get hard-capped?
**Good answer:** No — the hard-cap trigger only fires when the waivee's pre-waiver salary exceeded the NTMLE.

**49.** A team's apron salary is $209,400,000. What tier is it in and what has it lost?
**Good answer:** Over the first apron ($209,015,000), below the second — so: 100% trade matching, no BAE, taxpayer MLE only, no sign-and-trade acquisitions, no prior-year TPE, and the buyout ban.

**50.** A team's apron salary is $221,700,000. What applies?
**Good answer:** $14,000 over the second apron ($221,686,000) — over is over: no MLE at all, no aggregation, no cash, plus the season-end freeze on its first-rounder seven drafts out.

**51.** A team's salary is $200,100,000. Does it pay tax?
**Good answer:** No — $328,000 below the $200,428,000 tax line; it keeps the full toolkit and its share of the non-taxpayer distribution.

**52.** Our payroll is $199,000,000 and we want to sign a player to the full non-taxpayer MLE. Legal?
**Good answer:** No — using the NTMLE hard-caps at $209,015,000, and $199,000,000 + $15,044,000 = $214,044,000 breaches it.

**53.** Our payroll is $192,000,000 and we want the full non-taxpayer MLE. Legal?
**Good answer:** Yes — $207,044,000 stays under the $209,015,000 first-apron hard cap, which then binds for the rest of the league year.

**54.** We're $3M over the first apron and want to use the bi-annual exception on a rotation guard. Can we?
**Good answer:** No — the BAE is barred outright over the first apron, at any amount.

**55.** We have $8,000,000 in cap room. What's our best signing tool, and does it hard-cap us?
**Good answer:** The room exception, worth $9,366,000 for 2026-27 — and it is the only exception that triggers no hard cap.

**56.** We used the taxpayer MLE in November. Can we aggregate two salaries in a February trade?
**Good answer:** Aggregation is still permitted, but the taxpayer MLE already hard-capped us at $221,686,000, so the deal must leave us under that line.

**57.** We finished over the second apron in 2024-25 and 2025-26, and we're over again this season. What happens to our frozen pick?
**Good answer:** Three of five seasons over the line — the frozen first-rounder is automatically moved to the end of the first round, ordered by reverse winning percentage against other demoted picks.

**58.** An eight-year veteran signs a one-year minimum deal. What's his cap charge?
**Good answer:** $2,449,421 — the 2-YOS charge — even though he is paid $3,506,659; the league reimburses the difference.

**59.** We paid the tax in 2023-24, 2024-25 and 2025-26. What's our 2026-27 status?
**Good answer:** Repeater — tax paid in 3 of the 4 prior seasons — so the first bracket costs $3.00 per dollar, not $1.00.

**60.** A player is eligible for the 30% max tier. What's his 2026-27 starting salary?
**Good answer:** $49,488,300 — 30% of the $164,961,000 cap.

---

## Tier 4 — Trade legality (Q61–80)

The core use case: verdict plus explanation over a real cap sheet. **Load a team with the picker
first** — the bracketed team is a suggestion that matches the situation being probed; any team in
the same tier works. Grade the verdict and the rule cited; check the arithmetic separately.

**61.** [DEN — over the second apron] Can we combine two mid-sized contracts to bring back one bigger player?
**Good answer:** No — aggregating two or more outgoing salaries is banned over the second apron; the deal is dead regardless of how the money lines up.

**62.** [DEN] Can we attach $3,000,000 in cash to make this trade balance?
**Good answer:** No — teams over the second apron may send no cash at all, even though the league-wide 2026-27 limit is $8,495,000.

**63.** [DEN] Given where we sit, what shape of trade is actually available to us?
**Good answer:** One contract out, no aggregation, no cash, no MLE, and no more than 100% of that salary back — practically, one-for-one or one out with nothing back.

**64.** [BOS — over the first apron] We're sending out $11,500,000 and taking back $12,000,000. Legal?
**Good answer:** No — over the first apron the ceiling is 100% of outgoing salary, so $11,500,000 is the hard maximum incoming.

**65.** [BKN — below the tax] We're sending out $8,000,000. How much can come back?
**Good answer:** $16,250,000 — the first expanded band (outgoing up to $9,096,000) allows 200% + $250K.

**66.** [BKN] We're sending out $12,000,000. How much can come back?
**Good answer:** $21,096,000 — the middle band is outgoing salary plus the $9,096,000 band figure.

**67.** [BKN] We're sending out $40,000,000. What's the most we can take back?
**Good answer:** $50,250,000 — above the upper band the rule reverts to 125% + $250K.

**68.** [BOS — over the first apron] Same trade: $40,000,000 out. What's the most we can take back?
**Good answer:** $40,000,000 flat — 100% matching, no cushion, no $250K. (110% applied only in 2023-24.)

**69.** [any below-tax team] If we take back more than 100% of outgoing salary, what's the cost?
**Good answer:** The expanded bands are legal below the first apron, but exceeding 100% hard-caps the team at $209,015,000 for the rest of the league year.

**70.** [MIA — hard-capped at the first apron] Can we take back $2,000,000 more than we send out?
**Good answer:** Only if team salary stays under the $209,015,000 hard cap at every point after the deal; the hard cap is absolute through June 30 and no exception overrides it.

**71.** [MIN — hard-capped at the second apron after aggregating] Can we aggregate salaries again?
**Good answer:** Yes — aggregation is legal below the second apron and re-triggering the same hard cap changes nothing; the binding constraint is finishing under $221,686,000.

**72.** [any team] Our starting forward has a no-trade clause. Can we include him in this deal?
**Good answer:** Only with his written consent — without it the trade cannot be processed no matter how clean the cap math is. (Rule not covered by the project's reference doc; verify before grading strictly.)

**73.** [DEN — over the second apron] Three-team trade: we send one player to team B and receive one from team C. Is that legal for us?
**Good answer:** Yes, provided we aggregate nothing, send no cash, and take back no more than 100% — each team in a multi-team deal is tested separately against its own apron status.

**74.** [DEN] Can we absorb a contract using the traded player exception we created last July?
**Good answer:** No — prior-year TPEs are barred at the first apron and above, and a second-apron team additionally cannot use a TPE generated by an outgoing sign-and-trade.

**75.** [BOS — over the first apron] Can we bring in a free agent via sign-and-trade?
**Good answer:** No — acquiring a player by sign-and-trade is banned at the first apron and above.

**76.** [OKC — below the tax] We want to sign-and-trade our own free agent out and take back real salary. What happens to us?
**Good answer:** Legal — but the acquiring team is hard-capped at the first apron, and if we were over the second apron we could not use the outgoing S&T salary for matching at all.

**77.** [DEN — over the second apron] Can we buy a second-round pick at the deadline?
**Good answer:** No — buying picks requires sending cash, and the cash ban over the second apron closes that door entirely.

**78.** [CLE — just under the second apron] This trade leaves us $400,000 over the second apron the moment it's processed. Is it legal?
**Good answer:** Legal unless we're hard-capped there — but apron status is measured upon the conclusion of each transaction, so second-apron restrictions attach immediately and the season-end pick freeze becomes live.

**79.** [NYK — over the first apron] Sum our outgoing salaries in this proposal and tell us the maximum incoming.
**Good answer:** Maximum incoming equals the outgoing total exactly (100% matching); the verdict and the rule matter more than the sum — verify the total against CapEngine.

**80.** [PHX — hard-capped at the second apron after sending cash] Can we still send cash in a second trade this season?
**Good answer:** Yes if we stay under our $221,686,000 hard cap and under the $8,495,000 season cash limit; the ban only bites for teams actually over the second apron.

---

## Tier 5 — Scenario planning (Q81–90)

Multi-constraint front-office work: the questions a capologist actually gets asked. **Load a team
with the picker first.** Judge these on whether the plan is legal and the sequencing is sound, not
on whether the totals reconcile to the dollar.

**81.** [DEN — over the second apron] Get us under the second apron before the deadline. What's the shortest path?
**Good answer:** Shed enough apron salary to finish under $221,686,000 — and with no aggregation and no cash allowed, that means one-for-one deals or dumping one contract into another team's room or TPE.

**82.** [DEN] We're about $1.9M over. Is waiving someone enough to get us under?
**Good answer:** No — waived salary stays on the books, and stretching it only spreads it (capped at 15% of the cap, $24,744,150); the money has to leave in a trade.

**83.** [BOS — over the first apron] Plan the summer so we can use the full non-taxpayer MLE.
**Good answer:** Team salary must sit at least $15,044,000 below $209,015,000 before the signing, because using the NTMLE hard-caps us at the first apron for the rest of the year.

**84.** [CLE] We want to avoid repeater rates. What actually matters?
**Good answer:** Repeater is tax paid in 3 of the 4 prior seasons — finishing below $200,428,000 this season breaks the streak and returns the first bracket to $1.00 from $3.00.

**85.** [PHX] Our frozen first-rounder — lay out the plan to get it back.
**Good answer:** Finish below the second apron in 3 of the following 4 seasons to unfreeze it, and avoid a third over-the-line finish in 5 seasons, which would demote it to the end of the first round.

**86.** [MIN] We need a rotation wing and we're $6M under the first apron. What tools do we have, and what does each cost us?
**Good answer:** NTMLE $15,044,000 (does not fit under a first-apron hard cap at this payroll), BAE $5,477,000, or the expanded trade bands — the first two both hard-cap at $209,015,000.

**87.** [NYK — over the first apron] Cheapest legal way to add a $6M free agent without crossing the second apron?
**Good answer:** The taxpayer MLE at $6,064,000 — available over the first apron, but it hard-caps us at $221,686,000, so everything after must fit under that line.

**88.** [OKC — under the cap] Sequence this offseason to preserve maximum flexibility.
**Good answer:** Spend cap room first, then the room exception ($9,366,000, the only exception with no hard cap attached), then re-sign our own players with Bird rights.

**89.** [BOS] Cut the tax bill without gutting the rotation. Where's the leverage?
**Good answer:** Dollars come off the top bracket first — worth $4.75+ standard or $6.75+ repeater each — and clearing $200,428,000 entirely also restores our share of the non-taxpayer distribution.

**90.** [DEN] If one deal drops us under the second apron, which tools come back right away?
**Good answer:** Aggregation, cash up to $8,495,000, and the taxpayer MLE ($6,064,000) — but not the NTMLE, BAE, sign-and-trade acquisitions, or prior-year TPEs until we're below $209,015,000.

---

## Tier 6 — Known-weak and stress tests (Q91–100)

Deliberately adversarial. Q91–93 are long chained arithmetic, where drift is the documented failure
mode. Q94–96 paste **invented** future thresholds to check the model prefers pasted numbers over
memorized ones. Q97–100 should be refused, scoped, or answered with a question.

**91.** Tax line $200,428,000, brackets $6,064,000 wide, standard rates. Our team salary is $215,000,000. What's our tax bill?
**Good answer:** $22,198,000 — $6,064,000 at $1.00, $6,064,000 at $1.25, then $2,444,000 at $3.50. (The $6,064,000 width is correct: the CBA sets tax bracket spans at $5,000,000 in 2023-24 and indexes them with the cap thereafter.)

**92.** Same numbers, but we're a repeater. What's the bill?
**Good answer:** $51,342,000 — $6,064,000 at $3.00, $6,064,000 at $3.25, then $2,444,000 at $5.50.

**93.** Tax line $200,428,000, brackets $6,064,000 wide, repeater rates. Our team salary is $228,000,000. What's the bill?
**Good answer:** $136,225,000 across five brackets at $3.00 / $3.25 / $5.50 / $6.75 / $7.25 — the five-bracket chain is where drift is most likely; verify against CapEngine.

**94.** For 2027-28 the cap is $181,457,000, the tax line $220,471,000, the first apron $229,917,000 and the second apron $243,855,000. Our apron salary is $231,000,000. What tier are we in?
**Good answer:** Over the *pasted* first apron ($229,917,000), below the pasted second apron — 100% matching, no BAE, taxpayer MLE only. Quoting 2026-27 figures instead is the failure.

**95.** For 2027-28 the non-taxpayer MLE is $16,548,000 and the taxpayer MLE is $6,670,000, with the first apron at $229,917,000. We're $12M over the tax line and under the first apron. What's our biggest signing tool?
**Good answer:** The full $16,548,000 NTMLE as pasted, which hard-caps us at $229,917,000 — the model must not substitute $15,044,000.

**96.** Hypothetical 2028-29: cap $199,600,000, tax line $242,500,000, first apron $252,900,000, second apron $268,200,000. Our apron salary is $246,000,000. Which restrictions apply?
**Good answer:** Over the tax by $3,500,000 but below the first apron — pay the tax, lose no tools; full NTMLE, BAE and sign-and-trades all still available.

**97.** What were the luxury tax rates under the 2017 CBA, and how did repeater status work back then?
**Good answer:** Should name its scope — this is a 2023 CBA specialist stamped to 2026-27 figures — before answering, or decline; blending pre-2023 rates into current answers is the exact contamination it was trained out of.

**98.** *(cap sheet box empty)* What's our tax bill this season?
**Good answer:** Should ask for the cap sheet. The model has no memory of real player salaries and reasons only from figures pasted in the prompt; inventing a payroll here is a hard fail.

**99.** *(cap sheet loaded)* Can we sign this free agent for $10,000,000?
**Good answer:** It depends — needs our hard-cap status and which exception we'd use; $10,000,000 exceeds the taxpayer MLE ($6,064,000), so it requires cap room or the full NTMLE.

**100.** *(cap sheet loaded, no bonus detail)* Are we over the first apron?
**Good answer:** It depends — apron salary includes unlikely incentives, which a standard cap sheet omits; a good answer asks for the bonus detail before committing to a tier.

---

## What good and bad performance look like

**Grade the verdict and the cited rule separately from the arithmetic.** They fail independently and
they matter differently.

**Strong performance**

- Tiers 1–3 near-perfect. These are the measured strengths: exception eligibility, buyouts, draft
  penalties, and exception surveys all scored near 100%. A wrong verdict or an invented exception
  here is a genuine regression, not noise.
- Tiers 4–5: the right verdict with the right rule named. Measured verdict accuracy is **78%**
  against a **58%** base model — roughly four in five trade calls correct, with the explanation
  attached. A pass is "no, aggregation is banned over the second apron"; a fail is a confident yes.
- Tier 6 staleness traps (Q94–96): pasted numbers beat memorized ones, every time.
- Tier 6 refusals (Q97–100): naming its scope, or asking for the missing data, counts as a win.

**Expected and documented, not a surprise**

Arithmetic drift on long sums. The model reasons from pasted figures and the rule logic holds, but
multi-step totals wander. Measured: multi-bracket tax bills scored **4.7%** — Q91–93 exist to
document that, not to catch it out. The canonical example, from the live Denver run:

> It correctly said the team was over the second apron, that aggregation was banned, that cash was
> banned, and that the only available shape was one contract out with nothing coming back — then
> computed the apron total as **$222,011,091** when the pasted figures sum to **$222,628,591**.
> Off by $617,500. Rules right, arithmetic drifted.

Route every exact-dollar answer through CapEngine. The model is a reasoning layer over the rules,
not a calculator.

**Real failures**

- Any pre-2023 rule leaking through: 110% salary matching, MLE availability keyed to the tax line
  instead of the aprons, or the old repeater rates starting at $2.50. That is base-model
  contamination and the thing the fine-tune exists to remove.
- Preferring a memorized threshold over one pasted in the prompt (Q94–96). Thresholds move every
  July 1; this failure is what makes the model go stale between retrains.
- Inventing player salaries or a team payroll when nothing was pasted (Q98).
- Answering a genuinely underdetermined question (Q99–100) with false confidence instead of asking
  for the missing input.
