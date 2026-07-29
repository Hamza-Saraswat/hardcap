# NBA 2023 CBA — Salary Cap & Apron Rules Reference

Research date: 2026-07-28. This document is the **specification for `capengine/`**. Every rule
encoded in the calculator should trace back to a line here.

> **Sourcing warning:** `cbafaq.com` (Larry Coon's FAQ) was **never updated for the 2023 CBA** —
> it is frozen at the 2017 edition, and Coon has publicly retired. Do **not** use it for apron-era
> rules. Current authorities: the CBA text itself, the league's CBA 101, and the Hoops Rumors
> glossary series.

---

## 1. Threshold structure

Four layers, in ascending order:

1. **Salary cap** — soft; exceeded via exceptions.
2. **Luxury tax line** — purely financial under the 2023 CBA (money + repeater accrual, almost no
   roster restrictions on its own).
3. **First apron** — the first *restriction* line.
4. **Second apron** — severe restrictions plus draft-pick penalties.

Apron levels are indexed to the cap: `prior-year apron × (current cap ÷ prior cap)`, rounded to the
nearest $1,000. Apron status is evaluated **upon the conclusion of each transaction**, not merely at
season's end.

**Critical asymmetry:** *unlikely* incentives count toward **apron** team salary even though they do
not count toward regular cap/tax salary. (Toronto sat over the first apron in 2025-26 purely on
unlikely bonuses: Barrett $3.4M, Quickley $2.5M, Poeltl $0.5M.)

## 2. Official threshold figures

| Item | 2024-25 | 2025-26 | 2026-27 |
|---|---|---|---|
| Salary cap | $140,588,000 | $154,647,000 | **$164,961,000** |
| Minimum team salary (90%) | $126,529,000 | $139,182,000 | $148,465,000 |
| Luxury tax line | $170,814,000 | $187,895,000 | **$200,428,000** |
| First apron | $178,132,000 | $195,945,000 | **$209,015,000** |
| Second apron | $188,931,000 | $207,824,000 | **$221,686,000** |
| Non-taxpayer MLE | $12,822,000 | $14,104,000 | $15,044,000 |
| Taxpayer MLE | $5,168,000 | $5,685,000 | $6,064,000 |
| Room exception | $7,983,000 | $8,781,000 | $9,366,000 |
| Bi-annual exception | ~$4.7M ⚠️ | ~$5.1M ⚠️ | $5,477,000 |

Sources: [NBA PR 2024-25](https://pr.nba.com/2024-25-nba-season-salary-cap) ·
[NBA PR 2025-26 (July 1, 2025)](https://pr.nba.com/nba-salary-cap-2025-26-season) ·
[NBA.com 2026-27 (June 30, 2026)](https://www.nba.com/news/nba-salary-cap-2026-27-season) ·
[Hoops Rumors 2026-27](https://www.hoopsrumors.com/2026/06/salary-cap-tax-line-set-for-2026-27-nba-season.html)

**2026-27 additional constants:** max salary tiers 25% = $41,240,250 / 30% = $49,488,300 /
35% = $57,736,350; cash-in-trade annual limit $8,495,000; expanded-TPE band figure $9,096,000;
two-way salary $678,882 ⚠️ (single-source).

**2026-27 minimum salary scale** by years of service:
0: $1,357,763 · 1: $2,185,116 · 2: $2,449,421 · 3: $2,537,526 · 4: $2,625,627 · 5: $2,845,883 ·
6: $3,066,143 · 7: $3,286,399 · 8: $3,506,659 · 9: $3,524,115 · 10+: $3,876,529.
Veterans with 3+ YOS on one-year minimum deals carry only the 2-YOS cap charge ($2,449,421); the
league reimburses the difference.
([Hoops Rumors, July 1 2026](https://www.hoopsrumors.com/2026/07/nba-minimum-salaries-for-2026-27.html))

### Cap growth rule
The CBA caps annual salary-cap growth at **10%** and floors it at **3%**. 2025-26 rose the full 10%.
2026-27 was expected to do the same (~$170.1M) on the strength of the 11-year ~$77B media deal, but
came in at **$164.961M — +6.7%**, roughly $5M short, after regional sports network revenue collapsed.
This dragged the tax and apron lines ~$5M below what teams had budgeted.
([Front Office Sports](https://frontofficesports.com/nba-salary-cap-up-7-in-2026-27-but-teams-expected-more/) ·
[Bleacher Report, June 2026](https://bleacherreport.com/articles/25448479-2026-27-nba-salary-cap-1st-and-2nd-aprons-luxury-tax-levels-revealed-fa))

**Lesson encoded in the dataset:** never extrapolate thresholds by assuming +10%. Always read them
from the prompt.

---

## 3. Restrictions by threshold

### 3a. Over the luxury tax (below first apron)
1. Pay the tax per bracket (below).
2. Accrue **repeater** status — repeater = paid tax in **3 of the 4 prior seasons**.
3. Forfeit the non-taxpayer tax distribution (50% of collected tax is split among non-taxpayers).
4. No exception is lost: a tax team below the first apron may still use the full non-taxpayer MLE,
   the BAE, and sign-and-trades — accepting the resulting hard cap.

**Luxury tax rates** (per increment over the line; brackets ~$5.168M wide in 2024-25, indexed):

| Bracket | Standard ≤2024-25 | Repeater ≤2024-25 | **Standard 2025-26+** | **Repeater 2025-26+** |
|---|---|---|---|---|
| 1st | $1.50 | $2.50 | **$1.00** | **$3.00** |
| 2nd | $1.75 | $2.75 | **$1.25** | **$3.25** |
| 3rd | $2.50 | $3.50 | **$3.50** | **$5.50** |
| 4th | $3.25 | $4.25 | **$4.75** | **$6.75** |
| each beyond | +$0.50 | +$0.50 | +$0.50 | +$0.50 |

Design intent: cheaper to dip slightly into the tax, brutal to live deep in it as a repeater.
([Hoops Rumors glossary, Nov 2024](https://www.hoopsrumors.com/2024/11/hoops-rumors-glossary-luxury-tax-penalties-4.html))

### 3b. Over the first apron — cannot:
1. Acquire a player via **sign-and-trade**.
2. Use any portion of the **bi-annual exception**.
3. Use more than the **taxpayer MLE** to sign a player; cannot use any MLE portion to acquire a
   player by trade or waiver claim.
4. **Buyout ban:** sign a player waived during the current regular season whose pre-waiver salary
   exceeded the non-taxpayer MLE.
5. Take back **more than 100%** of outgoing salary in a trade.
6. Use a **traded player exception generated in a prior league year**.

### 3c. Over the second apron — everything above, plus cannot:
1. Use **any MLE at all** (taxpayer MLE unavailable) — additions are effectively minimums and own
   Bird rights only.
2. **Aggregate** two or more outgoing salaries in one trade to acquire a player.
3. Send **cash** in any trade (this also kills buying second-round picks).
4. Use an outgoing signed-and-traded player's salary for matching, or use a TPE generated by an
   outgoing S&T.

**Draft penalties:**
- Finishing a season over the second apron **freezes your first-round pick seven drafts out**
  (untradeable). It unfreezes only after finishing below the second apron in 3 of the following 4
  seasons.
- Over the second apron in **3 of 5 seasons** (the freezing season plus ≥2 of the next 4) → the
  frozen pick **automatically moves to the end of the first round**. Multiple demoted picks order by
  reverse winning percentage.

([Hoops Rumors: Tax Aprons, Jan 2025](https://www.hoopsrumors.com/2025/01/hoops-rumors-glossary-tax-aprons-2.html) ·
[Forbes, July 2025](https://www.forbes.com/sites/bryantoporek/2025/07/28/why-nba-teams-are-afraid-of-the-second-apron/))

### 3d. Salary matching bands (team **below** the first apron)
"Expanded TPE" rules:
- Outgoing salary up to a first band ($9,096,000 in 2026-27): take back **200% + $250K**.
- Middle band: **outgoing + the band amount**.
- Above the upper band: **125% + $250K**.

A team **over the first apron** is capped at **100%** of outgoing salary. (The 110% transitional rule
applied only in 2023-24.)
([Hoops Rumors](https://www.hoopsrumors.com/2023/09/salary-matching-rules-for-trades-during-2023-24-season.html) ·
[Sports Business Classroom](https://sportsbusinessclassroom.com/understanding-trade-matching-in-the-new-collective-bargaining-agreement/))

### 3e. Hard cap triggers
Hard-capped at the **first apron** for the remainder of the league year by: using the non-taxpayer
MLE; using the BAE; acquiring a player via sign-and-trade; taking back >100% of outgoing salary;
using a prior-year TPE; signing a mid-season waivee whose pre-waiver salary exceeded the NTMLE.

Hard-capped at the **second apron** by: using the taxpayer MLE; aggregating salaries in a trade;
sending cash in a trade; using an outgoing S&T player's salary for matching.

The **room exception triggers no hard cap.** Hard caps run through June 30 and are never retroactive.
([Hoops Rumors: Hard Cap, Jan 2025](https://www.hoopsrumors.com/2025/01/hoops-rumors-glossary-hard-cap-4.html))

### 3f. Stretch provision
Waived salary may be stretched over `2 × remaining years + 1`. **Limit:** total stretched dead money
may not exceed **15% of the salary cap** in any season. This is what blocked Phoenix from fully
stretching Bradley Beal (they already carried $3.8M stretched for Little/Liddell), forcing Beal to
give back ~$13.9M of his ~$110.8M; the remaining ~$97M stretched over 5 years ≈ $19.4M/yr dead cap
through 2029-30.
([Forbes, July 2025](https://www.forbes.com/sites/bryantoporek/2025/07/04/why-the-phoenix-suns-cant-just-waive-and-stretch-bradley-beals-contract/))

---

## 4. Case studies (golden tests + narrative training data)

**Boston Celtics — the canonical unwind.** 2024 champs ran deep into the second apron; after Tatum's
May 2025 Achilles tear the projected 2025-26 bill hit ~$500M+. June 24, 2025: Jrue Holiday → Portland
for Anfernee Simons (~$4.7M salary saved, ~$35-40M tax saved, $72M of future money shed). June 25,
2025: Porzingis → Atlanta in a 3-team deal → Boston dropped ~$4.5M below the second apron and the
projected bill fell ~$540M → ~$280M. July 1, 2026: Jaylen Brown → Philadelphia for Paul George + 2
firsts + 2 seconds, explicitly a cap/flexibility trade tied to the lagging 2026-27 cap. Then used the
NTMLE on Mitchell Robinson (3yr/$47.4M) → first-apron hard cap. Brad Stevens: he didn't understand
how real the penalties were "until they were staring me in the face."

**Phoenix Suns — apron prison.** Over the second apron 2023-24 and 2024-25 (2032 first frozen). The
Durant trade (agreed June 22, finalized July 6, 2025) became a **record seven-team trade** — and
produced *no apron savings*. The escape was the Beal waive-and-stretch (§3f). July 2026: sent cash in
a trade → hard-capped at the second apron.

**Minnesota** — Oct 2024 KAT → Knicks "largely for financial reasons"; still finished 2024-25 over
the second apron (2032 pick frozen); escaped in 2025-26. July 2026: aggregated Randle + Naz Reid →
second-apron hard cap.

**Cleveland** — the only team over the second apron in 2025-26 (2033 first frozen, ~$98M tax). Feb 5,
2026: acquired Harden for Garland; Harden declined his option in June 2026, dropping them out of the
second apron; Mitchell extended 4yr/$273M on July 10, 2026.

**Denver** — let KCP walk in 2024; July 2025 traded MPJ + an unprotected 2032 first for Cam Johnson to
duck the second apron. July 2026: OKC weaponized restricted free agency and Denver **matched a
2yr/$12M offer sheet for Spencer Jones**, making them the only team currently over the 2026-27 second
apron (~$1.9M over) as a repeater.

**July 2026 offseason at large** — the apron drove everything: the Knicks won the 2026 title and still
let Mitchell Robinson walk rather than cross the second apron (Dolan: you'd "have to be suicidal");
OKC traded Dort, Joe, and Wiggins essentially for seconds, reportedly saving $300M+; Giannis (+Portis)
→ Miami via expanded TPE (first-apron hard cap); Kawhi → Toronto **on hold** pending the league's
cap-circumvention investigation into his $28M Aspiration endorsement; Wembanyama took the 25% max
(5yr/$252M) over a $302.8M supermax to preserve San Antonio's flexibility. 21 teams hard-capped for
2026-27. NBPA director David Kelly, July 10, 2026: "We are not fans of the second apron."

---

## 5. Front-office landscape

Every team now employs cap/CBA staff ("capologist"). Public tooling: **Spotrac** (de facto public
system of record, $30/yr premium), **capsheets.com** + the **Third Apron** newsletter (Yossi Gozlan —
the deepest public CBA-mechanics writing), **Sports Business Classroom** trackers, Hoops Rumors
glossary, **Salary Swish**, Fanspo/ESPN trade machines. Sportradar is the league's data/betting
partner — *not* a cap tool. No public report of any NBA team using an LLM for CBA/cap work.

**Documented pain points this project targets:** multi-constraint scenario planning done by hand
(7-team Durant trade; Boston's $540M→$280M engineering; OKC's sequenced dumps), CBA edge cases (Beal's
blocked stretch, unlikely incentives counting for aprons), deadline-day speed across 21 hard-capped
teams, and the knowledge vacuum left by Coon's retirement.

---

## 6. Validation of this project's architecture

**Where the fine-tuned specialist genuinely wins:** 2023-CBA-correct Q&A (generic models blur pre/post
-2023 rules — 110% vs 100% matching, tax-based vs apron-based MLE availability, old vs new repeater
rates); trade legality reasoning over a pasted cap sheet with *explanation* (trade machines validate
but don't explain; frontier models explain but misremember rules); multi-step scenario planning;
contract structuring; extension/exception bookkeeping; local/private operation.

**Where it can lose, and the mitigations built into the plan:**
1. *Staleness* — every threshold moves each July 1. → Anti-staleness training slice + eval probes:
   pasted numbers must always beat memorized ones.
2. *Arithmetic* — matching/tax math is exact and LLMs slip. → Decomposed arithmetic in training data,
   exact-dollar eval gate, CapEngine as ground truth.
3. *Frontier model + CBA in context is a strong baseline* — the 676-page CBA fits in modern context
   windows. → Our edge must be reasoning patterns + local operation, and the eval must measure
   against that baseline honestly.
4. *Rule drift* — NBPA is campaigning against the second apron; CBA talks loom after 2028-29. →
   Version-stamp the model ("2023 CBA, 2026-27 figures"); retraining is cheap by design.

---

## ⚠️ Open uncertainties to verify before they enter training data
- BAE amounts for 2024-25 / 2025-26 (~$4.7M / ~$5.1M) are approximate; 2026-27 BAE and two-way figures
  are single-sourced.
- 2025-26 minimum scale given as ≈6.7% below 2026-27; exact 0-YOS figure unverified.
- Cavaliers' 2025-26 tax bill (~$98M) and margin over the apron vary by source snapshot.
- Timberwolves' July 2026 aggregation → LaMelo Ball return is lightly sourced (fan sites).
- Warriors' 2026-27 second-apron hard cap: Bleacher Report says yes, Hoops Rumors' July 10 list omits
  them — likely a timing discrepancy.
