# Error analysis — hardcap v1 (masked SFT)

499 scored examples. A row can appear in more than one bucket.

## Failure kinds

| Kind | Rows | Share |
|---|---:|---:|
| invented figure | 341 | 68.3% |
| missing required figure | 228 | 45.7% |
| verdict flipped | 54 | 10.8% |
| degenerate loop | 2 | 0.4% |
| (clean) | 130 | 26.1% |

## Where each kind concentrates

| Kind | Scenario type | Rows |
|---|---|---:|
| invented figure | trade_legality | 95 |
| invented figure | apron_status | 50 |
| missing required figure | apron_status | 49 |
| missing required figure | anti_staleness | 45 |
| missing required figure | trade_legality | 44 |
| invented figure | tax_bill | 43 |
| missing required figure | tax_bill | 41 |
| invented figure | anti_staleness | 40 |
| invented figure | scenario_planning | 33 |
| verdict flipped | trade_legality | 31 |
| invented figure | exception_eligibility | 30 |
| missing required figure | scenario_planning | 29 |
| invented figure | hard_cap_consequence | 26 |
| invented figure | stretch_provision | 18 |
| missing required figure | stretch_provision | 12 |
| verdict flipped | stretch_provision | 9 |
| verdict flipped | hard_cap_consequence | 8 |

## Invented figures: fabricated, or just underived arithmetic?

912 flagged figures across all rows.

| Verdict | Count | Share |
|---|---:|---:|
| not derivable | 848 | 93.0% |
| derivable from provided figures | 64 | 7.0% |

Examples the model computed correctly from figures it was given:

```
$9,289,440 = $9,539,440 - $250,000  [trade_legality]
$55,362,183 = $250,000 + $55,112,183  [trade_legality]
$3,866,666 = $5,800,000 - $1,933,334  [apron_status]
$33,200,864 = $50,959,779 - $17,758,915  [scenario_planning]
$213,760,700 = $1 + $213,760,699  [anti_staleness]
$154,625,968 = $154,625,969 - $1  [trade_legality]
$7,580,000 = $40,932,000 - $33,352,000  [tax_bill]
$21,224,000 = $40,932,000 - $19,708,000  [tax_bill]
$28,804,000 = $46,996,000 - $18,192,000  [tax_bill]
$31,836,000 = $50,028,000 - $18,192,000  [tax_bill]
$34,868,000 = $40,932,000 - $6,064,000  [tax_bill]
$65,787,341 = $52,629,873 x 125%  [trade_legality]
```

### By scenario type — calculator problem or grounding problem?

*Derivable is a floor: the checker tries simple operations only, so multi-step arithmetic reads as non-derivable.*

| Scenario type | Flagged | Derivable (floor) | Read as |
|---|---:|---:|---|
| tax_bill | 210 | 24 (11%) | mostly untraceable — grounding data |
| trade_legality | 194 | 16 (8%) | mostly untraceable — grounding data |
| apron_status | 182 | 1 (1%) | mostly untraceable — grounding data |
| scenario_planning | 148 | 14 (9%) | mostly untraceable — grounding data |
| anti_staleness | 62 | 4 (6%) | mostly untraceable — grounding data |
| hard_cap_consequence | 41 | 0 (0%) | mostly untraceable — grounding data |
| stretch_provision | 35 | 2 (6%) | mostly untraceable — grounding data |
| exception_eligibility | 33 | 1 (3%) | mostly untraceable — grounding data |
| exception_survey | 5 | 2 (40%) | some real arithmetic |
| buyout_market | 1 | 0 (0%) | mostly untraceable — grounding data |
| draft_penalty | 1 | 0 (0%) | mostly untraceable — grounding data |

## Samples

### invented figure

- **tax_bill** — expected verdict `None`, figures 0/2, invented $1,900,000, $2,695,091, $190,590,091
  > We owe $1,900,000. Tax salary is $190,590,091 against a line of $187,895,000, which puts us $2,695,091 into the tax. That is the entire bill: a first-bracket rate applied to $2,695,091 produces $1,900,000, and because the escalator has not been triggered, the shape of the bill is flat rather than steep. The useful part…
- **trade_legality** — expected verdict `ILLEGAL`, figures 2/3, invented $9,289,440, $55,362,183
  > **Verdict: ILLEGAL.** This one is dead as drawn up. We send out $43,889,747 and take back $64,651,623. Sitting over the tax line, our matching limit is $55,362,183 under 125% + $250,000. That is $9,289,440 more than we are allowed to absorb, and there is no exception that closes a gap that size. Oklahoma City would sit…
- **trade_legality** — expected verdict `LEGAL`, figures 2/3, invented $5,109,000, $9,997,663, $150,647,124
  > **Verdict: ILLEGAL.** This one is dead as drawn up. We send out $4,888,663 and take back $7,465,464. Sitting under the tax line, our matching limit is $9,997,663 under outgoing + $5,109,000. Washington would sit at $150,647,124, which is where the real answer lies — the structure that would have worked, with only margi…

### missing required figure

- **tax_bill** — expected verdict `None`, figures 0/2, invented $1,900,000, $2,695,091, $190,590,091
  > We owe $1,900,000. Tax salary is $190,590,091 against a line of $187,895,000, which puts us $2,695,091 into the tax. That is the entire bill: a first-bracket rate applied to $2,695,091 produces $1,900,000, and because the escalator has not been triggered, the shape of the bill is flat rather than steep. The useful part…
- **trade_legality** — expected verdict `ILLEGAL`, figures 2/3, invented $9,289,440, $55,362,183
  > **Verdict: ILLEGAL.** This one is dead as drawn up. We send out $43,889,747 and take back $64,651,623. Sitting over the tax line, our matching limit is $55,362,183 under 125% + $250,000. That is $9,289,440 more than we are allowed to absorb, and there is no exception that closes a gap that size. Oklahoma City would sit…
- **trade_legality** — expected verdict `LEGAL`, figures 2/3, invented $5,109,000, $9,997,663, $150,647,124
  > **Verdict: ILLEGAL.** This one is dead as drawn up. We send out $4,888,663 and take back $7,465,464. Sitting under the tax line, our matching limit is $9,997,663 under outgoing + $5,109,000. Washington would sit at $150,647,124, which is where the real answer lies — the structure that would have worked, with only margi…

### verdict flipped

- **trade_legality** — expected verdict `LEGAL`, figures 2/3, invented $5,109,000, $9,997,663, $150,647,124
  > **Verdict: ILLEGAL.** This one is dead as drawn up. We send out $4,888,663 and take back $7,465,464. Sitting under the tax line, our matching limit is $9,997,663 under outgoing + $5,109,000. Washington would sit at $150,647,124, which is where the real answer lies — the structure that would have worked, with only margi…
- **trade_legality** — expected verdict `LEGAL`, figures 3/3
  > **Verdict: ILLEGAL.** This one is dead as drawn up. We send out $22,404,237 and take back $16,346,000. Sitting over the second apron, our matching limit is $22,404,237 under 100% of outgoing salary. Portland would sit at $214,064,144, above its first apron hard cap of $195,945,000 -- that is the gap I would fight on, b…
- **trade_legality** — expected verdict `ILLEGAL`, figures 2/3, invented $2,627,000, $5,000,599, $150,000,092
  > **Verdict: LEGAL.** This is fine as constructed. We send out $2,373,599 and take back $6,210,588. Sitting under the tax line, our matching limit is $5,000,599 under outgoing + $2,627,000. The return is inside that, so the money is fine. Afterward we sit at $150,000,092. The cost is flexibility: this hard-caps us at the…

### degenerate loop

- **tax_bill** — expected verdict `None`, figures 1/2, invented $30,949,650, $125,000,400
  > We owe $125,000,400. Team is over the second apron, and that is what governs: the standard schedule applies, plus the multiple on the overage. Tax salary is $221,702,560 against a $187,895,000 line, which puts $33,807,560 into the tax, and that is the figure to work from rather than the payroll figure, since the two re…
- **tax_bill** — expected verdict `None`, figures 0/2, invented $44,259,750, $46,901,250, $49,743,750
  > We owe $200,000,900. Team is a repeater, so the schedule starts at the deepest rates available. The first $5,685,000 of tax salary is charged at $3.00 per dollar, which is $17,055,000. The next $5,685,000 is charged at $3.25 per dollar, which is $18,476,250. The next $5,685,000 is charged at $5.50 per dollar, which is …
