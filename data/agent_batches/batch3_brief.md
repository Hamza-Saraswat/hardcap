# Writing batch 3

You are writing training examples for a basketball salary cap assistant. Each scenario below
has already been solved by a deterministic rules engine. Your job is to express the answer in
natural language -- the way a sharp front-office analyst would say it to a general manager.

## Rules

1. **Use only the figures in the trace.** Every dollar amount you write must appear in that
   scenario's trace or its cap sheet. Do not derive new numbers, even correct ones. An
   automatic checker rejects any figure the engine did not compute.
2. **Exact amounts, comma-formatted.** `$12,345,678`. Never `$12.3 million`, never "about",
   never "roughly".
3. **Include every required figure** listed for the scenario.
4. **Open with the verdict** when one is given: `**Verdict: LEGAL.**` or
   `**Verdict: ILLEGAL.**`, then explain. On a LEGAL verdict, keep negations like "cannot"
   or "not allowed" out of the first few sentences -- a checker reads the opening to confirm
   the verdict, and an early negation reads as a rejection.
5. **Vary your writing.** These examples exist to teach the model range. Do not use the same
   opening or structure twice in this batch. Some answers can lead with the number, some with
   the rule, some with the consequence. Length can vary too.
6. **Sound like an analyst, not a textbook.** Direct, specific, willing to volunteer the
   thing the GM did not ask about but needs to know. No throat-clearing, no restating the
   question back.

## Output format

Write one JSON object per line to `data/agent_batches/batch3_responses.jsonl`, nothing else in the file:

    {"id": 0, "response": "**Verdict: ILLEGAL.** ..."}

The `id` must match the scenario number below.

---

## Scenario 0 -- tax_bill

**What the user said:**

```
2025-26 LEAGUE THRESHOLDS
  Salary cap:          $154,647,000
  Luxury tax line:     $187,895,000
  First apron:         $195,945,000
  Second apron:        $207,824,000
  Non-taxpayer MLE:    $14,104,000
  Taxpayer MLE:        $5,685,000
  Room exception:      $8,781,000
  Tax bracket width:   $5,685,000

NEW ORLEANS -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Amari Vasquez,6021150,0,2
Micah Kalinic,22116345,0,3
Trey Halvorsen,13034386,0,1
Julian Cordero,5595988,0,1
Marcus Achiuwa,3341192,0,1
Corey Amadi,10951118,0,1
Rashad Sabonis,5344856,0,2
Dante Duval,3034823,0,3
Deni Osei,42977941,0,2
Brennan Ferreira,4639899,0,3
Goran Marsh,48255719,0,1
Kristaps Jokubaitis,21063175,0,1
Kobe Stavros,4364565,0,4

Roster count: 13

Ownership wants the tax number. What do we owe, and how does it break down?
```

**Ground truth:** {"tax_salary": 190741157, "tax_line": 187895000, "amount_over": 2846157, "is_repeater": false, "total": 2846157, "brackets": [{"index": 1, "amount": 2846157, "rate": 1.0, "owed": 2846157}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $2,846,157, $2,846,157

**Computation trace (the only figures you may use):**

```
  1. New Orleans tax salary = $190,741,157
  2. 2025-26 luxury tax line = $187,895,000
  3. Amount over the tax line = $2,846,157 ($190,741,157 - $187,895,000)
  4. Rate schedule: standard (2025-26) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $2,846,157 at $1.00 per dollar = $2,846,157
  6. Total luxury tax owed = $2,846,157
  7. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 1 -- trade_legality

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

NEW ORLEANS -- 2024-25 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Goran Osei | $5,971,273 | -- | 2 |
| Zion Jokubaitis | $20,219,456 | -- | 1 |
| Darnell Kearns | $23,871,470 | -- | 1 |
| Corey Ibarra | $4,412,767 | -- | 4 |
| Zion Novak | $9,261,206 | -- | 2 |
| Kristaps Dumont | $24,671,767 | -- | 2 |
| Bogdan Ellington | $41,076,483 | -- | 3 |
| Brennan Okoro | $2,808,013 | -- | 2 |
| Kellen Okoro | $44,593,897 | -- | 3 |
| Marcus Kearns | $8,483,187 | -- | 2 |
| Marcus Novak | $4,541,795 | -- | 2 |
| Zion Ibarra | $3,501,311 | -- | 4 |
| Malik Marsh | $9,117,603 | -- | 3 |

Roster count: 13

We're discussing a trade that sends Goran Osei to another team for Andre Kalinic at $5,563,256. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 5971273, "incoming_salary": 5563256, "max_incoming": 5971273, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 202122211, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $5,971,273, $5,563,256, $5,971,273

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: New Orleans
  2. --- New Orleans (2024-25) --- (apron salary $202,530,228, over the second apron)
  3. New Orleans outgoing salary = $5,971,273 (Goran Osei $5,971,273)
  4. New Orleans incoming salary = $5,563,256 (Andre Kalinic $5,563,256)
  5. New Orleans matching limit = $5,971,273 (100% of outgoing salary (team is over the first apron))
  6. New Orleans apron salary after the trade = $202,122,211
  7. Verdict: LEGAL
```


## Scenario 2 -- trade_legality

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

TORONTO -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Kristaps Lindqvist | $8,494,108 | -- | 2 |
| Luka Petrov | $9,280,904 | -- | 4 |
| Alperen Okoro | $8,779,618 | -- | 4 |
| Cam Kalinic | $18,523,865 | -- | 3 |
| Luka Amadi | $8,209,180 | -- | 4 |
| Cam Lindqvist | $4,682,906 | -- | 2 |
| Darnell Osei | $54,741,062 | -- | 3 |
| Brennan Boateng | $4,226,835 | -- | 4 |
| Santi Achiuwa | $7,490,635 | -- | 1 |
| Andre Whitfield | $5,577,880 | -- | 1 |
| Jalil Duval | $51,343,349 | -- | 3 |
| Andre Sabonis | $5,069,905 | -- | 3 |
| Terrance Petrov | $7,113,878 | -- | 3 |
| Brennan Ibarra | $6,925,061 | -- | 3 |
| Zion Kearns | $5,771,722 | -- | 3 |

Roster count: 15

We're discussing a trade that sends Brennan Ibarra to another team for Julian Kalinic at $13,698,757. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 6925061, "incoming_salary": 13698757, "max_incoming": 14100122, "matching_rule": "200% + $250,000 (outgoing at or below $9,096,000)", "apron_level": "over the tax line", "apron_salary_after": 213004604, "hard_cap_triggered": "first apron", "violations": ["Toronto: hard cap exceeded -- Toronto would sit at $213,004,604, above its first apron hard cap of $209,015,000 -- over by $3,989,604"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $6,925,061, $13,698,757, $14,100,122

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Toronto
  2. --- Toronto (2026-27) --- (apron salary $206,230,908, over the tax line)
  3. Toronto outgoing salary = $6,925,061 (Brennan Ibarra $6,925,061)
  4. Toronto incoming salary = $13,698,757 (Julian Kalinic $13,698,757)
  5. Toronto matching limit = $14,100,122 (200% + $250,000 (outgoing at or below $9,096,000))
  6. Toronto hard-capped at the first apron = $209,015,000 (took back more than 100% of outgoing salary)
  7. Toronto apron salary after the trade = $213,004,604
  8. VIOLATION -- hard cap exceeded (Toronto would sit at $213,004,604, above its first apron hard cap of $209,015,000 -- over by $3,989,604)
  9. Verdict: ILLEGAL
```


## Scenario 3 -- tax_bill

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

MIAMI -- 2024-25 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Darnell Ferreira | $36,088,715 | -- | 3 |
| Kellen Reddish | $8,508,005 | -- | 2 |
| Deni Amadi | $2,376,005 | -- | 1 |
| Trey Osei | $2,499,604 | -- | 1 |
| Zion Amadi | $4,365,361 | -- | 3 |
| Jalil Nakamura | $9,531,931 | -- | 3 |
| Trey Vasquez | $5,463,621 | -- | 2 |
| Dante Jokubaitis | $4,888,262 | -- | 1 |
| Jaylen Ellington | $23,079,543 | -- | 4 |
| Kellen Cordero | $20,071,015 | -- | 4 |
| Dante Ferreira | $8,257,232 | -- | 2 |
| Corey Dumont | $5,313,416 | -- | 2 |
| Corey Amadi | $40,975,338 | -- | 1 |

Roster count: 13
Repeater taxpayer: yes

Ownership wants the tax number. What do we owe, and how does it break down?
```

**Ground truth:** {"tax_salary": 171418048, "tax_line": 170814000, "amount_over": 604048, "is_repeater": true, "total": 1510120, "brackets": [{"index": 1, "amount": 604048, "rate": 2.5, "owed": 1510120}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $1,510,120, $604,048

**Computation trace (the only figures you may use):**

```
  1. Miami tax salary = $171,418,048
  2. 2024-25 luxury tax line = $170,814,000
  3. Amount over the tax line = $604,048 ($171,418,048 - $170,814,000)
  4. Rate schedule: repeater (2024-25) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $604,048 at $2.50 per dollar = $1,510,120
  6. Total luxury tax owed = $1,510,120
  7. Repeater status applies (paid the tax in 3 of the prior 4 seasons)
  8. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 4 -- scenario_planning

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

MIAMI -- 2024-25 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Kobe Rees | $4,552,975 | -- | 2 |
| Marcus Ibarra | $6,379,141 | -- | 4 |
| Nico Duval | $21,186,843 | -- | 2 |
| Zion Stavros | $5,095,300 | -- | 1 |
| Elijah Petrov | $22,374,814 | -- | 1 |
| Julian Kearns | $6,386,360 | -- | 1 |
| Brennan Marsh | $36,989,906 | -- | 4 |
| Rashad Ferreira | $6,326,586 | -- | 2 |
| Deni Petrov | $3,694,969 | -- | 2 |
| Zion Osei | $13,918,831 | -- | 3 |
| Elijah Osei | $14,598,781 | -- | 4 |
| Malik Halvorsen | $2,753,398 | -- | 2 |
| Cam Halvorsen | $40,595,837 | -- | 3 |
| Tobias Achiuwa | $4,994,216 | -- | 3 |
| Andre Jokubaitis | $2,180,922 | -- | 4 |

Roster count: 15

Ownership wants us out of the second apron. Walk me through how we do it.
```

**Ground truth:** {"apron_salary": 192028879, "second_apron": 188931000, "overage": 3097879, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Deni Petrov", "salary": 3694969, "surplus": 597090}, {"player": "Kobe Rees", "salary": 4552975, "surplus": 1455096}, {"player": "Tobias Achiuwa", "salary": 4994216, "surplus": 1896337}, {"player": "Zion Stavros", "salary": 5095300, "surplus": 1997421}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $3,097,879

**Computation trace (the only figures you may use):**

```
  1. Miami apron salary = $192,028,879
  2. 2024-25 second apron = $188,931,000
  3. Amount over the second apron = $3,097,879
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Deni Petrov alone clears the gap = $597,090 ($3,694,969 out against $3,097,879 of overage, assuming no salary comes back)
  7. Moving Kobe Rees alone clears the gap = $1,455,096 ($4,552,975 out against $3,097,879 of overage, assuming no salary comes back)
  8. Moving Tobias Achiuwa alone clears the gap = $1,896,337 ($4,994,216 out against $3,097,879 of overage, assuming no salary comes back)
  9. Moving Zion Stavros alone clears the gap = $1,997,421 ($5,095,300 out against $3,097,879 of overage, assuming no salary comes back)
```


## Scenario 5 -- trade_legality

**What the user said:**

```
2025-26 LEAGUE THRESHOLDS
  Salary cap:          $154,647,000
  Luxury tax line:     $187,895,000
  First apron:         $195,945,000
  Second apron:        $207,824,000
  Non-taxpayer MLE:    $14,104,000
  Taxpayer MLE:        $5,685,000
  Room exception:      $8,781,000
  Tax bracket width:   $5,685,000

ATLANTA -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Amari Kalinic,42655767,0,4
Amari Sabonis,6824171,0,1
Zion Cordero,26932938,0,4
Deni Beauchamp,44946140,0,2
Goran Kearns,5472204,0,3
Alperen Okoro,28421533,0,2
Terrance Ellington,3361777,0,3
Trey Kalinic,6705565,0,1
Bogdan Duval,3803093,0,1
Malik Vasquez,7183301,0,3
Rashad Cordero,3375272,0,3
Kobe Okoro,4005288,0,1
Amari Dumont,7832417,0,1

Roster count: 13

We're discussing a trade that sends Bogdan Duval to another team for Andre Dumont at $6,869,178. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 3803093, "incoming_salary": 6869178, "max_incoming": 7856186, "matching_rule": "200% + $250,000 (outgoing at or below $8,527,000)", "apron_level": "over the tax line", "apron_salary_after": 194585551, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $3,803,093, $6,869,178, $7,856,186

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Atlanta
  2. --- Atlanta (2025-26) --- (apron salary $191,519,466, over the tax line)
  3. Atlanta outgoing salary = $3,803,093 (Bogdan Duval $3,803,093)
  4. Atlanta incoming salary = $6,869,178 (Andre Dumont $6,869,178)
  5. Atlanta matching limit = $7,856,186 (200% + $250,000 (outgoing at or below $8,527,000))
  6. Atlanta hard-capped at the first apron = $195,945,000 (took back more than 100% of outgoing salary)
  7. Atlanta apron salary after the trade = $194,585,551
  8. Atlanta stays under its first apron hard cap = $1,359,449 ($195,945,000 - $194,585,551 of room to spare)
  9. Verdict: LEGAL
```


## Scenario 6 -- stretch_provision

**What the user said:**

```
2025-26 LEAGUE THRESHOLDS
  Salary cap:          $154,647,000
  Luxury tax line:     $187,895,000
  First apron:         $195,945,000
  Second apron:        $207,824,000
  Non-taxpayer MLE:    $14,104,000
  Taxpayer MLE:        $5,685,000
  Room exception:      $8,781,000
  Tax bracket width:   $5,685,000

If we waive and stretch Deni Dumont -- $93,100,000 left over 1 year -- what does the dead money look like, and is it even allowed?
```

**Ground truth:** {"legal": false, "remaining_salary": 93100000, "years_remaining": 1, "stretch_years": 3, "annual_dead_money": 31033333, "existing_stretched": 7500000, "limit": 23197050, "givebacks_required": 46008849, "reason": "the stretch is not legal as structured: $38,533,333 of dead money would exceed the $23,197,050 ceiling by $15,336,283 per season. The player would have to give back roughly $46,008,849 for the waiver to work"}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $31,033,333, $23,197,050

**Computation trace (the only figures you may use):**

```
  1. Salary remaining on the contract = $93,100,000
  2. Years remaining (1)
  3. Stretch period (2 x 1 + 1 = 3 seasons)
  4. Annual dead money if stretched = $31,033,333 ($93,100,000 / 3)
  5. Dead money already stretched = $7,500,000
  6. Total stretched dead money = $38,533,333
  7. Limit (15% of the 2025-26 cap) = $23,197,050 (15% x $154,647,000)
  8. VIOLATION -- exceeds the dead-money ceiling = $15,336,283
  9. Approximate giveback required = $46,008,849 ($15,336,283 x 3 seasons)
```


## Scenario 7 -- exception_eligibility

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

PORTLAND -- 2026-27 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Rashad Halvorsen,11253613,0,1
Micah Stavros,9725039,0,1
Zion Petrov,11154693,0,4
Julian Cordero,24911325,0,2
Luka Boateng,56747137,0,2
Micah Ibarra,5112212,0,2
Micah Okoro,9807118,0,3
Kristaps Whitfield,22017973,0,4
Andre Jokubaitis,6164409,0,2
Kristaps Ibarra,3415614,0,3
Elijah Kearns,5592462,0,3
Julian Kearns,5259287,0,4
Nico Achiuwa,8160102,0,2
Luka Ibarra,22726578,0,4
Isaiah Amadi,10370995,0,1

Roster count: 15

Can we sign Luka Vasquez for $5,119,987 using the bi-annual exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "bi-annual exception", "salary": 5119987, "hard_cap_triggered": "none", "apron_level": "over the first apron", "apron_salary_after": 217538544, "reasons": ["bi-annual exception is unavailable over the first apron", "Portland already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $5,119,987

**Computation trace (the only figures you may use):**

```
  1. Portland apron salary before signing = $212,418,557 (over the first apron)
  2. Proposed salary for Luka Vasquez = $5,119,987
  3. Exception: bi-annual exception
  4. VIOLATION -- bi-annual exception unavailable (unavailable over the first apron)
  5. Portland apron salary after signing = $217,538,544
  6. VIOLATION -- roster is full (15-man limit reached)
  7. Verdict: ILLEGAL
```


## Scenario 8 -- anti_staleness

**What the user said:**

```
2029-30 LEAGUE THRESHOLDS
  Salary cap:          $180,808,000
  Luxury tax line:     $219,683,000
  First apron:         $229,095,000
  Second apron:        $242,983,000
  Non-taxpayer MLE:    $16,489,000
  Taxpayer MLE:        $6,647,000
  Room exception:      $10,266,000
  Tax bracket width:   $6,647,000
  Bi-annual exception: $6,003,000

UTAH -- 2029-30 CAP SHEET
Corey Lindqvist         $7,121,521
Goran Novak             $6,479,156
Amari Halvorsen        $61,317,759
Jalil Nakamura          $5,846,163
Andre Boateng           $2,693,856
Goran Ferreira          $4,723,934
Tobias Reddish          $6,849,597
Goran Reddish           $6,929,292
Micah Duval            $19,164,493
Nikola Nakamura        $23,379,167
Kellen Duval            $6,338,100
Kobe Petrov             $5,345,336
Jaylen Halvorsen       $16,373,793
Elijah Lindqvist        $2,753,824
Nico Marsh             $51,310,322

Roster count: 15

Using the 2029-30 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2029-30", "apron_salary": 226626313, "apron_level": "over the tax line", "first_apron_provided": 229095000, "second_apron_provided": 242983000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $226,626,313, $242,983,000

**Computation trace (the only figures you may use):**

```
  1. Utah apron salary = $226,626,313
  2. 2029-30 first apron (from the figures provided) = $229,095,000
  3. 2029-30 second apron (from the figures provided) = $242,983,000
  4. Position: over the tax line
  5. Room below the second apron = $16,356,687
```


## Scenario 9 -- apron_status

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

MIAMI -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Micah Marsh,10014957,0,2
Luka Okoro,5893709,0,2
Zion Halvorsen,3318105,0,1
Cam Ferreira,4600815,0,4
Bogdan Jokubaitis,3835465,0,1
Rashad Kearns,9968328,0,1
Micah Stavros,2645569,0,3
Darnell Osei,2742340,0,4
Marcus Dumont,5197368,0,4
Nico Stavros,29718870,0,1
Kellen Kearns,9988171,0,3
Julian Nakamura,27023085,0,1
Isaiah Dumont,7364911,0,3
Brennan Achiuwa,49205800,0,3

Roster count: 14

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 171517493, "unlikely_incentives": 0, "apron_salary": 171517493, "apron_level": "over the tax line", "room_to_first_apron": 6614507, "room_to_second_apron": 17413507}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $171,517,493

**Computation trace (the only figures you may use):**

```
  1. Miami salaries plus likely incentives = $171,517,493
  2. Apron salary = $171,517,493
  3. 2024-25 luxury tax line = $170,814,000
  4. 2024-25 first apron = $178,132,000
  5. 2024-25 second apron = $188,931,000
  6. Position: over the tax line
  7. Amount above the tax line = $703,493
  8. Room below the first apron = $6,614,507
  9. Room below the second apron = $17,413,507
```


## Scenario 10 -- trade_legality

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

NEW ORLEANS -- 2024-25 CAP SHEET
Tobias Stavros           $2,651,927
Julian Stavros          $25,824,637
Goran Achiuwa           $39,544,338
Tobias Ferreira         $15,860,098
Kristaps Nakamura        $3,117,358
Micah Cordero           $40,146,789
Malik Amadi             $14,708,347
Malik Novak              $8,665,073
Jaylen Sabonis          $13,720,906
Nikola Ferreira          $2,223,377
Terrance Petrov          $8,646,703
Elijah Duval             $6,219,417
Dante Boateng            $3,411,493
Goran Brantley           $7,127,805

Roster count: 14

We're discussing a trade that sends Tobias Stavros and Micah Cordero to another team for Zion Novak at $48,453,002. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 42798716, "incoming_salary": 48453002, "max_incoming": 42798716, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 197522554, "hard_cap_triggered": "none", "violations": ["New Orleans: second-apron aggregation ban -- New Orleans is over the second apron ($191,868,268 vs $188,931,000) and may not combine 2 salaries in one trade", "New Orleans: salary matching -- New Orleans takes back $48,453,002 but may only absorb $42,798,716 under 100% of outgoing salary (team is over the first apron) -- over by $5,654,286"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $42,798,716, $48,453,002, $42,798,716

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: New Orleans
  2. --- New Orleans (2024-25) --- (apron salary $191,868,268, over the second apron)
  3. New Orleans outgoing salary = $42,798,716 (Tobias Stavros $2,651,927, Micah Cordero $40,146,789)
  4. New Orleans incoming salary = $48,453,002 (Zion Novak $48,453,002)
  5. VIOLATION -- second-apron aggregation ban (New Orleans is over the second apron ($191,868,268 vs $188,931,000) and may not combine 2 salaries in one trade)
  6. New Orleans matching limit = $42,798,716 (100% of outgoing salary (team is over the first apron))
  7. VIOLATION -- salary matching (New Orleans takes back $48,453,002 but may only absorb $42,798,716 under 100% of outgoing salary (team is over the first apron) -- over by $5,654,286)
  8. New Orleans apron salary after the trade = $197,522,554
  9. Verdict: ILLEGAL
```


## Scenario 11 -- scenario_planning

**What the user said:**

```
2025-26 LEAGUE THRESHOLDS
  Salary cap:          $154,647,000
  Luxury tax line:     $187,895,000
  First apron:         $195,945,000
  Second apron:        $207,824,000
  Non-taxpayer MLE:    $14,104,000
  Taxpayer MLE:        $5,685,000
  Room exception:      $8,781,000
  Tax bracket width:   $5,685,000

TORONTO -- 2025-26 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Corey Petrov | $5,926,144 | -- | 2 |
| Deni Kearns | $16,137,019 | -- | 3 |
| Micah Kearns | $9,238,211 | -- | 2 |
| Amari Whitfield | $6,573,884 | -- | 4 |
| Alperen Cordero | $5,442,864 | -- | 3 |
| Malik Novak | $9,445,422 | -- | 2 |
| Kobe Halvorsen | $39,349,503 | -- | 4 |
| Rashad Marsh | $9,228,363 | -- | 4 |
| Alperen Stavros | $54,126,450 | -- | 4 |
| Jaylen Jokubaitis | $10,755,070 | -- | 2 |
| Malik Achiuwa | $7,724,341 | -- | 2 |
| Micah Duval | $11,812,339 | -- | 1 |
| Devonte Cordero | $5,746,389 | -- | 4 |
| Luka Whitfield | $24,855,444 | -- | 1 |
| Zion Reddish | $7,190,868 | -- | 1 |

Roster count: 15

What's the cleanest path under the second apron from here?
```

**Ground truth:** {"apron_salary": 223552311, "second_apron": 207824000, "overage": 15728311, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Deni Kearns", "salary": 16137019, "surplus": 408708}, {"player": "Luka Whitfield", "salary": 24855444, "surplus": 9127133}, {"player": "Kobe Halvorsen", "salary": 39349503, "surplus": 23621192}, {"player": "Alperen Stavros", "salary": 54126450, "surplus": 38398139}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $15,728,311

**Computation trace (the only figures you may use):**

```
  1. Toronto apron salary = $223,552,311
  2. 2025-26 second apron = $207,824,000
  3. Amount over the second apron = $15,728,311
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Deni Kearns alone clears the gap = $408,708 ($16,137,019 out against $15,728,311 of overage, assuming no salary comes back)
  7. Moving Luka Whitfield alone clears the gap = $9,127,133 ($24,855,444 out against $15,728,311 of overage, assuming no salary comes back)
  8. Moving Kobe Halvorsen alone clears the gap = $23,621,192 ($39,349,503 out against $15,728,311 of overage, assuming no salary comes back)
  9. Moving Alperen Stavros alone clears the gap = $38,398,139 ($54,126,450 out against $15,728,311 of overage, assuming no salary comes back)
```


## Scenario 12 -- apron_status

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

MIAMI -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Trey Dumont,21283621,0,4
Deni Ferreira,7310043,0,4
Deni Novak,6671892,0,3
Rashad Rees,3589415,0,2
Santi Reddish,4911681,0,4
Micah Lindqvist,37305988,0,4
Isaiah Achiuwa,6594428,0,3
Terrance Kearns,4525549,0,1
Trey Ellington,7444168,0,1
Malik Dumont,7239400,0,3
Deni Cordero,5389492,0,3
Isaiah Rees,35467043,0,4
Terrance Dumont,3752319,0,2
Malik Brantley,5373727,0,1
Marcus Marsh,22310491,0,1

Roster count: 15

Are we over the second apron? How much room do we have?
```

**Ground truth:** {"tax_salary": 179169257, "unlikely_incentives": 0, "apron_salary": 179169257, "apron_level": "over the first apron", "room_to_first_apron": -1037257, "room_to_second_apron": 9761743}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $179,169,257

**Computation trace (the only figures you may use):**

```
  1. Miami salaries plus likely incentives = $179,169,257
  2. Apron salary = $179,169,257
  3. 2024-25 luxury tax line = $170,814,000
  4. 2024-25 first apron = $178,132,000
  5. 2024-25 second apron = $188,931,000
  6. Position: over the first apron
  7. Amount above the tax line = $8,355,257
  8. Amount above the first apron = $1,037,257
  9. Room below the second apron = $9,761,743
```


## Scenario 13 -- exception_eligibility

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

MEMPHIS -- 2026-27 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Santi Beauchamp,6273215,0,2
Julian Sabonis,5361803,0,4
Julian Amadi,13469968,0,2
Tobias Nakamura,3946219,0,3
Dante Stavros,4634559,0,3
Terrance Nakamura,3574713,0,3
Corey Lindqvist,5899790,0,1
Rashad Rees,8838206,0,1
Julian Novak,8930059,0,3
Alperen Dumont,46818815,0,1
Devonte Ibarra,17615916,0,1
Julian Jokubaitis,19576449,0,1
Andre Rees,5775449,0,2
Andre Duval,17050328,0,1

Roster count: 14

Can we sign Rashad Stavros for $4,872,890 using the taxpayer mid-level exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": true, "exception": "taxpayer mid-level exception", "salary": 4872890, "hard_cap_triggered": "second apron", "apron_level": "under the tax line", "apron_salary_after": 172638379, "reasons": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $4,872,890

**Computation trace (the only figures you may use):**

```
  1. Memphis apron salary before signing = $167,765,489 (under the tax line)
  2. Proposed salary for Rashad Stavros = $4,872,890
  3. Exception: taxpayer mid-level exception
  4. taxpayer mid-level exception maximum = $6,064,000
  5. Room remaining within the exception = $1,191,110
  6. Memphis apron salary after signing = $172,638,379
  7. Hard cap: second apron = $221,686,000
  8. Room below the hard cap = $49,047,621
  9. Verdict: LEGAL
```


## Scenario 14 -- exception_survey

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

TORONTO -- 2026-27 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Kellen Lindqvist,2582779,0,3
Malik Amadi,5766263,0,3
Kobe Jokubaitis,8107454,0,3
Santi Vasquez,7867776,0,4
Zion Kearns,7707457,0,3
Kellen Achiuwa,6619465,0,1
Kellen Osei,8348464,0,2
Santi Ferreira,4214598,0,3
Luka Osei,44499399,0,4
Goran Sabonis,12291730,0,2
Amari Petrov,47303625,0,4
Darnell Nakamura,11199839,0,4
Nico Petrov,26198017,0,1
Malik Rees,12111580,0,3

Roster count: 14

Which exceptions can we actually use at this payroll?
```

**Ground truth:** {"apron_level": "over the tax line", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": true, "amount": 15044000, "reason": "available at $15,044,000; using it hard-caps the team at the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 6064000, "reason": "available at $6,064,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": true, "amount": 5477000, "reason": "available at $5,477,000; using it hard-caps the team at the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Toronto apron salary = $204,818,446 (over the tax line)
  2. 2026-27 first apron = $209,015,000
  3. 2026-27 second apron = $221,686,000
  4. non-taxpayer mid-level exception: available = $15,044,000 (available at $15,044,000; using it hard-caps the team at the first apron)
  5. taxpayer mid-level exception: available = $6,064,000 (available at $6,064,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: available = $5,477,000 (available at $5,477,000; using it hard-caps the team at the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 15 -- trade_legality

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

NEW ORLEANS -- 2024-25 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Malik Cordero | $26,766,660 | -- | 4 |
| Julian Amadi | $2,552,054 | -- | 1 |
| Marcus Beauchamp | $7,089,852 | -- | 2 |
| Kobe Brantley | $8,621,007 | -- | 4 |
| Jalil Whitfield | $2,088,000 | -- | 1 |
| Malik Duval | $44,211,382 | -- | 4 |
| Bogdan Lindqvist | $2,986,214 | -- | 2 |
| Micah Vasquez | $2,589,459 | -- | 4 |
| Kellen Beauchamp | $6,577,197 | -- | 4 |
| Jalil Ellington | $7,176,581 | -- | 3 |
| Zion Amadi | $5,247,887 | -- | 4 |
| Rashad Whitfield | $4,549,622 | -- | 4 |
| Julian Okoro | $5,621,185 | -- | 3 |
| Nico Ibarra | $13,039,150 | -- | 3 |

Roster count: 14

We're discussing a trade that sends Zion Amadi to another team for Darnell Cordero at $13,274,315. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 5247887, "incoming_salary": 13274315, "max_incoming": 10745774, "matching_rule": "200% + $250,000 (outgoing at or below $7,752,000)", "apron_level": "under the tax line", "apron_salary_after": 147142678, "hard_cap_triggered": "first apron", "violations": ["New Orleans: salary matching -- New Orleans takes back $13,274,315 but may only absorb $10,745,774 under 200% + $250,000 (outgoing at or below $7,752,000) -- over by $2,528,541"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $5,247,887, $13,274,315, $10,745,774

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: New Orleans
  2. --- New Orleans (2024-25) --- (apron salary $139,116,250, under the tax line)
  3. New Orleans outgoing salary = $5,247,887 (Zion Amadi $5,247,887)
  4. New Orleans incoming salary = $13,274,315 (Darnell Cordero $13,274,315)
  5. New Orleans matching limit = $10,745,774 (200% + $250,000 (outgoing at or below $7,752,000))
  6. VIOLATION -- salary matching (New Orleans takes back $13,274,315 but may only absorb $10,745,774 under 200% + $250,000 (outgoing at or below $7,752,000) -- over by $2,528,541)
  7. New Orleans hard-capped at the first apron = $178,132,000 (took back more than 100% of outgoing salary)
  8. New Orleans apron salary after the trade = $147,142,678
  9. New Orleans stays under its first apron hard cap = $30,989,322 ($178,132,000 - $147,142,678 of room to spare)
  10. Verdict: ILLEGAL
```


## Scenario 16 -- tax_bill

**What the user said:**

```
2025-26 LEAGUE THRESHOLDS
  Salary cap:          $154,647,000
  Luxury tax line:     $187,895,000
  First apron:         $195,945,000
  Second apron:        $207,824,000
  Non-taxpayer MLE:    $14,104,000
  Taxpayer MLE:        $5,685,000
  Room exception:      $8,781,000
  Tax bracket width:   $5,685,000

BROOKLYN -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Goran Brantley,6259824,0,4
Deni Duval,15776955,0,2
Micah Lindqvist,5806187,0,1
Santi Whitfield,23938393,0,4
Jalil Beauchamp,40990504,0,1
Santi Ibarra,2605959,0,2
Isaiah Marsh,44091388,0,1
Micah Amadi,5207505,0,4
Jaylen Sabonis,2307584,0,4
Malik Okoro,6392131,0,3
Nikola Amadi,3644728,0,2
Bogdan Nakamura,22278274,0,1
Jalil Cordero,3201664,0,4
Kobe Jokubaitis,5154014,0,1
Kristaps Lindqvist,3047881,0,2

Roster count: 15

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 190702991, "tax_line": 187895000, "amount_over": 2807991, "is_repeater": false, "total": 2807991, "brackets": [{"index": 1, "amount": 2807991, "rate": 1.0, "owed": 2807991}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $2,807,991, $2,807,991

**Computation trace (the only figures you may use):**

```
  1. Brooklyn tax salary = $190,702,991
  2. 2025-26 luxury tax line = $187,895,000
  3. Amount over the tax line = $2,807,991 ($190,702,991 - $187,895,000)
  4. Rate schedule: standard (2025-26) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $2,807,991 at $1.00 per dollar = $2,807,991
  6. Total luxury tax owed = $2,807,991
  7. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 17 -- apron_status

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

TORONTO -- 2024-25 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Darnell Osei | $5,462,883 | -- | 1 |
| Dante Jokubaitis | $2,543,291 | -- | 3 |
| Bogdan Boateng | $7,530,631 | $566,666 | 2 |
| Andre Duval | $49,205,800 | -- | 2 |
| Tobias Novak | $3,097,230 | -- | 2 |
| Kellen Boateng | $9,006,395 | -- | 1 |
| Luka Osei | $6,145,469 | -- | 2 |
| Corey Novak | $32,169,811 | -- | 4 |
| Deni Dumont | $5,638,421 | $566,668 | 1 |
| Julian Ellington | $10,352,874 | -- | 3 |
| Andre Okoro | $7,077,234 | -- | 2 |
| Marcus Brantley | $4,076,044 | -- | 2 |
| Amari Lindqvist | $7,617,131 | $566,666 | 3 |
| Brennan Stavros | $16,651,178 | -- | 2 |

Roster count: 14

Are we over the second apron? How much room do we have?
```

**Ground truth:** {"tax_salary": 166574392, "unlikely_incentives": 1700000, "apron_salary": 168274392, "apron_level": "under the tax line", "room_to_first_apron": 9857608, "room_to_second_apron": 20656608}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $168,274,392

**Computation trace (the only figures you may use):**

```
  1. Toronto salaries plus likely incentives = $166,574,392
  2. Unlikely incentives = $1,700,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $168,274,392
  4. 2024-25 luxury tax line = $170,814,000
  5. 2024-25 first apron = $178,132,000
  6. 2024-25 second apron = $188,931,000
  7. Position: under the tax line
  8. Room below the tax line = $2,539,608
  9. Room below the first apron = $9,857,608
  10. Room below the second apron = $20,656,608
```


## Scenario 18 -- tax_bill

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

BROOKLYN -- 2026-27 CAP SHEET
Andre Jokubaitis        $52,511,113
Elijah Beauchamp         $3,749,794
Marcus Whitfield         $7,933,730
Kellen Nakamura          $6,349,644
Jaylen Reddish           $5,909,248
Nikola Novak            $13,921,003
Terrance Kalinic         $8,735,855
Darnell Lindqvist       $52,261,646
Zion Kalinic             $9,264,861
Deni Kearns              $9,112,235
Trey Stavros            $23,695,695
Isaiah Brantley          $8,719,062
Andre Ellington          $5,939,548
Tobias Duval            $13,030,060

Roster count: 14
Repeater taxpayer: yes

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 221133494, "tax_line": 200428000, "amount_over": 20705494, "is_repeater": true, "total": 88218084, "brackets": [{"index": 1, "amount": 6064000, "rate": 3.0, "owed": 18192000}, {"index": 2, "amount": 6064000, "rate": 3.25, "owed": 19708000}, {"index": 3, "amount": 6064000, "rate": 5.5, "owed": 33352000}, {"index": 4, "amount": 2513494, "rate": 6.75, "owed": 16966084}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $88,218,084, $20,705,494

**Computation trace (the only figures you may use):**

```
  1. Brooklyn tax salary = $221,133,494
  2. 2026-27 luxury tax line = $200,428,000
  3. Amount over the tax line = $20,705,494 ($221,133,494 - $200,428,000)
  4. Rate schedule: repeater (2026-27) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $6,064,000 at $3.00 per dollar = $18,192,000
  6. Bracket 2: $6,064,000 at $3.25 per dollar = $19,708,000
  7. Bracket 3: $6,064,000 at $5.50 per dollar = $33,352,000
  8. Bracket 4: $2,513,494 at $6.75 per dollar = $16,966,084
  9. Total luxury tax owed = $88,218,084
  10. Repeater status applies (paid the tax in 3 of the prior 4 seasons)
  11. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 19 -- anti_staleness

**What the user said:**

```
2028-29 LEAGUE THRESHOLDS
  Salary cap:          $146,941,000
  Luxury tax line:     $178,533,000
  First apron:         $186,181,000
  Second apron:        $197,468,000
  Non-taxpayer MLE:    $13,401,000
  Taxpayer MLE:        $5,402,000
  Room exception:      $8,344,000
  Tax bracket width:   $5,402,000
  Bi-annual exception: $5,226,000

WASHINGTON -- 2028-29 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Nico Reddish | $3,659,992 | -- | 4 |
| Deni Amadi | $8,960,940 | -- | 2 |
| Cam Rees | $17,311,329 | -- | 4 |
| Luka Jokubaitis | $4,303,738 | -- | 3 |
| Jaylen Halvorsen | $4,841,657 | -- | 3 |
| Devonte Sabonis | $7,078,584 | -- | 1 |
| Micah Lindqvist | $39,811,866 | -- | 2 |
| Malik Cordero | $3,619,676 | -- | 4 |
| Brennan Beauchamp | $19,145,846 | -- | 3 |
| Kobe Reddish | $5,129,640 | -- | 3 |
| Amari Ferreira | $2,182,000 | -- | 3 |
| Terrance Nakamura | $5,812,483 | -- | 3 |
| Terrance Rees | $4,113,167 | -- | 4 |
| Zion Brantley | $13,802,679 | -- | 4 |
| Zion Sabonis | $44,078,912 | -- | 2 |

Roster count: 15

Using the 2028-29 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2028-29", "apron_salary": 183852509, "apron_level": "over the tax line", "first_apron_provided": 186181000, "second_apron_provided": 197468000, "would_be_wrong_using_published_figures": "over the first apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $183,852,509, $197,468,000

**Computation trace (the only figures you may use):**

```
  1. Washington apron salary = $183,852,509
  2. 2028-29 first apron (from the figures provided) = $186,181,000
  3. 2028-29 second apron (from the figures provided) = $197,468,000
  4. Position: over the tax line
  5. Room below the second apron = $13,615,491
```


## Scenario 20 -- apron_status

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

ORLANDO -- 2024-25 CAP SHEET
Cam Kearns              $24,910,592
Julian Whitfield         $5,147,857
Devonte Ellington        $4,062,167
Nikola Ibarra            $2,088,000   (+$666,666 unlikely)
Julian Novak            $39,763,452
Micah Dumont             $7,309,426
Bogdan Ellington        $34,559,767
Luka Boateng             $2,523,489
Jaylen Dumont            $2,088,000
Isaiah Jokubaitis        $5,739,922   (+$666,666 unlikely)
Brennan Dumont          $22,381,872
Darnell Amadi            $7,364,857
Micah Halvorsen          $6,313,736
Isaiah Dumont           $16,876,223   (+$666,668 unlikely)

Roster count: 14

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 181129360, "unlikely_incentives": 2000000, "apron_salary": 183129360, "apron_level": "over the first apron", "room_to_first_apron": -4997360, "room_to_second_apron": 5801640}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $183,129,360

**Computation trace (the only figures you may use):**

```
  1. Orlando salaries plus likely incentives = $181,129,360
  2. Unlikely incentives = $2,000,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $183,129,360
  4. 2024-25 luxury tax line = $170,814,000
  5. 2024-25 first apron = $178,132,000
  6. 2024-25 second apron = $188,931,000
  7. Position: over the first apron
  8. Amount above the tax line = $12,315,360
  9. Amount above the first apron = $4,997,360
  10. Room below the second apron = $5,801,640
```


## Scenario 21 -- exception_eligibility

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

PORTLAND -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Micah Novak | $3,440,735 | -- | 1 |
| Cam Ferreira | $6,910,539 | -- | 1 |
| Rashad Osei | $5,127,661 | -- | 1 |
| Corey Osei | $3,996,802 | -- | 3 |
| Alperen Rees | $30,708,989 | -- | 3 |
| Amari Reddish | $8,694,315 | -- | 1 |
| Tobias Vasquez | $9,825,075 | -- | 2 |
| Terrance Cordero | $8,584,806 | -- | 3 |
| Alperen Sabonis | $4,563,226 | -- | 2 |
| Micah Halvorsen | $57,736,350 | -- | 4 |
| Brennan Cordero | $9,479,509 | -- | 3 |
| Darnell Boateng | $25,685,364 | -- | 2 |
| Luka Brantley | $9,018,317 | -- | 3 |
| Corey Duval | $6,412,382 | -- | 1 |
| Rashad Stavros | $25,644,068 | -- | 2 |

Roster count: 15

Can we sign Rashad Cordero for $6,843,180 using the bi-annual exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "bi-annual exception", "salary": 6843180, "hard_cap_triggered": "none", "apron_level": "over the first apron", "apron_salary_after": 222671318, "reasons": ["bi-annual exception is unavailable over the first apron", "Portland already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $6,843,180

**Computation trace (the only figures you may use):**

```
  1. Portland apron salary before signing = $215,828,138 (over the first apron)
  2. Proposed salary for Rashad Cordero = $6,843,180
  3. Exception: bi-annual exception
  4. VIOLATION -- bi-annual exception unavailable (unavailable over the first apron)
  5. Portland apron salary after signing = $222,671,318
  6. VIOLATION -- roster is full (15-man limit reached)
  7. Verdict: ILLEGAL
```


## Scenario 22 -- exception_survey

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

SACRAMENTO -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Darnell Whitfield | $6,877,357 | -- | 2 |
| Corey Petrov | $7,638,222 | -- | 4 |
| Jalil Rees | $38,083,715 | -- | 3 |
| Amari Petrov | $8,446,493 | -- | 3 |
| Nico Brantley | $6,142,971 | -- | 4 |
| Santi Ferreira | $32,736,213 | -- | 3 |
| Micah Duval | $12,993,328 | -- | 1 |
| Trey Vasquez | $12,647,141 | -- | 1 |
| Micah Dumont | $57,736,350 | -- | 3 |
| Amari Osei | $10,146,554 | -- | 4 |
| Kobe Novak | $8,587,165 | -- | 1 |
| Trey Lindqvist | $7,651,623 | -- | 2 |
| Kristaps Whitfield | $9,691,049 | -- | 2 |
| Zion Beauchamp | $9,081,070 | -- | 1 |
| Darnell Beauchamp | $12,336,562 | -- | 1 |

Roster count: 15

Run me through our tools in free agency this summer.
```

**Ground truth:** {"apron_level": "over the second apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the second apron -- no mid-level of any kind", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Sacramento apron salary = $240,795,813 (over the second apron)
  2. 2026-27 first apron = $209,015,000
  3. 2026-27 second apron = $221,686,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: unavailable (unavailable over the second apron -- no mid-level of any kind)
  6. bi-annual exception: unavailable (unavailable over the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 23 -- tax_bill

**What the user said:**

```
2025-26 LEAGUE THRESHOLDS
  Salary cap:          $154,647,000
  Luxury tax line:     $187,895,000
  First apron:         $195,945,000
  Second apron:        $207,824,000
  Non-taxpayer MLE:    $14,104,000
  Taxpayer MLE:        $5,685,000
  Room exception:      $8,781,000
  Tax bracket width:   $5,685,000

ATLANTA -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Kellen Ferreira,11287321,0,3
Elijah Whitfield,10979576,0,3
Alperen Cordero,27166282,0,3
Zion Duval,8356296,0,3
Terrance Dumont,54126450,0,4
Marcus Dumont,6512629,0,1
Rashad Ibarra,6616759,0,3
Jalil Ferreira,7226154,0,3
Corey Okoro,19497321,0,2
Terrance Ellington,4443746,0,3
Tobias Reddish,10405939,0,4
Kristaps Sabonis,10408975,0,1
Julian Halvorsen,4785280,0,3
Kristaps Jokubaitis,4385653,0,3
Kristaps Vasquez,4596473,0,4

Roster count: 15

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 190794854, "tax_line": 187895000, "amount_over": 2899854, "is_repeater": false, "total": 2899854, "brackets": [{"index": 1, "amount": 2899854, "rate": 1.0, "owed": 2899854}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $2,899,854, $2,899,854

**Computation trace (the only figures you may use):**

```
  1. Atlanta tax salary = $190,794,854
  2. 2025-26 luxury tax line = $187,895,000
  3. Amount over the tax line = $2,899,854 ($190,794,854 - $187,895,000)
  4. Rate schedule: standard (2025-26) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $2,899,854 at $1.00 per dollar = $2,899,854
  6. Total luxury tax owed = $2,899,854
  7. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 24 -- scenario_planning

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

INDIANA -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Jalil Rees | $10,722,079 | -- | 3 |
| Nikola Okoro | $43,471,268 | -- | 4 |
| Darnell Dumont | $13,706,917 | -- | 3 |
| Bogdan Lindqvist | $57,736,350 | -- | 1 |
| Trey Lindqvist | $8,807,671 | -- | 2 |
| Deni Brantley | $9,148,807 | -- | 4 |
| Deni Kalinic | $8,890,831 | -- | 3 |
| Goran Sabonis | $11,424,314 | -- | 2 |
| Kobe Sabonis | $13,474,528 | -- | 4 |
| Deni Achiuwa | $5,377,658 | -- | 1 |
| Isaiah Whitfield | $7,012,520 | -- | 2 |
| Elijah Achiuwa | $15,607,489 | -- | 3 |
| Deni Jokubaitis | $12,665,627 | -- | 1 |
| Darnell Okoro | $7,104,324 | -- | 4 |
| Kellen Achiuwa | $5,674,175 | -- | 4 |

Roster count: 15

What's the cleanest path under the second apron from here?
```

**Ground truth:** {"apron_salary": 230824558, "second_apron": 221686000, "overage": 9138558, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Deni Brantley", "salary": 9148807, "surplus": 10249}, {"player": "Jalil Rees", "salary": 10722079, "surplus": 1583521}, {"player": "Goran Sabonis", "salary": 11424314, "surplus": 2285756}, {"player": "Deni Jokubaitis", "salary": 12665627, "surplus": 3527069}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $9,138,558

**Computation trace (the only figures you may use):**

```
  1. Indiana apron salary = $230,824,558
  2. 2026-27 second apron = $221,686,000
  3. Amount over the second apron = $9,138,558
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Deni Brantley alone clears the gap = $10,249 ($9,148,807 out against $9,138,558 of overage, assuming no salary comes back)
  7. Moving Jalil Rees alone clears the gap = $1,583,521 ($10,722,079 out against $9,138,558 of overage, assuming no salary comes back)
  8. Moving Goran Sabonis alone clears the gap = $2,285,756 ($11,424,314 out against $9,138,558 of overage, assuming no salary comes back)
  9. Moving Deni Jokubaitis alone clears the gap = $3,527,069 ($12,665,627 out against $9,138,558 of overage, assuming no salary comes back)
```


## Scenario 25 -- apron_status

**What the user said:**

```
2025-26 LEAGUE THRESHOLDS
  Salary cap:          $154,647,000
  Luxury tax line:     $187,895,000
  First apron:         $195,945,000
  Second apron:        $207,824,000
  Non-taxpayer MLE:    $14,104,000
  Taxpayer MLE:        $5,685,000
  Room exception:      $8,781,000
  Tax bracket width:   $5,685,000

WASHINGTON -- 2025-26 CAP SHEET
Nikola Duval           $20,233,932   (+$1,200,000 unlikely)
Trey Duval             $17,288,886
Darnell Duval           $2,913,267
Marcus Kearns           $5,850,183
Devonte Marsh           $3,449,467
Jalil Kearns            $4,842,085
Deni Rees               $5,360,232
Jaylen Duval            $3,234,869
Corey Nakamura          $2,353,355   (+$1,200,000 unlikely)
Darnell Brantley       $15,054,682
Rashad Cordero         $37,634,088   (+$1,200,000 unlikely)
Luka Dumont             $2,296,001
Cam Achiuwa             $4,424,690
Jalil Novak             $6,316,806
Alperen Rees            $4,987,731

Roster count: 15

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 136240274, "unlikely_incentives": 3600000, "apron_salary": 139840274, "apron_level": "under the tax line", "room_to_first_apron": 56104726, "room_to_second_apron": 67983726}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $139,840,274

**Computation trace (the only figures you may use):**

```
  1. Washington salaries plus likely incentives = $136,240,274
  2. Unlikely incentives = $3,600,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $139,840,274
  4. 2025-26 luxury tax line = $187,895,000
  5. 2025-26 first apron = $195,945,000
  6. 2025-26 second apron = $207,824,000
  7. Position: under the tax line
  8. Room below the tax line = $48,054,726
  9. Room below the first apron = $56,104,726
  10. Room below the second apron = $67,983,726
```


## Scenario 26 -- stretch_provision

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

If we waive and stretch Darnell Vasquez -- $23,300,000 left over 2 years -- what does the dead money look like, and is it even allowed?
```

**Ground truth:** {"legal": true, "remaining_salary": 23300000, "years_remaining": 2, "stretch_years": 5, "annual_dead_money": 4660000, "existing_stretched": 6700000, "limit": 24744150, "givebacks_required": 0, "reason": "the stretch is legal: $11,360,000 of total dead money sits below the $24,744,150 ceiling"}

**Verdict:** LEGAL

**Required figures (must all appear):** $4,660,000, $24,744,150

**Computation trace (the only figures you may use):**

```
  1. Salary remaining on the contract = $23,300,000
  2. Years remaining (2)
  3. Stretch period (2 x 2 + 1 = 5 seasons)
  4. Annual dead money if stretched = $4,660,000 ($23,300,000 / 5)
  5. Dead money already stretched = $6,700,000
  6. Total stretched dead money = $11,360,000
  7. Limit (15% of the 2026-27 cap) = $24,744,150 (15% x $164,961,000)
  8. Legal = $13,384,150 (room to spare)
```


## Scenario 27 -- anti_staleness

**What the user said:**

```
2027-28 LEAGUE THRESHOLDS
  Salary cap:          $148,423,000
  Luxury tax line:     $180,334,000
  First apron:         $188,060,000
  Second apron:        $199,461,000
  Non-taxpayer MLE:    $13,537,000
  Taxpayer MLE:        $5,456,000
  Room exception:      $8,428,000
  Tax bracket width:   $5,456,000
  Bi-annual exception: $5,279,000

TORONTO -- 2027-28 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Trey Brantley,7812641,0,1
Brennan Jokubaitis,9174197,0,3
Zion Reddish,7634036,0,4
Isaiah Boateng,10927347,0,1
Devonte Ibarra,9179612,0,2
Jalil Okoro,51948050,0,2
Jalil Boateng,20189336,0,1
Marcus Petrov,9540787,0,3
Cam Dumont,8018164,0,3
Jaylen Lindqvist,6645597,0,3
Goran Dumont,24641794,0,2
Luka Lindqvist,9043203,0,1
Marcus Lindqvist,10899655,0,2
Elijah Halvorsen,10845247,0,3

Roster count: 14

Using the 2027-28 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2027-28", "apron_salary": 196499666, "apron_level": "over the first apron", "first_apron_provided": 188060000, "second_apron_provided": 199461000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $196,499,666, $199,461,000

**Computation trace (the only figures you may use):**

```
  1. Toronto apron salary = $196,499,666
  2. 2027-28 first apron (from the figures provided) = $188,060,000
  3. 2027-28 second apron (from the figures provided) = $199,461,000
  4. Position: over the first apron
  5. Room below the second apron = $2,961,334
```


## Scenario 28 -- scenario_planning

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

ATLANTA -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Jaylen Kalinic | $11,995,954 | -- | 1 |
| Elijah Amadi | $8,649,773 | -- | 1 |
| Jaylen Halvorsen | $9,403,649 | -- | 2 |
| Dante Petrov | $7,794,314 | -- | 4 |
| Brennan Okoro | $6,725,483 | -- | 4 |
| Trey Petrov | $6,491,593 | -- | 3 |
| Dante Stavros | $57,736,350 | -- | 4 |
| Kellen Dumont | $7,884,303 | -- | 1 |
| Andre Duval | $23,480,388 | -- | 4 |
| Nico Stavros | $57,736,350 | -- | 2 |
| Jalil Rees | $10,322,855 | -- | 4 |
| Kobe Osei | $11,684,086 | -- | 1 |
| Santi Cordero | $16,836,930 | -- | 3 |
| Brennan Petrov | $5,170,424 | -- | 1 |
| Luka Novak | $4,298,986 | -- | 3 |

Roster count: 15

Ownership wants us out of the second apron. Walk me through how we do it.
```

**Ground truth:** {"apron_salary": 246211438, "second_apron": 221686000, "overage": 24525438, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Dante Stavros", "salary": 57736350, "surplus": 33210912}, {"player": "Nico Stavros", "salary": 57736350, "surplus": 33210912}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $24,525,438

**Computation trace (the only figures you may use):**

```
  1. Atlanta apron salary = $246,211,438
  2. 2026-27 second apron = $221,686,000
  3. Amount over the second apron = $24,525,438
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Dante Stavros alone clears the gap = $33,210,912 ($57,736,350 out against $24,525,438 of overage, assuming no salary comes back)
  7. Moving Nico Stavros alone clears the gap = $33,210,912 ($57,736,350 out against $24,525,438 of overage, assuming no salary comes back)
```


## Scenario 29 -- draft_penalty

**What the user said:**

```
2025-26 LEAGUE THRESHOLDS
  Salary cap:          $154,647,000
  Luxury tax line:     $187,895,000
  First apron:         $195,945,000
  Second apron:        $207,824,000
  Non-taxpayer MLE:    $14,104,000
  Taxpayer MLE:        $5,685,000
  Room exception:      $8,781,000
  Tax bracket width:   $5,685,000

HOUSTON -- 2025-26 CAP SHEET
Kobe Stavros              $6,949,073
Corey Ibarra             $12,831,831
Cam Novak                $10,463,095
Terrance Achiuwa         $13,923,092
Jalil Boateng             $6,620,942
Devonte Jokubaitis       $54,126,450
Terrance Novak            $5,598,009
Nico Novak               $12,601,674
Isaiah Beauchamp          $6,234,348
Luka Jokubaitis          $39,059,022
Goran Jokubaitis          $8,451,288
Julian Petrov             $5,940,960
Santi Brantley           $24,058,278
Tobias Brantley          $12,186,857

Roster count: 14

If we finish the season at this payroll, what happens to our draft picks?
```

**Ground truth:** {"pick_frozen": true, "frozen_draft_year": 2032, "pick_demoted": false, "seasons_over": 0, "reason": "Houston finishes over the second apron, freezing its 2032 first-round pick. It unfreezes only after finishing below the second apron in 3 of the following 4 seasons"}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Houston apron salary = $219,044,919 (over the second apron)
  2. Seasons finished over the second apron (within the window) (0)
  3. First-round pick frozen (the 2032 first-rounder (7 drafts out) becomes untradeable)
  4. Pick not yet demoted (demotion requires 3 of 5 seasons over the second apron)
```


## Scenario 30 -- apron_status

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

MEMPHIS -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Dante Halvorsen,36452818,0,4
Jalil Ferreira,24976189,0,1
Goran Vasquez,19309666,0,4
Kellen Boateng,15526306,0,1
Amari Vasquez,5427674,0,2
Rashad Vasquez,19929725,0,1
Tobias Vasquez,2856528,2066666,3
Marcus Kearns,4324517,2066666,4
Dante Brantley,8431676,0,2
Nikola Whitfield,8250423,0,4
Malik Nakamura,6905703,0,2
Nikola Ellington,7007705,0,4
Kristaps Stavros,7507620,0,2
Kristaps Kearns,3214634,2066668,2
Kobe Stavros,3341380,0,1

Roster count: 15

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 173462564, "unlikely_incentives": 6200000, "apron_salary": 179662564, "apron_level": "over the first apron", "room_to_first_apron": -1530564, "room_to_second_apron": 9268436}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $179,662,564

**Computation trace (the only figures you may use):**

```
  1. Memphis salaries plus likely incentives = $173,462,564
  2. Unlikely incentives = $6,200,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $179,662,564
  4. 2024-25 luxury tax line = $170,814,000
  5. 2024-25 first apron = $178,132,000
  6. 2024-25 second apron = $188,931,000
  7. Position: over the first apron
  8. Amount above the tax line = $8,848,564
  9. Amount above the first apron = $1,530,564
  10. Room below the second apron = $9,268,436
```


## Scenario 31 -- hard_cap_consequence

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

BROOKLYN -- 2026-27 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Devonte Sabonis,13767534,0,4
Santi Rees,7280886,0,1
Darnell Jokubaitis,57736350,0,4
Julian Stavros,10041557,0,1
Amari Kearns,11878998,0,1
Bogdan Boateng,15318168,0,4
Corey Ellington,6596496,0,3
Terrance Rees,11742813,0,1
Elijah Nakamura,22803292,0,2
Santi Duval,11065031,0,2
Jaylen Halvorsen,17065139,0,3
Dante Dumont,7353942,0,3
Kobe Brantley,11531146,0,3

Roster count: 13
Hard cap: first apron

We're hard-capped at the first apron. Can we add Santi Stavros at $2,754,323?
```

**Ground truth:** {"legal": true, "hard_cap": "first apron", "hard_cap_limit": 209015000, "room_below_hard_cap": 4833648, "salary": 2754323, "apron_salary_after": 206935675, "reasons": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $2,754,323, $209,015,000

**Computation trace (the only figures you may use):**

```
  1. Brooklyn apron salary before signing = $204,181,352 (over the tax line)
  2. Proposed salary for Santi Stavros = $2,754,323
  3. Exception: minimum salary exception
  4. Brooklyn apron salary after signing = $206,935,675
  5. Hard cap: first apron = $209,015,000
  6. Room below the hard cap = $2,079,325
  7. Verdict: LEGAL
  8. Room below the first apron hard cap before signing = $4,833,648 ($209,015,000 - $204,181,352)
```


## Scenario 32 -- exception_survey

**What the user said:**

```
2025-26 LEAGUE THRESHOLDS
  Salary cap:          $154,647,000
  Luxury tax line:     $187,895,000
  First apron:         $195,945,000
  Second apron:        $207,824,000
  Non-taxpayer MLE:    $14,104,000
  Taxpayer MLE:        $5,685,000
  Room exception:      $8,781,000
  Tax bracket width:   $5,685,000

MIAMI -- 2025-26 CAP SHEET
Nico Marsh             $31,309,810
Nikola Cordero          $9,152,817
Marcus Novak           $52,829,580
Andre Ibarra            $4,321,565
Zion Amadi              $3,293,827
Julian Vasquez          $4,671,746
Nikola Kearns           $3,282,410
Kellen Okoro            $4,338,950
Cam Ibarra             $10,018,590
Malik Brantley          $5,751,253
Isaiah Boateng          $8,070,193
Andre Jokubaitis        $4,823,672
Elijah Nakamura         $3,355,853
Terrance Rees           $8,801,316
Andre Brantley         $10,447,709

Roster count: 15

Run me through our tools in free agency this summer.
```

**Ground truth:** {"apron_level": "under the tax line", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": true, "amount": 14104000, "reason": "available at $14,104,000; using it hard-caps the team at the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 5685000, "reason": "available at $5,685,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": true, "amount": null, "reason": "available, but the published amount for this season is not on file", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Miami apron salary = $164,469,291 (under the tax line)
  2. 2025-26 first apron = $195,945,000
  3. 2025-26 second apron = $207,824,000
  4. non-taxpayer mid-level exception: available = $14,104,000 (available at $14,104,000; using it hard-caps the team at the first apron)
  5. taxpayer mid-level exception: available = $5,685,000 (available at $5,685,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: available (available, but the published amount for this season is not on file)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 33 -- trade_legality

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

MIAMI -- 2024-25 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Isaiah Kearns | $3,240,839 | -- | 1 |
| Kobe Vasquez | $10,535,771 | -- | 4 |
| Jaylen Marsh | $48,694,169 | -- | 3 |
| Kellen Jokubaitis | $5,075,326 | -- | 2 |
| Corey Amadi | $31,176,160 | -- | 4 |
| Bogdan Sabonis | $8,000,269 | -- | 3 |
| Dante Novak | $7,027,038 | -- | 2 |
| Marcus Amadi | $23,285,311 | -- | 4 |
| Cam Dumont | $9,858,091 | -- | 2 |
| Kristaps Kearns | $20,061,842 | -- | 3 |
| Rashad Stavros | $7,285,065 | -- | 4 |
| Isaiah Osei | $3,058,321 | -- | 3 |
| Terrance Vasquez | $9,029,554 | -- | 3 |

Roster count: 13

We're discussing a trade that sends Jaylen Marsh to another team for Kobe Osei at $42,348,012. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 48694169, "incoming_salary": 42348012, "max_incoming": 48694169, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 179981599, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $48,694,169, $42,348,012, $48,694,169

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Miami
  2. --- Miami (2024-25) --- (apron salary $186,327,756, over the first apron)
  3. Miami outgoing salary = $48,694,169 (Jaylen Marsh $48,694,169)
  4. Miami incoming salary = $42,348,012 (Kobe Osei $42,348,012)
  5. Miami matching limit = $48,694,169 (100% of outgoing salary (team is over the first apron))
  6. Miami apron salary after the trade = $179,981,599
  7. Verdict: LEGAL
```


## Scenario 34 -- scenario_planning

**What the user said:**

```
2025-26 LEAGUE THRESHOLDS
  Salary cap:          $154,647,000
  Luxury tax line:     $187,895,000
  First apron:         $195,945,000
  Second apron:        $207,824,000
  Non-taxpayer MLE:    $14,104,000
  Taxpayer MLE:        $5,685,000
  Room exception:      $8,781,000
  Tax bracket width:   $5,685,000

DETROIT -- 2025-26 CAP SHEET
Nikola Ibarra           $8,095,775
Andre Kalinic          $28,691,617
Trey Cordero           $24,492,276
Trey Osei               $6,269,817
Julian Duval           $54,126,450
Kellen Kalinic         $11,862,787
Marcus Vasquez          $6,484,997
Elijah Ibarra           $8,882,315
Kellen Whitfield       $13,367,109
Amari Vasquez           $6,237,319
Micah Dumont           $10,159,496
Brennan Dumont         $12,403,158
Elijah Ferreira         $4,759,297
Kellen Amadi            $8,977,702
Bogdan Okoro           $14,014,148

Roster count: 15

We need to get under the second apron before the deadline. What are our options, and what are we giving up?
```

**Ground truth:** {"apron_salary": 218824263, "second_apron": 207824000, "overage": 11000263, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Kellen Kalinic", "salary": 11862787, "surplus": 862524}, {"player": "Brennan Dumont", "salary": 12403158, "surplus": 1402895}, {"player": "Kellen Whitfield", "salary": 13367109, "surplus": 2366846}, {"player": "Bogdan Okoro", "salary": 14014148, "surplus": 3013885}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $11,000,263

**Computation trace (the only figures you may use):**

```
  1. Detroit apron salary = $218,824,263
  2. 2025-26 second apron = $207,824,000
  3. Amount over the second apron = $11,000,263
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Kellen Kalinic alone clears the gap = $862,524 ($11,862,787 out against $11,000,263 of overage, assuming no salary comes back)
  7. Moving Brennan Dumont alone clears the gap = $1,402,895 ($12,403,158 out against $11,000,263 of overage, assuming no salary comes back)
  8. Moving Kellen Whitfield alone clears the gap = $2,366,846 ($13,367,109 out against $11,000,263 of overage, assuming no salary comes back)
  9. Moving Bogdan Okoro alone clears the gap = $3,013,885 ($14,014,148 out against $11,000,263 of overage, assuming no salary comes back)
```


## Scenario 35 -- apron_status

**What the user said:**

```
2025-26 LEAGUE THRESHOLDS
  Salary cap:          $154,647,000
  Luxury tax line:     $187,895,000
  First apron:         $195,945,000
  Second apron:        $207,824,000
  Non-taxpayer MLE:    $14,104,000
  Taxpayer MLE:        $5,685,000
  Room exception:      $8,781,000
  Tax bracket width:   $5,685,000

UTAH -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Rashad Ferreira,18022519,0,1
Jalil Kalinic,50062099,0,2
Kellen Rees,2960729,0,2
Marcus Ellington,4946629,0,1
Kristaps Duval,4433736,0,3
Elijah Sabonis,27917652,0,3
Brennan Stavros,34898236,0,1
Cam Petrov,3472501,0,2
Deni Stavros,10382738,0,1
Dante Marsh,6423961,0,2
Jalil Petrov,3216096,0,3
Trey Dumont,9888034,0,2
Kellen Kalinic,9328512,0,4
Marcus Jokubaitis,8430133,0,3
Jalil Achiuwa,9699794,0,2

Roster count: 15

Are we over the second apron? How much room do we have?
```

**Ground truth:** {"tax_salary": 204083369, "unlikely_incentives": 0, "apron_salary": 204083369, "apron_level": "over the first apron", "room_to_first_apron": -8138369, "room_to_second_apron": 3740631}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $204,083,369

**Computation trace (the only figures you may use):**

```
  1. Utah salaries plus likely incentives = $204,083,369
  2. Apron salary = $204,083,369
  3. 2025-26 luxury tax line = $187,895,000
  4. 2025-26 first apron = $195,945,000
  5. 2025-26 second apron = $207,824,000
  6. Position: over the first apron
  7. Amount above the tax line = $16,188,369
  8. Amount above the first apron = $8,138,369
  9. Room below the second apron = $3,740,631
```


## Scenario 36 -- stretch_provision

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

If we waive and stretch Tobias Achiuwa -- $34,100,000 left over 3 years -- what does the dead money look like, and is it even allowed?
```

**Ground truth:** {"legal": true, "remaining_salary": 34100000, "years_remaining": 3, "stretch_years": 7, "annual_dead_money": 4871429, "existing_stretched": 6200000, "limit": 21088200, "givebacks_required": 0, "reason": "the stretch is legal: $11,071,429 of total dead money sits below the $21,088,200 ceiling"}

**Verdict:** LEGAL

**Required figures (must all appear):** $4,871,429, $21,088,200

**Computation trace (the only figures you may use):**

```
  1. Salary remaining on the contract = $34,100,000
  2. Years remaining (3)
  3. Stretch period (2 x 3 + 1 = 7 seasons)
  4. Annual dead money if stretched = $4,871,429 ($34,100,000 / 7)
  5. Dead money already stretched = $6,200,000
  6. Total stretched dead money = $11,071,429
  7. Limit (15% of the 2024-25 cap) = $21,088,200 (15% x $140,588,000)
  8. Legal = $10,016,771 (room to spare)
```


## Scenario 37 -- exception_eligibility

**What the user said:**

```
2024-25 LEAGUE THRESHOLDS
  Salary cap:          $140,588,000
  Luxury tax line:     $170,814,000
  First apron:         $178,132,000
  Second apron:        $188,931,000
  Non-taxpayer MLE:    $12,822,000
  Taxpayer MLE:        $5,168,000
  Room exception:      $7,983,000
  Tax bracket width:   $5,168,000

BROOKLYN -- 2024-25 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Darnell Ferreira | $10,130,718 | -- | 3 |
| Dante Achiuwa | $4,263,201 | -- | 1 |
| Malik Duval | $3,824,039 | -- | 2 |
| Julian Halvorsen | $9,756,086 | -- | 1 |
| Goran Duval | $49,205,800 | -- | 3 |
| Alperen Okoro | $4,256,162 | -- | 4 |
| Nico Okoro | $2,920,382 | -- | 4 |
| Kristaps Vasquez | $3,296,418 | -- | 3 |
| Trey Reddish | $10,484,783 | -- | 3 |
| Santi Novak | $49,205,800 | -- | 1 |
| Nikola Okoro | $18,248,274 | -- | 3 |
| Marcus Stavros | $10,996,638 | -- | 3 |
| Jaylen Lindqvist | $8,510,301 | -- | 1 |
| Jaylen Cordero | $20,585,792 | -- | 2 |

Roster count: 14

Can we sign Deni Okoro for $6,419,559 using the taxpayer mid-level exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "taxpayer mid-level exception", "salary": 6419559, "hard_cap_triggered": "none", "apron_level": "over the second apron", "apron_salary_after": 212103953, "reasons": ["taxpayer mid-level exception is unavailable over the second apron -- no mid-level of any kind"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $6,419,559

**Computation trace (the only figures you may use):**

```
  1. Brooklyn apron salary before signing = $205,684,394 (over the second apron)
  2. Proposed salary for Deni Okoro = $6,419,559
  3. Exception: taxpayer mid-level exception
  4. VIOLATION -- taxpayer mid-level exception unavailable (unavailable over the second apron -- no mid-level of any kind)
  5. Brooklyn apron salary after signing = $212,103,953
  6. Verdict: ILLEGAL
```


## Scenario 38 -- anti_staleness

**What the user said:**

```
2029-30 LEAGUE THRESHOLDS
  Salary cap:          $180,759,000
  Luxury tax line:     $219,622,000
  First apron:         $229,031,000
  Second apron:        $242,916,000
  Non-taxpayer MLE:    $16,485,000
  Taxpayer MLE:        $6,645,000
  Room exception:      $10,263,000
  Tax bracket width:   $6,645,000
  Bi-annual exception: $6,002,000

OKLAHOMA CITY -- 2029-30 CAP SHEET
Micah Ibarra            $12,671,121
Isaiah Nakamura          $7,645,947
Alperen Reddish         $13,616,338
Alperen Lindqvist       $10,357,298
Luka Achiuwa            $15,450,417
Julian Petrov            $7,871,275
Deni Amadi               $5,258,296
Rashad Rees             $12,602,433
Jalil Ibarra            $23,826,083
Trey Jokubaitis          $5,717,442
Goran Reddish            $6,341,664
Alperen Halvorsen       $63,265,649
Alperen Rees             $7,387,208
Marcus Reddish           $9,019,782
Elijah Lindqvist        $26,211,935

Roster count: 15

Using the 2029-30 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2029-30", "apron_salary": 227242888, "apron_level": "over the tax line", "first_apron_provided": 229031000, "second_apron_provided": 242916000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $227,242,888, $242,916,000

**Computation trace (the only figures you may use):**

```
  1. Oklahoma City apron salary = $227,242,888
  2. 2029-30 first apron (from the figures provided) = $229,031,000
  3. 2029-30 second apron (from the figures provided) = $242,916,000
  4. Position: over the tax line
  5. Room below the second apron = $15,673,112
```


## Scenario 39 -- exception_eligibility

**What the user said:**

```
2026-27 LEAGUE THRESHOLDS
  Salary cap:          $164,961,000
  Luxury tax line:     $200,428,000
  First apron:         $209,015,000
  Second apron:        $221,686,000
  Non-taxpayer MLE:    $15,044,000
  Taxpayer MLE:        $6,064,000
  Room exception:      $9,366,000
  Tax bracket width:   $6,064,000
  Bi-annual exception: $5,477,000

BROOKLYN -- 2026-27 CAP SHEET
Trey Petrov               $3,787,092
Jalil Rees               $27,088,843
Brennan Osei              $5,682,542
Darnell Osei              $3,359,245
Deni Novak               $33,948,846
Jaylen Vasquez            $6,854,207
Brennan Ibarra            $9,024,219
Alperen Vasquez          $23,052,034
Bogdan Kearns             $7,435,102
Kristaps Novak            $5,762,076
Goran Ferreira           $13,504,593
Brennan Jokubaitis        $8,228,386
Brennan Nakamura         $57,736,350

Roster count: 13

Can we sign Isaiah Ibarra for $4,807,219 using the taxpayer mid-level exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": true, "exception": "taxpayer mid-level exception", "salary": 4807219, "hard_cap_triggered": "second apron", "apron_level": "over the tax line", "apron_salary_after": 210270754, "reasons": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $4,807,219

**Computation trace (the only figures you may use):**

```
  1. Brooklyn apron salary before signing = $205,463,535 (over the tax line)
  2. Proposed salary for Isaiah Ibarra = $4,807,219
  3. Exception: taxpayer mid-level exception
  4. taxpayer mid-level exception maximum = $6,064,000
  5. Room remaining within the exception = $1,256,781
  6. Brooklyn apron salary after signing = $210,270,754
  7. Hard cap: second apron = $221,686,000
  8. Room below the hard cap = $11,415,246
  9. Verdict: LEGAL
```


