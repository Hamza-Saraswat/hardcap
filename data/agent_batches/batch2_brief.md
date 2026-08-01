# Writing batch 2

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

Write one JSON object per line to `/tmp/rexport/batch2_responses.jsonl`, nothing else in the file:

    {"id": 0, "response": "**Verdict: ILLEGAL.** ..."}

The `id` must match the scenario number below.

---

## Scenario 0 -- exception_eligibility

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
player,salary,unlikely_incentives,years_remaining
Alperen Boateng,9417761,0,3
Kristaps Whitfield,43031355,0,4
Goran Brantley,38481929,0,2
Amari Boateng,7598812,0,4
Goran Cordero,4324462,0,1
Kobe Ibarra,7318530,0,3
Amari Ibarra,5055088,0,4
Tobias Ferreira,2753804,0,3
Andre Brantley,4816565,0,1
Isaiah Sabonis,4740701,0,1
Zion Kalinic,6991308,0,2
Trey Nakamura,3263585,0,1
Elijah Novak,5701256,0,4
Jaylen Boateng,14374642,0,2
Dante Lindqvist,4781044,0,2

Roster count: 15

Can we sign Malik Cordero for $2,500,901 using the minimum salary exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "minimum salary exception", "salary": 2500901, "hard_cap_triggered": "none", "apron_level": "under the tax line", "apron_salary_after": 165151743, "reasons": ["Orlando already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $2,500,901

**Computation trace (the only figures you may use):**

```
  1. Orlando apron salary before signing = $162,650,842 (under the tax line)
  2. Proposed salary for Malik Cordero = $2,500,901
  3. Exception: minimum salary exception
  4. Orlando apron salary after signing = $165,151,743
  5. VIOLATION -- roster is full (15-man limit reached)
  6. Verdict: ILLEGAL
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

CHICAGO -- 2024-25 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Kellen Marsh | $16,883,877 | -- | 2 |
| Goran Beauchamp | $3,164,585 | -- | 2 |
| Goran Halvorsen | $5,389,880 | -- | 1 |
| Malik Cordero | $8,222,103 | -- | 4 |
| Goran Osei | $41,546,553 | -- | 1 |
| Tobias Ellington | $5,041,492 | -- | 2 |
| Luka Ellington | $8,112,270 | -- | 4 |
| Tobias Kalinic | $8,298,651 | -- | 2 |
| Alperen Brantley | $5,861,442 | -- | 4 |
| Kristaps Whitfield | $3,506,099 | -- | 3 |
| Jalil Amadi | $5,282,159 | -- | 1 |
| Isaiah Petrov | $25,029,424 | -- | 4 |
| Kobe Cordero | $5,432,800 | -- | 2 |
| Isaiah Nakamura | $8,842,927 | -- | 3 |
| Trey Marsh | $2,855,260 | -- | 1 |

Roster count: 15

We're discussing a trade that sends Goran Beauchamp and Isaiah Petrov to another team for Brennan Nakamura at $33,030,628. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 28194009, "incoming_salary": 33030628, "max_incoming": 35946009, "matching_rule": "outgoing + $7,752,000 (middle band)", "apron_level": "under the tax line", "apron_salary_after": 158306141, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $28,194,009, $33,030,628, $35,946,009

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Chicago
  2. --- Chicago (2024-25) --- (apron salary $153,469,522, under the tax line)
  3. Chicago outgoing salary = $28,194,009 (Goran Beauchamp $3,164,585, Isaiah Petrov $25,029,424)
  4. Chicago incoming salary = $33,030,628 (Brennan Nakamura $33,030,628)
  5. Chicago matching limit = $35,946,009 (outgoing + $7,752,000 (middle band))
  6. Chicago hard-capped at the first apron = $178,132,000 (took back more than 100% of outgoing salary)
  7. Chicago hard-capped at the second apron = $188,931,000 (aggregated two or more salaries in one trade)
  8. Two hard caps triggered -- the tighter one governs = $178,132,000
  9. Chicago apron salary after the trade = $158,306,141
  10. Chicago stays under its first apron hard cap = $19,825,859 ($178,132,000 - $158,306,141 of room to spare)
  11. Verdict: LEGAL
```


## Scenario 2 -- exception_survey

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
Corey Stavros          $6,526,154
Elijah Duval           $9,054,679
Jalil Ferreira         $4,506,773
Trey Amadi             $5,772,073
Marcus Kalinic        $11,865,216
Rashad Ibarra         $16,892,420
Alperen Kearns        $49,205,800
Tobias Vasquez         $9,924,075
Kellen Ferreira       $28,758,168
Andre Lindqvist        $3,484,992
Kellen Nakamura        $9,414,550
Isaiah Nakamura        $8,534,200
Rashad Sabonis         $5,744,841
Corey Nakamura        $11,520,924

Roster count: 14

Run me through our tools in free agency this summer.
```

**Ground truth:** {"apron_level": "over the first apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 5168000, "reason": "available at $5,168,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Orlando apron salary = $181,204,865 (over the first apron)
  2. 2024-25 first apron = $178,132,000
  3. 2024-25 second apron = $188,931,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: available = $5,168,000 (available at $5,168,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: unavailable (unavailable over the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 3 -- tax_bill

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
player,salary,unlikely_incentives,years_remaining
Isaiah Brantley,10170016,0,1
Zion Kalinic,11795903,0,2
Micah Halvorsen,12557166,0,1
Rashad Jokubaitis,26880459,0,4
Jaylen Osei,5163640,0,1
Terrance Nakamura,54126450,0,1
Julian Dumont,10776581,0,3
Micah Ferreira,7267113,0,4
Trey Sabonis,10704546,0,3
Cam Brantley,19560348,0,1
Cam Okoro,10570050,0,3
Amari Osei,8357679,0,3
Dante Whitfield,9583206,0,2

Roster count: 13
Repeater taxpayer: yes

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 197513157, "tax_line": 187895000, "amount_over": 9618157, "is_repeater": true, "total": 29837760, "brackets": [{"index": 1, "amount": 5685000, "rate": 3.0, "owed": 17055000}, {"index": 2, "amount": 3933157, "rate": 3.25, "owed": 12782760}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $29,837,760, $9,618,157

**Computation trace (the only figures you may use):**

```
  1. Houston tax salary = $197,513,157
  2. 2025-26 luxury tax line = $187,895,000
  3. Amount over the tax line = $9,618,157 ($197,513,157 - $187,895,000)
  4. Rate schedule: repeater (2025-26) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $5,685,000 at $3.00 per dollar = $17,055,000
  6. Bracket 2: $3,933,157 at $3.25 per dollar = $12,782,760
  7. Total luxury tax owed = $29,837,760
  8. Repeater status applies (paid the tax in 3 of the prior 4 seasons)
  9. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 4 -- anti_staleness

**What the user said:**

```
2029-30 LEAGUE THRESHOLDS
  Salary cap:          $153,816,000
  Luxury tax line:     $186,886,000
  First apron:         $194,892,000
  Second apron:        $206,707,000
  Non-taxpayer MLE:    $14,028,000
  Taxpayer MLE:        $5,654,000
  Room exception:      $8,734,000
  Tax bracket width:   $5,654,000
  Bi-annual exception: $5,470,000

UTAH -- 2029-30 CAP SHEET
Marcus Brantley          $5,959,656
Dante Reddish           $27,153,100
Corey Achiuwa            $5,677,748
Isaiah Kalinic           $8,123,319
Tobias Dumont            $7,425,534
Goran Dumont             $8,850,567
Devonte Marsh            $4,624,289
Goran Lindqvist          $7,047,177
Andre Novak              $8,516,685
Kobe Nakamura            $8,382,021
Cam Kalinic             $11,833,939
Nico Dumont             $50,687,066
Marcus Vasquez           $8,084,468
Tobias Osei              $4,317,365
Devonte Lindqvist       $23,316,037

Roster count: 15

Using the 2029-30 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2029-30", "apron_salary": 189998971, "apron_level": "over the tax line", "first_apron_provided": 194892000, "second_apron_provided": 206707000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $189,998,971, $206,707,000

**Computation trace (the only figures you may use):**

```
  1. Utah apron salary = $189,998,971
  2. 2029-30 first apron (from the figures provided) = $194,892,000
  3. 2029-30 second apron (from the figures provided) = $206,707,000
  4. Position: over the tax line
  5. Room below the second apron = $16,708,029
```


## Scenario 5 -- apron_status

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
player,salary,unlikely_incentives,years_remaining
Brennan Duval,6533219,0,1
Jalil Ferreira,3772119,0,4
Bogdan Ellington,6314454,0,4
Alperen Amadi,39189962,0,1
Devonte Sabonis,49205800,0,4
Andre Stavros,8984031,0,3
Cam Petrov,11111707,0,1
Zion Stavros,5342293,0,1
Deni Lindqvist,5234310,0,2
Santi Reddish,12594694,0,1
Darnell Dumont,13294798,0,2
Jaylen Ellington,4225234,0,4
Malik Kearns,5655624,0,1

Roster count: 13

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 171458245, "unlikely_incentives": 0, "apron_salary": 171458245, "apron_level": "over the tax line", "room_to_first_apron": 6673755, "room_to_second_apron": 17472755}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $171,458,245

**Computation trace (the only figures you may use):**

```
  1. Brooklyn salaries plus likely incentives = $171,458,245
  2. Apron salary = $171,458,245
  3. 2024-25 luxury tax line = $170,814,000
  4. 2024-25 first apron = $178,132,000
  5. 2024-25 second apron = $188,931,000
  6. Position: over the tax line
  7. Amount above the tax line = $644,245
  8. Room below the first apron = $6,673,755
  9. Room below the second apron = $17,472,755
```


## Scenario 6 -- apron_status

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

DETROIT -- 2026-27 CAP SHEET
Trey Rees              $11,095,634
Luka Dumont             $5,149,741   (+$1,566,666 unlikely)
Julian Stavros         $10,131,754
Micah Novak            $10,170,474
Micah Halvorsen        $10,749,681
Andre Osei              $5,954,376
Rashad Achiuwa         $29,681,209
Alperen Sabonis         $8,638,112
Amari Duval            $12,824,749
Amari Rees             $57,736,350
Trey Kearns            $38,922,426   (+$1,566,666 unlikely)
Alperen Boateng         $7,139,725   (+$1,566,668 unlikely)
Rashad Ellington        $5,185,864

Roster count: 13

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 213380095, "unlikely_incentives": 4700000, "apron_salary": 218080095, "apron_level": "over the first apron", "room_to_first_apron": -9065095, "room_to_second_apron": 3605905}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $218,080,095

**Computation trace (the only figures you may use):**

```
  1. Detroit salaries plus likely incentives = $213,380,095
  2. Unlikely incentives = $4,700,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $218,080,095
  4. 2026-27 luxury tax line = $200,428,000
  5. 2026-27 first apron = $209,015,000
  6. 2026-27 second apron = $221,686,000
  7. Position: over the first apron
  8. Amount above the tax line = $17,652,095
  9. Amount above the first apron = $9,065,095
  10. Room below the second apron = $3,605,905
```


## Scenario 7 -- apron_status

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Corey Achiuwa | $15,379,075 | -- | 1 |
| Luka Vasquez | $10,498,839 | -- | 2 |
| Jaylen Beauchamp | $3,556,277 | -- | 2 |
| Micah Sabonis | $2,296,000 | -- | 3 |
| Bogdan Okoro | $36,167,767 | -- | 2 |
| Micah Ibarra | $31,400,877 | -- | 4 |
| Bogdan Sabonis | $4,859,574 | -- | 4 |
| Goran Ibarra | $10,100,869 | -- | 1 |
| Dante Stavros | $5,299,027 | -- | 2 |
| Santi Duval | $5,894,176 | -- | 2 |
| Bogdan Novak | $4,914,557 | -- | 4 |
| Malik Vasquez | $2,592,593 | -- | 1 |
| Kellen Nakamura | $15,727,735 | -- | 4 |

Roster count: 13

Are we over the second apron? How much room do we have?
```

**Ground truth:** {"tax_salary": 148687366, "unlikely_incentives": 0, "apron_salary": 148687366, "apron_level": "under the tax line", "room_to_first_apron": 47257634, "room_to_second_apron": 59136634}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $148,687,366

**Computation trace (the only figures you may use):**

```
  1. Brooklyn salaries plus likely incentives = $148,687,366
  2. Apron salary = $148,687,366
  3. 2025-26 luxury tax line = $187,895,000
  4. 2025-26 first apron = $195,945,000
  5. 2025-26 second apron = $207,824,000
  6. Position: under the tax line
  7. Room below the tax line = $39,207,634
  8. Room below the first apron = $47,257,634
  9. Room below the second apron = $59,136,634
```


## Scenario 8 -- stretch_provision

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

If we waive and stretch Zion Reddish -- $42,700,000 left over 3 years -- what does the dead money look like, and is it even allowed?
```

**Ground truth:** {"legal": true, "remaining_salary": 42700000, "years_remaining": 3, "stretch_years": 7, "annual_dead_money": 6100000, "existing_stretched": 0, "limit": 21088200, "givebacks_required": 0, "reason": "the stretch is legal: $6,100,000 of total dead money sits below the $21,088,200 ceiling"}

**Verdict:** LEGAL

**Required figures (must all appear):** $6,100,000, $21,088,200

**Computation trace (the only figures you may use):**

```
  1. Salary remaining on the contract = $42,700,000
  2. Years remaining (3)
  3. Stretch period (2 x 3 + 1 = 7 seasons)
  4. Annual dead money if stretched = $6,100,000 ($42,700,000 / 7)
  5. Dead money already stretched = $0
  6. Total stretched dead money = $6,100,000
  7. Limit (15% of the 2024-25 cap) = $21,088,200 (15% x $140,588,000)
  8. Legal = $14,988,200 (room to spare)
```


## Scenario 9 -- hard_cap_consequence

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

HOUSTON -- 2024-25 CAP SHEET
Micah Achiuwa             $3,069,214
Nikola Reddish           $24,642,984
Darnell Jokubaitis        $5,656,944
Terrance Kearns          $33,433,635
Malik Kearns              $5,285,917
Julian Dumont             $2,553,030
Devonte Sabonis           $4,399,824
Elijah Ferreira          $23,790,464
Zion Osei                 $4,593,632
Kobe Marsh                $7,427,256
Micah Boateng            $10,955,741
Cam Lindqvist             $4,831,203
Zion Reddish              $6,096,952
Alperen Jokubaitis       $39,689,338
Trey Brantley             $6,313,057

Roster count: 15
Hard cap: second apron

We're hard-capped at the second apron. Can we add Bogdan Brantley at $4,054,341?
```

**Ground truth:** {"legal": false, "hard_cap": "second apron", "hard_cap_limit": 188931000, "room_below_hard_cap": 6191809, "salary": 4054341, "apron_salary_after": 186793532, "reasons": ["Houston already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $4,054,341, $188,931,000

**Computation trace (the only figures you may use):**

```
  1. Houston apron salary before signing = $182,739,191 (over the first apron)
  2. Proposed salary for Bogdan Brantley = $4,054,341
  3. Exception: minimum salary exception
  4. Houston apron salary after signing = $186,793,532
  5. Hard cap: second apron = $188,931,000
  6. Room below the hard cap = $2,137,468
  7. VIOLATION -- roster is full (15-man limit reached)
  8. Verdict: ILLEGAL
  9. Room below the second apron hard cap before signing = $6,191,809 ($188,931,000 - $182,739,191)
```


## Scenario 10 -- exception_survey

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

ORLANDO -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Alperen Vasquez | $42,734,093 | -- | 3 |
| Darnell Boateng | $3,518,478 | -- | 1 |
| Nikola Dumont | $2,743,804 | -- | 3 |
| Nico Dumont | $3,840,965 | -- | 2 |
| Brennan Ibarra | $16,936,589 | -- | 2 |
| Cam Novak | $6,351,860 | -- | 1 |
| Brennan Osei | $7,844,247 | -- | 4 |
| Luka Beauchamp | $23,276,155 | -- | 4 |
| Zion Nakamura | $4,503,579 | -- | 1 |
| Nikola Vasquez | $2,729,272 | -- | 3 |
| Julian Ibarra | $23,015,020 | -- | 3 |
| Micah Petrov | $26,739,930 | -- | 3 |
| Bogdan Lindqvist | $3,688,390 | -- | 2 |
| Malik Novak | $2,905,401 | -- | 3 |

Roster count: 14

Which exceptions can we actually use at this payroll?
```

**Ground truth:** {"apron_level": "under the tax line", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": true, "amount": 15044000, "reason": "available at $15,044,000; using it hard-caps the team at the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 6064000, "reason": "available at $6,064,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": true, "amount": 5477000, "reason": "available at $5,477,000; using it hard-caps the team at the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Orlando apron salary = $170,827,783 (under the tax line)
  2. 2026-27 first apron = $209,015,000
  3. 2026-27 second apron = $221,686,000
  4. non-taxpayer mid-level exception: available = $15,044,000 (available at $15,044,000; using it hard-caps the team at the first apron)
  5. taxpayer mid-level exception: available = $6,064,000 (available at $6,064,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: available = $5,477,000 (available at $5,477,000; using it hard-caps the team at the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 11 -- exception_survey

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

UTAH -- 2024-25 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Dante Jokubaitis | $6,465,509 | -- | 2 |
| Isaiah Brantley | $13,562,855 | -- | 3 |
| Zion Ellington | $11,533,704 | -- | 2 |
| Brennan Reddish | $7,317,324 | -- | 3 |
| Amari Beauchamp | $37,188,198 | -- | 1 |
| Isaiah Achiuwa | $22,579,116 | -- | 4 |
| Elijah Petrov | $5,319,194 | -- | 3 |
| Devonte Amadi | $8,708,449 | -- | 1 |
| Nico Beauchamp | $48,608,496 | -- | 3 |
| Zion Rees | $2,509,819 | -- | 4 |
| Cam Halvorsen | $6,271,018 | -- | 4 |
| Trey Novak | $7,003,714 | -- | 3 |
| Nico Ferreira | $20,204,407 | -- | 1 |
| Terrance Rees | $2,314,374 | -- | 4 |

Roster count: 14

What signing exceptions do we still have available, and what does using each one cost us?
```

**Ground truth:** {"apron_level": "over the second apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the second apron -- no mid-level of any kind", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Utah apron salary = $199,586,177 (over the second apron)
  2. 2024-25 first apron = $178,132,000
  3. 2024-25 second apron = $188,931,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: unavailable (unavailable over the second apron -- no mid-level of any kind)
  6. bi-annual exception: unavailable (unavailable over the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 12 -- hard_cap_consequence

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
Corey Nakamura           $6,766,837
Julian Lindqvist         $3,510,205
Micah Vasquez            $6,396,021
Darnell Okoro            $4,764,047
Luka Amadi               $3,041,785
Tobias Nakamura          $8,348,169
Trey Ibarra             $14,601,088
Devonte Whitfield        $6,120,369
Zion Lindqvist          $49,946,203
Dante Okoro             $52,322,339
Julian Rees             $20,121,438
Tobias Achiuwa           $5,849,756
Luka Achiuwa             $6,220,573
Cam Beauchamp           $26,019,958
Goran Amadi              $2,640,445

Roster count: 15
Hard cap: second apron

We're hard-capped at the second apron. Can we add Luka Brantley at $3,305,705?
```

**Ground truth:** {"legal": false, "hard_cap": "second apron", "hard_cap_limit": 221686000, "room_below_hard_cap": 5016767, "salary": 3305705, "apron_salary_after": 219974938, "reasons": ["Toronto already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $3,305,705, $221,686,000

**Computation trace (the only figures you may use):**

```
  1. Toronto apron salary before signing = $216,669,233 (over the first apron)
  2. Proposed salary for Luka Brantley = $3,305,705
  3. Exception: minimum salary exception
  4. Toronto apron salary after signing = $219,974,938
  5. Hard cap: second apron = $221,686,000
  6. Room below the hard cap = $1,711,062
  7. VIOLATION -- roster is full (15-man limit reached)
  8. Verdict: ILLEGAL
  9. Room below the second apron hard cap before signing = $5,016,767 ($221,686,000 - $216,669,233)
```


## Scenario 13 -- tax_bill

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

HOUSTON -- 2026-27 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Dante Ibarra,9669368,0,1
Nico Kearns,11944264,0,4
Kristaps Amadi,4069282,0,3
Marcus Vasquez,4041048,0,4
Trey Nakamura,4904992,0,3
Jaylen Okoro,57736350,0,2
Jaylen Novak,7826960,0,2
Julian Osei,3993671,0,1
Terrance Lindqvist,7691924,0,4
Julian Cordero,12764780,0,2
Julian Sabonis,38449832,0,4
Rashad Stavros,21798851,0,2
Nico Osei,6484624,0,2
Malik Osei,6078914,0,2
Santi Ellington,4491013,0,1

Roster count: 15

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 201945873, "tax_line": 200428000, "amount_over": 1517873, "is_repeater": false, "total": 1517873, "brackets": [{"index": 1, "amount": 1517873, "rate": 1.0, "owed": 1517873}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $1,517,873, $1,517,873

**Computation trace (the only figures you may use):**

```
  1. Houston tax salary = $201,945,873
  2. 2026-27 luxury tax line = $200,428,000
  3. Amount over the tax line = $1,517,873 ($201,945,873 - $200,428,000)
  4. Rate schedule: standard (2026-27) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $1,517,873 at $1.00 per dollar = $1,517,873
  6. Total luxury tax owed = $1,517,873
  7. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 14 -- trade_legality

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

UTAH -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Nico Ellington | $7,279,274 | -- | 4 |
| Luka Beauchamp | $7,789,812 | -- | 1 |
| Dante Achiuwa | $19,284,336 | -- | 1 |
| Kellen Whitfield | $4,806,222 | -- | 3 |
| Micah Achiuwa | $42,451,865 | -- | 4 |
| Corey Novak | $3,612,863 | -- | 3 |
| Kristaps Stavros | $7,057,823 | -- | 3 |
| Santi Marsh | $7,689,561 | -- | 2 |
| Terrance Jokubaitis | $6,326,053 | -- | 1 |
| Micah Marsh | $11,159,329 | -- | 1 |
| Jalil Osei | $6,577,777 | -- | 2 |
| Rashad Duval | $6,862,450 | -- | 2 |
| Kristaps Kearns | $50,699,242 | -- | 3 |
| Andre Kearns | $24,842,286 | -- | 4 |

Roster count: 14

We're discussing a trade that sends Kristaps Kearns and Corey Novak to another team for Kellen Sabonis at $73,345,308. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 54312105, "incoming_salary": 73345308, "max_incoming": 68140131, "matching_rule": "125% + $250,000 (outgoing above $35,170,000)", "apron_level": "over the tax line", "apron_salary_after": 225472096, "hard_cap_triggered": "first apron", "violations": ["Utah: salary matching -- Utah takes back $73,345,308 but may only absorb $68,140,131 under 125% + $250,000 (outgoing above $35,170,000) -- over by $5,205,177", "Utah: hard cap exceeded -- Utah would sit at $225,472,096, above its first apron hard cap of $209,015,000 -- over by $16,457,096"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $54,312,105, $73,345,308, $68,140,131

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Utah
  2. --- Utah (2026-27) --- (apron salary $206,438,893, over the tax line)
  3. Utah outgoing salary = $54,312,105 (Kristaps Kearns $50,699,242, Corey Novak $3,612,863)
  4. Utah incoming salary = $73,345,308 (Kellen Sabonis $73,345,308)
  5. Utah matching limit = $68,140,131 (125% + $250,000 (outgoing above $35,170,000))
  6. VIOLATION -- salary matching (Utah takes back $73,345,308 but may only absorb $68,140,131 under 125% + $250,000 (outgoing above $35,170,000) -- over by $5,205,177)
  7. Utah hard-capped at the first apron = $209,015,000 (took back more than 100% of outgoing salary)
  8. Utah hard-capped at the second apron = $221,686,000 (aggregated two or more salaries in one trade)
  9. Two hard caps triggered -- the tighter one governs = $209,015,000
  10. Utah apron salary after the trade = $225,472,096
  11. VIOLATION -- hard cap exceeded (Utah would sit at $225,472,096, above its first apron hard cap of $209,015,000 -- over by $16,457,096)
  12. Verdict: ILLEGAL
```


## Scenario 15 -- stretch_provision

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

If we waive and stretch Andre Ellington -- $111,600,000 left over 1 year -- what does the dead money look like, and is it even allowed?
```

**Ground truth:** {"legal": false, "remaining_salary": 111600000, "years_remaining": 1, "stretch_years": 3, "annual_dead_money": 37200000, "existing_stretched": 5700000, "limit": 23197050, "givebacks_required": 59108850, "reason": "the stretch is not legal as structured: $42,900,000 of dead money would exceed the $23,197,050 ceiling by $19,702,950 per season. The player would have to give back roughly $59,108,850 for the waiver to work"}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $37,200,000, $23,197,050

**Computation trace (the only figures you may use):**

```
  1. Salary remaining on the contract = $111,600,000
  2. Years remaining (1)
  3. Stretch period (2 x 1 + 1 = 3 seasons)
  4. Annual dead money if stretched = $37,200,000 ($111,600,000 / 3)
  5. Dead money already stretched = $5,700,000
  6. Total stretched dead money = $42,900,000
  7. Limit (15% of the 2025-26 cap) = $23,197,050 (15% x $154,647,000)
  8. VIOLATION -- exceeds the dead-money ceiling = $19,702,950
  9. Approximate giveback required = $59,108,850 ($19,702,950 x 3 seasons)
```


## Scenario 16 -- exception_survey

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

DETROIT -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Santi Okoro,7614335,0,1
Nikola Okoro,2210997,0,3
Deni Duval,16986666,0,4
Terrance Nakamura,4030808,0,2
Dante Duval,3220777,0,1
Brennan Sabonis,15222876,0,2
Kobe Petrov,21958292,0,1
Kobe Vasquez,7097372,0,4
Alperen Ferreira,3335517,0,2
Jaylen Boateng,26900322,0,3
Kellen Brantley,6376218,0,4
Luka Stavros,44945705,0,3
Rashad Amadi,8865505,0,2

Roster count: 13

Which exceptions can we actually use at this payroll?
```

**Ground truth:** {"apron_level": "under the tax line", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": true, "amount": 12822000, "reason": "available at $12,822,000; using it hard-caps the team at the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 5168000, "reason": "available at $5,168,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": true, "amount": null, "reason": "available, but the published amount for this season is not on file", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Detroit apron salary = $168,765,390 (under the tax line)
  2. 2024-25 first apron = $178,132,000
  3. 2024-25 second apron = $188,931,000
  4. non-taxpayer mid-level exception: available = $12,822,000 (available at $12,822,000; using it hard-caps the team at the first apron)
  5. taxpayer mid-level exception: available = $5,168,000 (available at $5,168,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: available (available, but the published amount for this season is not on file)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 17 -- tax_bill

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

WASHINGTON -- 2024-25 CAP SHEET
Andre Ferreira         $46,102,546
Isaiah Kalinic          $2,979,106
Malik Brantley          $5,217,577
Devonte Amadi           $2,131,887
Nico Amadi              $5,965,078
Brennan Dumont         $16,630,794
Kellen Rees             $3,660,339
Deni Cordero           $23,895,571
Devonte Marsh           $2,502,544
Malik Vasquez          $18,305,767
Kristaps Achiuwa        $4,330,982
Kristaps Vasquez        $9,732,722
Kobe Achiuwa            $2,740,749
Rashad Achiuwa         $39,367,229

Roster count: 14
Repeater taxpayer: yes

What's our luxury tax bill this season? Walk me through the brackets.
```

**Ground truth:** {"tax_salary": 183562891, "tax_line": 170814000, "amount_over": 12748891, "is_repeater": true, "total": 35577118, "brackets": [{"index": 1, "amount": 5168000, "rate": 2.5, "owed": 12920000}, {"index": 2, "amount": 5168000, "rate": 2.75, "owed": 14212000}, {"index": 3, "amount": 2412891, "rate": 3.5, "owed": 8445118}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $35,577,118, $12,748,891

**Computation trace (the only figures you may use):**

```
  1. Washington tax salary = $183,562,891
  2. 2024-25 luxury tax line = $170,814,000
  3. Amount over the tax line = $12,748,891 ($183,562,891 - $170,814,000)
  4. Rate schedule: repeater (2024-25) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $5,168,000 at $2.50 per dollar = $12,920,000
  6. Bracket 2: $5,168,000 at $2.75 per dollar = $14,212,000
  7. Bracket 3: $2,412,891 at $3.50 per dollar = $8,445,118
  8. Total luxury tax owed = $35,577,118
  9. Repeater status applies (paid the tax in 3 of the prior 4 seasons)
  10. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 18 -- hard_cap_consequence

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
| Andre Okoro | $40,460,076 | -- | 2 |
| Darnell Ellington | $8,289,954 | -- | 2 |
| Jalil Halvorsen | $6,731,031 | -- | 3 |
| Darnell Stavros | $57,736,350 | -- | 1 |
| Corey Beauchamp | $12,891,347 | -- | 1 |
| Darnell Achiuwa | $7,420,236 | -- | 1 |
| Jalil Duval | $9,763,279 | -- | 1 |
| Luka Rees | $10,831,035 | -- | 4 |
| Rashad Dumont | $12,302,122 | -- | 1 |
| Deni Stavros | $6,274,992 | -- | 4 |
| Elijah Kearns | $11,653,297 | -- | 4 |
| Alperen Rees | $12,321,212 | -- | 1 |
| Nico Ferreira | $6,479,666 | -- | 1 |
| Brennan Brantley | $13,049,190 | -- | 3 |

Roster count: 14
Hard cap: second apron

We're hard-capped at the second apron. Can we add Bogdan Ferreira at $2,688,425?
```

**Ground truth:** {"legal": true, "hard_cap": "second apron", "hard_cap_limit": 221686000, "room_below_hard_cap": 5482213, "salary": 2688425, "apron_salary_after": 218892212, "reasons": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $2,688,425, $221,686,000

**Computation trace (the only figures you may use):**

```
  1. Atlanta apron salary before signing = $216,203,787 (over the first apron)
  2. Proposed salary for Bogdan Ferreira = $2,688,425
  3. Exception: minimum salary exception
  4. Atlanta apron salary after signing = $218,892,212
  5. Hard cap: second apron = $221,686,000
  6. Room below the hard cap = $2,793,788
  7. Verdict: LEGAL
  8. Room below the second apron hard cap before signing = $5,482,213 ($221,686,000 - $216,203,787)
```


## Scenario 19 -- apron_status

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

DETROIT -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Dante Boateng,4275310,1666666,1
Micah Achiuwa,29390128,0,3
Alperen Halvorsen,5407540,0,1
Brennan Nakamura,6092938,0,2
Jaylen Lindqvist,35818483,0,2
Terrance Boateng,12263035,0,1
Kobe Kearns,6151954,0,4
Dante Sabonis,5601157,0,4
Brennan Boateng,2447381,0,1
Elijah Rees,3113756,0,2
Tobias Ellington,3723294,0,1
Marcus Marsh,4681217,1666668,3
Malik Sabonis,7940140,0,2
Elijah Novak,11238598,0,4
Malik Marsh,6180175,1666666,2

Roster count: 15

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 144325106, "unlikely_incentives": 5000000, "apron_salary": 149325106, "apron_level": "under the tax line", "room_to_first_apron": 28806894, "room_to_second_apron": 39605894}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $149,325,106

**Computation trace (the only figures you may use):**

```
  1. Detroit salaries plus likely incentives = $144,325,106
  2. Unlikely incentives = $5,000,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $149,325,106
  4. 2024-25 luxury tax line = $170,814,000
  5. 2024-25 first apron = $178,132,000
  6. 2024-25 second apron = $188,931,000
  7. Position: under the tax line
  8. Room below the tax line = $21,488,894
  9. Room below the first apron = $28,806,894
  10. Room below the second apron = $39,605,894
```


## Scenario 20 -- apron_status

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

ORLANDO -- 2025-26 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Elijah Okoro | $7,124,992 | $1,766,668 | 1 |
| Cam Brantley | $5,591,688 | -- | 3 |
| Jalil Rees | $5,573,213 | $1,766,666 | 4 |
| Trey Reddish | $24,845,825 | -- | 2 |
| Dante Brantley | $2,296,000 | -- | 2 |
| Tobias Novak | $41,134,881 | $1,766,666 | 1 |
| Elijah Kalinic | $20,527,693 | -- | 1 |
| Julian Cordero | $6,921,414 | -- | 3 |
| Nico Lindqvist | $19,709,659 | -- | 1 |
| Rashad Kalinic | $14,930,461 | -- | 3 |
| Kobe Marsh | $33,951,480 | -- | 3 |
| Luka Ferreira | $6,292,550 | -- | 4 |
| Malik Kalinic | $4,856,953 | -- | 3 |

Roster count: 13

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 193756809, "unlikely_incentives": 5300000, "apron_salary": 199056809, "apron_level": "over the first apron", "room_to_first_apron": -3111809, "room_to_second_apron": 8767191}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $199,056,809

**Computation trace (the only figures you may use):**

```
  1. Orlando salaries plus likely incentives = $193,756,809
  2. Unlikely incentives = $5,300,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $199,056,809
  4. 2025-26 luxury tax line = $187,895,000
  5. 2025-26 first apron = $195,945,000
  6. 2025-26 second apron = $207,824,000
  7. Position: over the first apron
  8. Amount above the tax line = $11,161,809
  9. Amount above the first apron = $3,111,809
  10. Room below the second apron = $8,767,191
```


## Scenario 21 -- tax_bill

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

SAN ANTONIO -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Goran Sabonis,22927171,0,4
Micah Stavros,16755195,0,4
Corey Whitfield,4568594,0,2
Santi Petrov,13395166,0,1
Goran Reddish,2408502,0,4
Trey Kearns,4670562,0,2
Kobe Dumont,39964964,0,2
Malik Vasquez,19847330,0,3
Tobias Achiuwa,5675984,0,1
Elijah Nakamura,40376586,0,1
Jaylen Stavros,6988519,0,4
Kristaps Duval,5553562,0,4
Nico Cordero,3170982,0,4
Bogdan Dumont,2908740,0,4
Alperen Halvorsen,2651184,0,1

Roster count: 15

What's our luxury tax bill this season? Walk me through the brackets.
```

**Ground truth:** {"tax_salary": 191863041, "tax_line": 187895000, "amount_over": 3968041, "is_repeater": false, "total": 3968041, "brackets": [{"index": 1, "amount": 3968041, "rate": 1.0, "owed": 3968041}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $3,968,041, $3,968,041

**Computation trace (the only figures you may use):**

```
  1. San Antonio tax salary = $191,863,041
  2. 2025-26 luxury tax line = $187,895,000
  3. Amount over the tax line = $3,968,041 ($191,863,041 - $187,895,000)
  4. Rate schedule: standard (2025-26) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $3,968,041 at $1.00 per dollar = $3,968,041
  6. Total luxury tax owed = $3,968,041
  7. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 22 -- exception_eligibility

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

ORLANDO -- 2026-27 CAP SHEET
Julian Kalinic          $3,251,894
Goran Brantley          $6,506,265
Andre Jokubaitis        $5,113,469
Micah Petrov           $39,217,729
Kobe Kalinic           $18,368,235
Corey Stavros           $5,383,759
Deni Marsh              $4,416,286
Goran Jokubaitis       $11,755,752
Dante Rees              $3,542,603
Marcus Stavros         $19,571,519
Nikola Dumont           $3,225,591
Kristaps Achiuwa       $34,805,050
Nikola Marsh            $3,143,282
Elijah Whitfield        $3,002,986
Tobias Vasquez          $5,247,025

Roster count: 15

Can we sign Terrance Novak for $3,110,290 using the minimum salary exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "minimum salary exception", "salary": 3110290, "hard_cap_triggered": "none", "apron_level": "under the tax line", "apron_salary_after": 169661735, "reasons": ["Orlando already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $3,110,290

**Computation trace (the only figures you may use):**

```
  1. Orlando apron salary before signing = $166,551,445 (under the tax line)
  2. Proposed salary for Terrance Novak = $3,110,290
  3. Exception: minimum salary exception
  4. Orlando apron salary after signing = $169,661,735
  5. VIOLATION -- roster is full (15-man limit reached)
  6. Verdict: ILLEGAL
```


## Scenario 23 -- trade_legality

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
player,salary,unlikely_incentives,years_remaining
Terrance Kearns,4878477,0,2
Luka Vasquez,2803170,0,3
Kellen Duval,5792287,0,4
Jaylen Achiuwa,3529088,0,2
Cam Vasquez,3237742,0,1
Marcus Novak,34047841,0,3
Devonte Whitfield,4293321,0,4
Dante Rees,9583776,0,4
Devonte Vasquez,5186102,0,4
Alperen Ellington,17827102,0,1
Nikola Rees,4214878,0,1
Nikola Amadi,7160341,0,1
Nikola Duval,35992801,0,1
Brennan Brantley,19409864,0,1

Roster count: 14

We're discussing a trade that sends Nikola Amadi and Marcus Novak to another team for Amari Rees at $39,935,602. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 41208182, "incoming_salary": 39935602, "max_incoming": 51760227, "matching_rule": "125% + $250,000 (outgoing above $35,170,000)", "apron_level": "under the tax line", "apron_salary_after": 156684210, "hard_cap_triggered": "second apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $41,208,182, $39,935,602, $51,760,227

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Atlanta
  2. --- Atlanta (2026-27) --- (apron salary $157,956,790, under the tax line)
  3. Atlanta outgoing salary = $41,208,182 (Nikola Amadi $7,160,341, Marcus Novak $34,047,841)
  4. Atlanta incoming salary = $39,935,602 (Amari Rees $39,935,602)
  5. Atlanta matching limit = $51,760,227 (125% + $250,000 (outgoing above $35,170,000))
  6. Atlanta hard-capped at the second apron = $221,686,000 (aggregated two or more salaries in one trade)
  7. Atlanta apron salary after the trade = $156,684,210
  8. Atlanta stays under its second apron hard cap = $65,001,790 ($221,686,000 - $156,684,210 of room to spare)
  9. Verdict: LEGAL
```


## Scenario 24 -- apron_status

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
Nikola Rees             $54,126,450
Dante Brantley          $12,074,146
Nico Beauchamp          $13,397,751   (+$1,700,000 unlikely)
Zion Kearns             $10,772,389   (+$1,700,000 unlikely)
Dante Kalinic           $12,589,811
Luka Dumont              $5,221,262
Goran Duval             $14,431,655
Terrance Ferreira        $8,248,018
Nikola Marsh             $8,692,286   (+$1,700,000 unlikely)
Kristaps Ibarra         $13,885,828
Marcus Vasquez           $7,364,798
Julian Petrov           $38,907,515
Isaiah Okoro             $7,512,348
Devonte Reddish          $8,839,711
Nikola Reddish           $6,807,781

Roster count: 15

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 222871749, "unlikely_incentives": 5100000, "apron_salary": 227971749, "apron_level": "over the second apron", "room_to_first_apron": -32026749, "room_to_second_apron": -20147749}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $227,971,749

**Computation trace (the only figures you may use):**

```
  1. Utah salaries plus likely incentives = $222,871,749
  2. Unlikely incentives = $5,100,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $227,971,749
  4. 2025-26 luxury tax line = $187,895,000
  5. 2025-26 first apron = $195,945,000
  6. 2025-26 second apron = $207,824,000
  7. Position: over the second apron
  8. Amount above the tax line = $40,076,749
  9. Amount above the first apron = $32,026,749
  10. Amount above the second apron = $20,147,749
```


## Scenario 25 -- exception_eligibility

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
Elijah Marsh            $7,203,725
Marcus Kearns          $40,792,286
Corey Osei              $2,088,000
Alperen Nakamura        $7,389,882
Elijah Rees             $3,853,404
Devonte Okoro          $10,590,637
Goran Jokubaitis        $6,140,037
Jaylen Dumont          $17,162,712
Amari Cordero           $5,051,169
Nikola Stavros          $5,955,759
Dante Ferreira         $25,600,384
Alperen Duval           $7,069,391
Malik Osei              $6,591,681
Kobe Stavros            $8,105,375
Jalil Cordero          $32,200,995

Roster count: 15

Can we sign Rashad Nakamura for $1,253,319 using the minimum salary exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "minimum salary exception", "salary": 1253319, "hard_cap_triggered": "none", "apron_level": "over the first apron", "apron_salary_after": 187048756, "reasons": ["Memphis already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $1,253,319

**Computation trace (the only figures you may use):**

```
  1. Memphis apron salary before signing = $185,795,437 (over the first apron)
  2. Proposed salary for Rashad Nakamura = $1,253,319
  3. Exception: minimum salary exception
  4. Memphis apron salary after signing = $187,048,756
  5. VIOLATION -- roster is full (15-man limit reached)
  6. Verdict: ILLEGAL
```


## Scenario 26 -- hard_cap_consequence

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
Deni Novak              $6,793,807
Corey Nakamura         $12,018,077
Luka Petrov            $14,419,331
Goran Amadi             $3,735,833
Andre Brantley          $7,079,466
Micah Stavros           $5,310,899
Jaylen Novak            $6,236,583
Darnell Ferreira       $33,547,633
Kellen Reddish         $37,447,568
Trey Novak             $12,628,273
Andre Dumont            $7,764,846
Micah Rees             $19,755,109
Darnell Ibarra          $5,244,832

Roster count: 13
Hard cap: first apron

We're hard-capped at the first apron. Can we add Dante Brantley at $5,009,094?
```

**Ground truth:** {"legal": true, "hard_cap": "first apron", "hard_cap_limit": 178132000, "room_below_hard_cap": 6149743, "salary": 5009094, "apron_salary_after": 176991351, "reasons": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $5,009,094, $178,132,000

**Computation trace (the only figures you may use):**

```
  1. Miami apron salary before signing = $171,982,257 (over the tax line)
  2. Proposed salary for Dante Brantley = $5,009,094
  3. Exception: minimum salary exception
  4. Miami apron salary after signing = $176,991,351
  5. Hard cap: first apron = $178,132,000
  6. Room below the hard cap = $1,140,649
  7. Verdict: LEGAL
  8. Room below the first apron hard cap before signing = $6,149,743 ($178,132,000 - $171,982,257)
```


## Scenario 27 -- exception_survey

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Bogdan Reddish | $25,504,311 | -- | 2 |
| Jaylen Kalinic | $2,713,479 | -- | 3 |
| Santi Duval | $8,002,770 | -- | 4 |
| Kellen Kearns | $23,597,309 | -- | 2 |
| Malik Vasquez | $3,889,008 | -- | 4 |
| Julian Reddish | $7,761,524 | -- | 1 |
| Isaiah Marsh | $3,416,755 | -- | 2 |
| Zion Marsh | $42,735,810 | -- | 4 |
| Trey Kearns | $3,627,524 | -- | 4 |
| Marcus Jokubaitis | $2,317,380 | -- | 3 |
| Jaylen Vasquez | $14,941,008 | -- | 2 |
| Trey Amadi | $42,844,041 | -- | 3 |
| Bogdan Halvorsen | $22,546,855 | -- | 3 |

Roster count: 13

Run me through our tools in free agency this summer.
```

**Ground truth:** {"apron_level": "over the first apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 5685000, "reason": "available at $5,685,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Utah apron salary = $203,897,774 (over the first apron)
  2. 2025-26 first apron = $195,945,000
  3. 2025-26 second apron = $207,824,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: available = $5,685,000 (available at $5,685,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: unavailable (unavailable over the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 28 -- trade_legality

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

INDIANA -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Elijah Marsh,26348386,0,4
Elijah Stavros,3479637,0,3
Julian Vasquez,10222375,0,4
Corey Rees,8453354,0,1
Amari Halvorsen,10142116,0,2
Devonte Cordero,11087092,0,4
Trey Ferreira,8554373,0,2
Nikola Halvorsen,22882679,0,3
Alperen Dumont,29767390,0,1
Kobe Osei,11728988,0,1
Trey Kearns,10187480,0,2
Nico Novak,4688578,0,1
Nikola Boateng,49205800,0,3

Roster count: 13

We're discussing a trade that sends Corey Rees to another team for Julian Vasquez at $10,001,143. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 8453354, "incoming_salary": 10001143, "max_incoming": 8453354, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 208296037, "hard_cap_triggered": "none", "violations": ["Indiana: salary matching -- Indiana takes back $10,001,143 but may only absorb $8,453,354 under 100% of outgoing salary (team is over the first apron) -- over by $1,547,789"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $8,453,354, $10,001,143, $8,453,354

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Indiana
  2. --- Indiana (2024-25) --- (apron salary $206,748,248, over the second apron)
  3. Indiana outgoing salary = $8,453,354 (Corey Rees $8,453,354)
  4. Indiana incoming salary = $10,001,143 (Julian Vasquez $10,001,143)
  5. Indiana matching limit = $8,453,354 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (Indiana takes back $10,001,143 but may only absorb $8,453,354 under 100% of outgoing salary (team is over the first apron) -- over by $1,547,789)
  7. Indiana apron salary after the trade = $208,296,037
  8. Verdict: ILLEGAL
```


## Scenario 29 -- anti_staleness

**What the user said:**

```
2028-29 LEAGUE THRESHOLDS
  Salary cap:          $169,691,000
  Luxury tax line:     $206,173,000
  First apron:         $215,006,000
  Second apron:        $228,041,000
  Non-taxpayer MLE:    $15,476,000
  Taxpayer MLE:        $6,238,000
  Room exception:      $9,635,000
  Tax bracket width:   $6,238,000
  Bi-annual exception: $5,486,000

INDIANA -- 2028-29 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Andre Halvorsen,8901421,0,2
Julian Kearns,5366792,0,3
Devonte Marsh,52818342,0,1
Deni Dumont,18564894,0,1
Cam Brantley,8577949,0,4
Andre Sabonis,8638560,0,3
Jalil Vasquez,3732583,0,3
Andre Dumont,4188989,0,4
Kristaps Rees,11763122,0,2
Julian Novak,3318040,0,2
Nikola Stavros,54540736,0,3
Elijah Nakamura,8590629,0,2
Terrance Whitfield,20864181,0,3
Nikola Ferreira,6244803,0,3
Nico Sabonis,2910459,0,4

Roster count: 15

Using the 2028-29 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2028-29", "apron_salary": 219021500, "apron_level": "over the first apron", "first_apron_provided": 215006000, "second_apron_provided": 228041000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $219,021,500, $228,041,000

**Computation trace (the only figures you may use):**

```
  1. Indiana apron salary = $219,021,500
  2. 2028-29 first apron (from the figures provided) = $215,006,000
  3. 2028-29 second apron (from the figures provided) = $228,041,000
  4. Position: over the first apron
  5. Room below the second apron = $9,019,500
```


## Scenario 30 -- stretch_provision

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

If we waive and stretch Marcus Nakamura -- $69,200,000 left over 2 years -- what does the dead money look like, and is it even allowed?
```

**Ground truth:** {"legal": true, "remaining_salary": 69200000, "years_remaining": 2, "stretch_years": 5, "annual_dead_money": 13840000, "existing_stretched": 0, "limit": 24744150, "givebacks_required": 0, "reason": "the stretch is legal: $13,840,000 of total dead money sits below the $24,744,150 ceiling"}

**Verdict:** LEGAL

**Required figures (must all appear):** $13,840,000, $24,744,150

**Computation trace (the only figures you may use):**

```
  1. Salary remaining on the contract = $69,200,000
  2. Years remaining (2)
  3. Stretch period (2 x 2 + 1 = 5 seasons)
  4. Annual dead money if stretched = $13,840,000 ($69,200,000 / 5)
  5. Dead money already stretched = $0
  6. Total stretched dead money = $13,840,000
  7. Limit (15% of the 2026-27 cap) = $24,744,150 (15% x $164,961,000)
  8. Legal = $10,904,150 (room to spare)
```


## Scenario 31 -- trade_legality

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

UTAH -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Kellen Sabonis | $8,803,054 | -- | 1 |
| Santi Novak | $6,919,509 | -- | 4 |
| Nico Kalinic | $6,130,957 | -- | 2 |
| Corey Stavros | $6,129,512 | -- | 1 |
| Marcus Ellington | $5,120,603 | -- | 1 |
| Malik Whitfield | $5,449,357 | -- | 4 |
| Tobias Sabonis | $2,508,789 | -- | 4 |
| Bogdan Ferreira | $3,753,884 | -- | 2 |
| Corey Jokubaitis | $8,427,108 | -- | 2 |
| Malik Jokubaitis | $23,097,510 | -- | 4 |
| Darnell Novak | $7,946,928 | -- | 1 |
| Deni Kalinic | $15,735,329 | -- | 4 |
| Zion Whitfield | $6,149,922 | -- | 4 |
| Julian Whitfield | $54,174,638 | -- | 4 |

Roster count: 14

We're discussing a trade that sends Julian Whitfield to another team for Julian Kalinic at $80,598,233. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 54174638, "incoming_salary": 80598233, "max_incoming": 67968297, "matching_rule": "125% + $250,000 (outgoing above $35,170,000)", "apron_level": "under the tax line", "apron_salary_after": 186770695, "hard_cap_triggered": "first apron", "violations": ["Utah: salary matching -- Utah takes back $80,598,233 but may only absorb $67,968,297 under 125% + $250,000 (outgoing above $35,170,000) -- over by $12,629,936"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $54,174,638, $80,598,233, $67,968,297

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Utah
  2. --- Utah (2026-27) --- (apron salary $160,347,100, under the tax line)
  3. Utah outgoing salary = $54,174,638 (Julian Whitfield $54,174,638)
  4. Utah incoming salary = $80,598,233 (Julian Kalinic $80,598,233)
  5. Utah matching limit = $67,968,297 (125% + $250,000 (outgoing above $35,170,000))
  6. VIOLATION -- salary matching (Utah takes back $80,598,233 but may only absorb $67,968,297 under 125% + $250,000 (outgoing above $35,170,000) -- over by $12,629,936)
  7. Utah hard-capped at the first apron = $209,015,000 (took back more than 100% of outgoing salary)
  8. Utah apron salary after the trade = $186,770,695
  9. Utah stays under its first apron hard cap = $22,244,305 ($209,015,000 - $186,770,695 of room to spare)
  10. Verdict: ILLEGAL
```


## Scenario 32 -- trade_legality

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

ORLANDO -- 2026-27 CAP SHEET
Deni Dumont              $5,736,813
Luka Kalinic             $7,186,368
Malik Ellington         $40,742,882
Bogdan Duval             $3,630,400
Tobias Jokubaitis        $6,973,933
Bogdan Sabonis          $22,462,735
Kristaps Osei            $5,765,798
Kellen Ibarra            $5,774,015
Deni Amadi              $19,161,160
Julian Marsh            $46,700,757
Nico Vasquez             $7,348,893
Devonte Brantley         $4,702,502
Julian Kearns           $22,576,509
Kellen Petrov            $2,916,795

Roster count: 14

We're discussing a trade that sends Devonte Brantley to another team for Julian Cordero at $11,891,742. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 4702502, "incoming_salary": 11891742, "max_incoming": 9655004, "matching_rule": "200% + $250,000 (outgoing at or below $9,096,000)", "apron_level": "over the tax line", "apron_salary_after": 208868800, "hard_cap_triggered": "first apron", "violations": ["Orlando: salary matching -- Orlando takes back $11,891,742 but may only absorb $9,655,004 under 200% + $250,000 (outgoing at or below $9,096,000) -- over by $2,236,738"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $4,702,502, $11,891,742, $9,655,004

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Orlando
  2. --- Orlando (2026-27) --- (apron salary $201,679,560, over the tax line)
  3. Orlando outgoing salary = $4,702,502 (Devonte Brantley $4,702,502)
  4. Orlando incoming salary = $11,891,742 (Julian Cordero $11,891,742)
  5. Orlando matching limit = $9,655,004 (200% + $250,000 (outgoing at or below $9,096,000))
  6. VIOLATION -- salary matching (Orlando takes back $11,891,742 but may only absorb $9,655,004 under 200% + $250,000 (outgoing at or below $9,096,000) -- over by $2,236,738)
  7. Orlando hard-capped at the first apron = $209,015,000 (took back more than 100% of outgoing salary)
  8. Orlando apron salary after the trade = $208,868,800
  9. Orlando stays under its first apron hard cap = $146,200 ($209,015,000 - $208,868,800 of room to spare)
  10. Verdict: ILLEGAL
```


## Scenario 33 -- apron_status

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

HOUSTON -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Dante Ferreira | $5,780,690 | -- | 1 |
| Bogdan Halvorsen | $57,736,350 | -- | 1 |
| Kobe Nakamura | $8,647,006 | -- | 3 |
| Devonte Jokubaitis | $26,470,115 | -- | 1 |
| Trey Ibarra | $25,691,925 | -- | 2 |
| Luka Brantley | $3,201,207 | -- | 2 |
| Amari Novak | $3,660,725 | -- | 4 |
| Kellen Ibarra | $9,707,481 | -- | 1 |
| Jalil Boateng | $8,263,791 | -- | 1 |
| Cam Dumont | $10,061,210 | -- | 4 |
| Alperen Novak | $6,678,403 | -- | 1 |
| Nico Nakamura | $9,531,699 | -- | 3 |
| Trey Jokubaitis | $4,426,695 | -- | 4 |
| Malik Cordero | $7,337,219 | -- | 1 |
| Nikola Stavros | $9,783,086 | -- | 4 |

Roster count: 15

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 196977602, "unlikely_incentives": 0, "apron_salary": 196977602, "apron_level": "under the tax line", "room_to_first_apron": 12037398, "room_to_second_apron": 24708398}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $196,977,602

**Computation trace (the only figures you may use):**

```
  1. Houston salaries plus likely incentives = $196,977,602
  2. Apron salary = $196,977,602
  3. 2026-27 luxury tax line = $200,428,000
  4. 2026-27 first apron = $209,015,000
  5. 2026-27 second apron = $221,686,000
  6. Position: under the tax line
  7. Room below the tax line = $3,450,398
  8. Room below the first apron = $12,037,398
  9. Room below the second apron = $24,708,398
```


## Scenario 34 -- anti_staleness

**What the user said:**

```
2028-29 LEAGUE THRESHOLDS
  Salary cap:          $168,428,000
  Luxury tax line:     $204,639,000
  First apron:         $213,406,000
  Second apron:        $226,344,000
  Non-taxpayer MLE:    $15,361,000
  Taxpayer MLE:        $6,192,000
  Room exception:      $9,564,000
  Tax bracket width:   $6,192,000
  Bi-annual exception: $5,446,000

UTAH -- 2028-29 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Julian Halvorsen,5178094,0,4
Kristaps Osei,58949799,0,3
Zion Osei,31389002,0,1
Luka Kearns,16168241,0,2
Zion Brantley,12833826,0,4
Kobe Beauchamp,5244149,0,1
Kellen Jokubaitis,6177590,0,3
Kobe Sabonis,4337871,0,3
Corey Kalinic,4191630,0,3
Kellen Vasquez,4872863,0,4
Goran Whitfield,27147666,0,4
Kristaps Whitfield,8413975,0,3
Corey Achiuwa,11743329,0,4
Corey Okoro,10091280,0,1

Roster count: 14

Using the 2028-29 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2028-29", "apron_salary": 206739315, "apron_level": "over the tax line", "first_apron_provided": 213406000, "second_apron_provided": 226344000, "would_be_wrong_using_published_figures": "over the first apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $206,739,315, $226,344,000

**Computation trace (the only figures you may use):**

```
  1. Utah apron salary = $206,739,315
  2. 2028-29 first apron (from the figures provided) = $213,406,000
  3. 2028-29 second apron (from the figures provided) = $226,344,000
  4. Position: over the tax line
  5. Room below the second apron = $19,604,685
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

SAN ANTONIO -- 2025-26 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Kellen Osei | $22,505,613 | -- | 3 |
| Isaiah Boateng | $10,587,627 | -- | 1 |
| Terrance Ferreira | $4,745,969 | -- | 1 |
| Luka Kearns | $5,819,561 | -- | 3 |
| Darnell Rees | $17,579,976 | -- | 1 |
| Brennan Cordero | $7,983,415 | -- | 4 |
| Andre Dumont | $6,007,279 | -- | 3 |
| Kellen Vasquez | $54,126,450 | -- | 2 |
| Jaylen Ellington | $8,388,734 | -- | 3 |
| Corey Ellington | $7,609,724 | -- | 4 |
| Goran Kearns | $9,564,842 | -- | 1 |
| Nikola Jokubaitis | $11,716,172 | -- | 2 |
| Andre Vasquez | $5,881,445 | -- | 2 |
| Nico Whitfield | $8,657,902 | -- | 2 |
| Julian Rees | $5,473,559 | -- | 4 |

Roster count: 15

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 186648268, "unlikely_incentives": 0, "apron_salary": 186648268, "apron_level": "under the tax line", "room_to_first_apron": 9296732, "room_to_second_apron": 21175732}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $186,648,268

**Computation trace (the only figures you may use):**

```
  1. San Antonio salaries plus likely incentives = $186,648,268
  2. Apron salary = $186,648,268
  3. 2025-26 luxury tax line = $187,895,000
  4. 2025-26 first apron = $195,945,000
  5. 2025-26 second apron = $207,824,000
  6. Position: under the tax line
  7. Room below the tax line = $1,246,732
  8. Room below the first apron = $9,296,732
  9. Room below the second apron = $21,175,732
```


## Scenario 36 -- trade_legality

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
| Rashad Nakamura | $6,282,504 | -- | 2 |
| Darnell Ferreira | $21,563,278 | -- | 2 |
| Marcus Ellington | $5,781,014 | -- | 2 |
| Malik Halvorsen | $23,408,607 | -- | 3 |
| Brennan Amadi | $6,637,558 | -- | 1 |
| Amari Halvorsen | $3,333,506 | -- | 4 |
| Goran Novak | $53,776,788 | -- | 4 |
| Marcus Ibarra | $4,619,983 | -- | 4 |
| Micah Novak | $42,996,953 | -- | 4 |
| Kobe Boateng | $5,177,564 | -- | 4 |
| Julian Vasquez | $11,348,830 | -- | 4 |
| Zion Halvorsen | $3,004,421 | -- | 4 |
| Brennan Ellington | $6,583,450 | -- | 3 |
| Amari Okoro | $7,511,126 | -- | 3 |

Roster count: 14

We're discussing a trade that sends Marcus Ibarra to another team for Nikola Whitfield at $7,531,195. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 4619983, "incoming_salary": 7531195, "max_incoming": 9489966, "matching_rule": "200% + $250,000 (outgoing at or below $9,096,000)", "apron_level": "over the tax line", "apron_salary_after": 204936794, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $4,619,983, $7,531,195, $9,489,966

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Atlanta
  2. --- Atlanta (2026-27) --- (apron salary $202,025,582, over the tax line)
  3. Atlanta outgoing salary = $4,619,983 (Marcus Ibarra $4,619,983)
  4. Atlanta incoming salary = $7,531,195 (Nikola Whitfield $7,531,195)
  5. Atlanta matching limit = $9,489,966 (200% + $250,000 (outgoing at or below $9,096,000))
  6. Atlanta hard-capped at the first apron = $209,015,000 (took back more than 100% of outgoing salary)
  7. Atlanta apron salary after the trade = $204,936,794
  8. Atlanta stays under its first apron hard cap = $4,078,206 ($209,015,000 - $204,936,794 of room to spare)
  9. Verdict: LEGAL
```


## Scenario 37 -- scenario_planning

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
Jaylen Rees             $3,612,689
Andre Brantley         $22,422,161
Devonte Petrov          $3,779,149
Terrance Boateng        $6,564,882
Micah Novak             $3,687,769
Andre Novak            $43,540,925
Nikola Marsh            $3,026,848
Goran Lindqvist         $3,831,883
Amari Kearns           $43,708,184
Nico Achiuwa           $27,466,600
Elijah Amadi           $15,107,837
Nico Nakamura          $22,915,305
Nico Brantley           $5,167,289
Kellen Vasquez          $3,759,184
Andre Jokubaitis        $7,626,306

Roster count: 15

We need to get under the second apron before the deadline. What are our options, and what are we giving up?
```

**Ground truth:** {"apron_salary": 216217011, "second_apron": 207824000, "overage": 8393011, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Elijah Amadi", "salary": 15107837, "surplus": 6714826}, {"player": "Andre Brantley", "salary": 22422161, "surplus": 14029150}, {"player": "Nico Nakamura", "salary": 22915305, "surplus": 14522294}, {"player": "Nico Achiuwa", "salary": 27466600, "surplus": 19073589}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $8,393,011

**Computation trace (the only figures you may use):**

```
  1. Houston apron salary = $216,217,011
  2. 2025-26 second apron = $207,824,000
  3. Amount over the second apron = $8,393,011
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Elijah Amadi alone clears the gap = $6,714,826 ($15,107,837 out against $8,393,011 of overage, assuming no salary comes back)
  7. Moving Andre Brantley alone clears the gap = $14,029,150 ($22,422,161 out against $8,393,011 of overage, assuming no salary comes back)
  8. Moving Nico Nakamura alone clears the gap = $14,522,294 ($22,915,305 out against $8,393,011 of overage, assuming no salary comes back)
  9. Moving Nico Achiuwa alone clears the gap = $19,073,589 ($27,466,600 out against $8,393,011 of overage, assuming no salary comes back)
```


## Scenario 38 -- tax_bill

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

CHICAGO -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Elijah Brantley,41149176,0,4
Zion Achiuwa,5952176,0,3
Rashad Kearns,18575391,0,4
Kellen Reddish,7602702,0,2
Kobe Duval,22747857,0,3
Cam Petrov,36914958,0,2
Dante Halvorsen,2137981,0,4
Tobias Beauchamp,5345779,0,2
Isaiah Beauchamp,15567541,0,4
Jalil Amadi,7329796,0,3
Amari Sabonis,5480728,0,3
Kobe Boateng,3445361,0,1
Micah Okoro,8241293,0,2

Roster count: 13

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 180490739, "tax_line": 170814000, "amount_over": 9676739, "is_repeater": false, "total": 15642293, "brackets": [{"index": 1, "amount": 5168000, "rate": 1.5, "owed": 7752000}, {"index": 2, "amount": 4508739, "rate": 1.75, "owed": 7890293}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $15,642,293, $9,676,739

**Computation trace (the only figures you may use):**

```
  1. Chicago tax salary = $180,490,739
  2. 2024-25 luxury tax line = $170,814,000
  3. Amount over the tax line = $9,676,739 ($180,490,739 - $170,814,000)
  4. Rate schedule: standard (2024-25) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $5,168,000 at $1.50 per dollar = $7,752,000
  6. Bracket 2: $4,508,739 at $1.75 per dollar = $7,890,293
  7. Total luxury tax owed = $15,642,293
  8. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 39 -- exception_eligibility

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Goran Ellington | $17,676,958 | -- | 4 |
| Jalil Vasquez | $8,307,226 | -- | 4 |
| Nikola Stavros | $10,343,706 | -- | 4 |
| Micah Kearns | $19,354,072 | -- | 3 |
| Dante Kearns | $15,681,432 | -- | 3 |
| Amari Duval | $3,097,746 | -- | 3 |
| Goran Amadi | $8,873,006 | -- | 2 |
| Devonte Cordero | $7,701,180 | -- | 3 |
| Goran Whitfield | $6,538,122 | -- | 3 |
| Brennan Kalinic | $9,903,608 | -- | 4 |
| Nico Kalinic | $30,520,592 | -- | 2 |
| Julian Amadi | $9,802,332 | -- | 4 |
| Zion Beauchamp | $54,126,450 | -- | 4 |
| Elijah Cordero | $4,113,544 | -- | 3 |

Roster count: 14

Can we sign Cam Whitfield for $4,958,308 using the taxpayer mid-level exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "taxpayer mid-level exception", "salary": 4958308, "hard_cap_triggered": "none", "apron_level": "over the first apron", "apron_salary_after": 210998282, "reasons": ["the signing would put New Orleans at $210,998,282, above its second apron hard cap of $207,824,000"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $4,958,308

**Computation trace (the only figures you may use):**

```
  1. New Orleans apron salary before signing = $206,039,974 (over the first apron)
  2. Proposed salary for Cam Whitfield = $4,958,308
  3. Exception: taxpayer mid-level exception
  4. taxpayer mid-level exception maximum = $5,685,000
  5. Room remaining within the exception = $726,692
  6. New Orleans apron salary after signing = $210,998,282
  7. Hard cap: second apron = $207,824,000
  8. VIOLATION -- hard cap exceeded = $3,174,282
  9. Verdict: ILLEGAL
```


