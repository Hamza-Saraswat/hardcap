# Writing batch 1

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

Write one JSON object per line to `/tmp/rexport/batch1_responses.jsonl`, nothing else in the file:

    {"id": 0, "response": "**Verdict: ILLEGAL.** ..."}

The `id` must match the scenario number below.

---

## Scenario 0 -- trade_legality

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
player,salary,unlikely_incentives,years_remaining
Corey Stavros,17255325,0,3
Zion Lindqvist,11517974,0,4
Zion Okoro,15156899,0,2
Terrance Ferreira,5553694,0,1
Santi Ellington,6040114,0,2
Kristaps Jokubaitis,4877875,0,3
Andre Ellington,26037250,0,2
Alperen Vasquez,6907680,0,4
Nikola Stavros,7076390,0,1
Cam Achiuwa,10103785,0,2
Devonte Nakamura,57736350,0,1
Nico Nakamura,39841324,0,3
Deni Stavros,8689521,0,4
Kellen Kearns,4358215,0,4

Roster count: 14

We're discussing a trade that sends Alperen Vasquez to another team for Santi Lindqvist at $6,559,211. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 6907680, "incoming_salary": 6559211, "max_incoming": 6907680, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 220803927, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $6,907,680, $6,559,211, $6,907,680

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Orlando
  2. --- Orlando (2026-27) --- (apron salary $221,152,396, over the first apron)
  3. Orlando outgoing salary = $6,907,680 (Alperen Vasquez $6,907,680)
  4. Orlando incoming salary = $6,559,211 (Santi Lindqvist $6,559,211)
  5. Orlando matching limit = $6,907,680 (100% of outgoing salary (team is over the first apron))
  6. Orlando apron salary after the trade = $220,803,927
  7. Verdict: LEGAL
```


## Scenario 1 -- apron_status

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
| Trey Kalinic | $57,736,350 | -- | 2 |
| Isaiah Ibarra | $13,362,652 | -- | 3 |
| Kristaps Reddish | $12,949,231 | -- | 1 |
| Amari Stavros | $5,472,969 | -- | 4 |
| Kristaps Boateng | $6,258,811 | -- | 3 |
| Malik Kalinic | $6,650,935 | -- | 1 |
| Julian Ellington | $7,142,179 | $1,933,334 | 1 |
| Corey Ferreira | $7,585,981 | -- | 3 |
| Rashad Petrov | $11,575,404 | -- | 1 |
| Luka Novak | $12,984,539 | $1,933,333 | 4 |
| Elijah Cordero | $13,190,836 | -- | 1 |
| Santi Nakamura | $17,388,935 | $1,933,333 | 2 |
| Malik Dumont | $9,331,757 | -- | 1 |
| Darnell Vasquez | $12,462,535 | -- | 2 |
| Micah Kalinic | $6,419,735 | -- | 1 |

Roster count: 15

Are we over the second apron? How much room do we have?
```

**Ground truth:** {"tax_salary": 200512849, "unlikely_incentives": 5800000, "apron_salary": 206312849, "apron_level": "over the tax line", "room_to_first_apron": 2702151, "room_to_second_apron": 15373151}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $206,312,849

**Computation trace (the only figures you may use):**

```
  1. Atlanta salaries plus likely incentives = $200,512,849
  2. Unlikely incentives = $5,800,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $206,312,849
  4. 2026-27 luxury tax line = $200,428,000
  5. 2026-27 first apron = $209,015,000
  6. 2026-27 second apron = $221,686,000
  7. Position: over the tax line
  8. Amount above the tax line = $5,884,849
  9. Room below the first apron = $2,702,151
  10. Room below the second apron = $15,373,151
```


## Scenario 2 -- scenario_planning

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
Isaiah Ibarra,7694748,0,3
Bogdan Jokubaitis,6798629,0,3
Cam Ellington,6361359,0,3
Bogdan Okoro,46733476,0,2
Devonte Amadi,7276165,0,4
Santi Osei,5021823,0,3
Kristaps Brantley,7158564,0,1
Terrance Rees,29255111,0,4
Alperen Cordero,7001433,0,4
Elijah Nakamura,13263340,0,1
Trey Stavros,15305228,0,2
Devonte Jokubaitis,3176792,0,1
Kobe Duval,8423169,0,3
Kristaps Kearns,51551674,0,2
Marcus Halvorsen,11199799,0,3

Roster count: 15

What's the cleanest path under the second apron from here?
```

**Ground truth:** {"apron_salary": 226221310, "second_apron": 207824000, "overage": 18397310, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Terrance Rees", "salary": 29255111, "surplus": 10857801}, {"player": "Bogdan Okoro", "salary": 46733476, "surplus": 28336166}, {"player": "Kristaps Kearns", "salary": 51551674, "surplus": 33154364}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $18,397,310

**Computation trace (the only figures you may use):**

```
  1. Atlanta apron salary = $226,221,310
  2. 2025-26 second apron = $207,824,000
  3. Amount over the second apron = $18,397,310
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Terrance Rees alone clears the gap = $10,857,801 ($29,255,111 out against $18,397,310 of overage, assuming no salary comes back)
  7. Moving Bogdan Okoro alone clears the gap = $28,336,166 ($46,733,476 out against $18,397,310 of overage, assuming no salary comes back)
  8. Moving Kristaps Kearns alone clears the gap = $33,154,364 ($51,551,674 out against $18,397,310 of overage, assuming no salary comes back)
```


## Scenario 3 -- apron_status

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
Terrance Brantley,17627805,0,4
Andre Osei,9290567,1666666,4
Dante Okoro,45919335,1666666,1
Corey Jokubaitis,6305644,0,2
Andre Ibarra,9146453,1666668,2
Kellen Lindqvist,7170741,0,3
Amari Petrov,9933920,0,4
Jaylen Stavros,54126450,0,2
Corey Lindqvist,5825836,0,3
Tobias Brantley,5191882,0,3
Amari Nakamura,5762144,0,4
Goran Rees,18984262,0,4
Amari Duval,8250776,0,1

Roster count: 13

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 203535815, "unlikely_incentives": 5000000, "apron_salary": 208535815, "apron_level": "over the second apron", "room_to_first_apron": -12590815, "room_to_second_apron": -711815}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $208,535,815

**Computation trace (the only figures you may use):**

```
  1. Atlanta salaries plus likely incentives = $203,535,815
  2. Unlikely incentives = $5,000,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $208,535,815
  4. 2025-26 luxury tax line = $187,895,000
  5. 2025-26 first apron = $195,945,000
  6. 2025-26 second apron = $207,824,000
  7. Position: over the second apron
  8. Amount above the tax line = $20,640,815
  9. Amount above the first apron = $12,590,815
  10. Amount above the second apron = $711,815
```


## Scenario 4 -- apron_status

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
Kellen Brantley,5987275,1100000,1
Trey Rees,5739007,1100000,4
Brennan Halvorsen,4697012,0,2
Brennan Boateng,5786126,0,4
Kellen Beauchamp,3824919,1100000,3
Darnell Jokubaitis,13793826,0,1
Marcus Reddish,2296001,0,4
Micah Achiuwa,4701410,0,1
Kobe Lindqvist,3107727,0,3
Zion Duval,6204543,0,2
Trey Whitfield,36349022,0,2
Nico Marsh,5468018,0,1
Devonte Ibarra,5247555,0,4
Brennan Petrov,34412252,0,2
Luka Kalinic,11145517,0,4

Roster count: 15

Are we over the second apron? How much room do we have?
```

**Ground truth:** {"tax_salary": 148760210, "unlikely_incentives": 3300000, "apron_salary": 152060210, "apron_level": "under the tax line", "room_to_first_apron": 43884790, "room_to_second_apron": 55763790}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $152,060,210

**Computation trace (the only figures you may use):**

```
  1. New Orleans salaries plus likely incentives = $148,760,210
  2. Unlikely incentives = $3,300,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $152,060,210
  4. 2025-26 luxury tax line = $187,895,000
  5. 2025-26 first apron = $195,945,000
  6. 2025-26 second apron = $207,824,000
  7. Position: under the tax line
  8. Room below the tax line = $35,834,790
  9. Room below the first apron = $43,884,790
  10. Room below the second apron = $55,763,790
```


## Scenario 5 -- trade_legality

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

CHARLOTTE -- 2024-25 CAP SHEET
Elijah Novak           $40,483,226
Dante Jokubaitis        $6,164,227
Jalil Ibarra            $2,275,876
Isaiah Reddish          $7,166,920
Corey Halvorsen        $24,117,034
Andre Okoro            $25,998,370
Kellen Kearns           $4,507,543
Bogdan Novak            $5,459,156
Corey Ferreira          $6,877,563
Elijah Marsh           $23,189,762
Julian Kearns           $8,103,224
Amari Whitfield        $38,086,619
Goran Petrov            $3,158,206
Brennan Brantley        $3,903,289

Roster count: 14

We're discussing a trade that sends Elijah Novak to another team for Luka Reddish at $31,155,080. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 40483226, "incoming_salary": 31155080, "max_incoming": 40483226, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 190162869, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $40,483,226, $31,155,080, $40,483,226

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Charlotte
  2. --- Charlotte (2024-25) --- (apron salary $199,491,015, over the second apron)
  3. Charlotte outgoing salary = $40,483,226 (Elijah Novak $40,483,226)
  4. Charlotte incoming salary = $31,155,080 (Luka Reddish $31,155,080)
  5. Charlotte matching limit = $40,483,226 (100% of outgoing salary (team is over the first apron))
  6. Charlotte apron salary after the trade = $190,162,869
  7. Verdict: LEGAL
```


## Scenario 6 -- scenario_planning

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

ATLANTA -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Trey Petrov,41531341,0,1
Santi Okoro,11985022,0,1
Corey Brantley,20731604,0,2
Isaiah Ellington,5756130,0,2
Corey Rees,5721386,0,2
Marcus Vasquez,22095666,0,4
Darnell Achiuwa,4910166,0,2
Nikola Reddish,2794455,0,4
Elijah Boateng,7080953,0,4
Micah Brantley,10493279,0,2
Andre Stavros,6856439,0,2
Cam Nakamura,6591323,0,4
Alperen Achiuwa,5299236,0,4
Devonte Kearns,38260939,0,1
Bogdan Kearns,4015672,0,1

Roster count: 15

What's the cleanest path under the second apron from here?
```

**Ground truth:** {"apron_salary": 194123611, "second_apron": 188931000, "overage": 5192611, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Alperen Achiuwa", "salary": 5299236, "surplus": 106625}, {"player": "Corey Rees", "salary": 5721386, "surplus": 528775}, {"player": "Isaiah Ellington", "salary": 5756130, "surplus": 563519}, {"player": "Cam Nakamura", "salary": 6591323, "surplus": 1398712}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $5,192,611

**Computation trace (the only figures you may use):**

```
  1. Atlanta apron salary = $194,123,611
  2. 2024-25 second apron = $188,931,000
  3. Amount over the second apron = $5,192,611
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Alperen Achiuwa alone clears the gap = $106,625 ($5,299,236 out against $5,192,611 of overage, assuming no salary comes back)
  7. Moving Corey Rees alone clears the gap = $528,775 ($5,721,386 out against $5,192,611 of overage, assuming no salary comes back)
  8. Moving Isaiah Ellington alone clears the gap = $563,519 ($5,756,130 out against $5,192,611 of overage, assuming no salary comes back)
  9. Moving Cam Nakamura alone clears the gap = $1,398,712 ($6,591,323 out against $5,192,611 of overage, assuming no salary comes back)
```


## Scenario 7 -- exception_eligibility

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
Terrance Kearns,7708185,0,1
Zion Duval,2582688,0,1
Cam Dumont,4482683,0,3
Malik Beauchamp,3858363,0,4
Cam Jokubaitis,38615554,0,1
Jaylen Beauchamp,5285564,0,3
Rashad Rees,7095984,0,1
Zion Jokubaitis,9304100,0,2
Micah Lindqvist,6106913,0,4
Devonte Vasquez,37362878,0,4
Corey Osei,26423484,0,3
Goran Nakamura,4898040,0,2
Jaylen Ellington,8487216,0,1
Nikola Ferreira,7611377,0,4
Santi Nakamura,6435581,0,1

Roster count: 15

Can we sign Brennan Kearns for $2,305,708 using the minimum salary exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "minimum salary exception", "salary": 2305708, "hard_cap_triggered": "none", "apron_level": "over the tax line", "apron_salary_after": 178564318, "reasons": ["Miami already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $2,305,708

**Computation trace (the only figures you may use):**

```
  1. Miami apron salary before signing = $176,258,610 (over the tax line)
  2. Proposed salary for Brennan Kearns = $2,305,708
  3. Exception: minimum salary exception
  4. Miami apron salary after signing = $178,564,318
  5. VIOLATION -- roster is full (15-man limit reached)
  6. Verdict: ILLEGAL
```


## Scenario 8 -- tax_bill

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

SAN ANTONIO -- 2026-27 CAP SHEET
Kobe Nakamura           $7,301,219
Brennan Sabonis         $8,143,269
Nikola Duval            $5,630,240
Bogdan Ellington        $8,943,147
Malik Jokubaitis       $22,605,445
Jalil Novak             $8,520,834
Isaiah Ibarra           $4,632,834
Goran Marsh             $7,428,466
Marcus Duval           $10,855,584
Kellen Vasquez          $7,970,734
Devonte Nakamura        $4,235,265
Dante Reddish           $5,677,069
Tobias Halvorsen        $7,051,315
Zion Reddish           $57,736,350
Micah Halvorsen        $47,184,366

Roster count: 15
Repeater taxpayer: yes

Ownership wants the tax number. What do we owe, and how does it break down?
```

**Ground truth:** {"tax_salary": 213916137, "tax_line": 200428000, "amount_over": 13488137, "is_repeater": true, "total": 45380754, "brackets": [{"index": 1, "amount": 6064000, "rate": 3.0, "owed": 18192000}, {"index": 2, "amount": 6064000, "rate": 3.25, "owed": 19708000}, {"index": 3, "amount": 1360137, "rate": 5.5, "owed": 7480754}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $45,380,754, $13,488,137

**Computation trace (the only figures you may use):**

```
  1. San Antonio tax salary = $213,916,137
  2. 2026-27 luxury tax line = $200,428,000
  3. Amount over the tax line = $13,488,137 ($213,916,137 - $200,428,000)
  4. Rate schedule: repeater (2026-27) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $6,064,000 at $3.00 per dollar = $18,192,000
  6. Bracket 2: $6,064,000 at $3.25 per dollar = $19,708,000
  7. Bracket 3: $1,360,137 at $5.50 per dollar = $7,480,754
  8. Total luxury tax owed = $45,380,754
  9. Repeater status applies (paid the tax in 3 of the prior 4 seasons)
  10. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 9 -- trade_legality

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
| Amari Duval | $24,570,814 | -- | 2 |
| Tobias Dumont | $2,487,445 | -- | 2 |
| Dante Duval | $6,909,530 | -- | 1 |
| Deni Lindqvist | $22,192,879 | -- | 2 |
| Malik Lindqvist | $7,224,421 | -- | 4 |
| Terrance Brantley | $50,768,363 | -- | 1 |
| Deni Nakamura | $9,160,719 | -- | 1 |
| Kellen Brantley | $42,835,572 | -- | 2 |
| Brennan Kearns | $22,568,948 | -- | 4 |
| Nico Boateng | $5,430,984 | -- | 1 |
| Kellen Osei | $7,305,096 | -- | 1 |
| Deni Reddish | $4,575,792 | -- | 4 |
| Dante Vasquez | $7,129,063 | -- | 1 |
| Kristaps Ferreira | $6,495,294 | -- | 1 |
| Goran Beauchamp | $4,727,582 | -- | 1 |

Roster count: 15

We're discussing a trade that sends Kristaps Ferreira to another team for Marcus Halvorsen at $4,690,749. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 6495294, "incoming_salary": 4690749, "max_incoming": 6495294, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 222577957, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $6,495,294, $4,690,749, $6,495,294

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Toronto
  2. --- Toronto (2026-27) --- (apron salary $224,382,502, over the second apron)
  3. Toronto outgoing salary = $6,495,294 (Kristaps Ferreira $6,495,294)
  4. Toronto incoming salary = $4,690,749 (Marcus Halvorsen $4,690,749)
  5. Toronto matching limit = $6,495,294 (100% of outgoing salary (team is over the first apron))
  6. Toronto apron salary after the trade = $222,577,957
  7. Verdict: LEGAL
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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Cam Dumont | $20,861,446 | -- | 1 |
| Devonte Ellington | $27,643,896 | -- | 3 |
| Kristaps Dumont | $4,036,581 | -- | 1 |
| Kristaps Ibarra | $2,908,878 | -- | 1 |
| Deni Halvorsen | $5,789,100 | -- | 2 |
| Kobe Boateng | $5,164,503 | -- | 1 |
| Trey Dumont | $6,475,203 | -- | 4 |
| Jaylen Dumont | $8,121,245 | -- | 2 |
| Kobe Achiuwa | $39,911,206 | -- | 1 |
| Alperen Nakamura | $16,494,650 | -- | 1 |
| Kristaps Brantley | $5,924,896 | -- | 1 |
| Amari Cordero | $3,170,229 | -- | 4 |
| Isaiah Duval | $7,032,805 | -- | 4 |
| Kobe Duval | $45,557,453 | -- | 3 |

Roster count: 14

We're discussing a trade that sends Isaiah Duval and Kobe Boateng to another team for Brennan Reddish at $13,987,983. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 12197308, "incoming_salary": 13987983, "max_incoming": 12197308, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 200882766, "hard_cap_triggered": "none", "violations": ["New Orleans: second-apron aggregation ban -- New Orleans is over the second apron ($199,092,091 vs $188,931,000) and may not combine 2 salaries in one trade", "New Orleans: salary matching -- New Orleans takes back $13,987,983 but may only absorb $12,197,308 under 100% of outgoing salary (team is over the first apron) -- over by $1,790,675"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $12,197,308, $13,987,983, $12,197,308

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: New Orleans
  2. --- New Orleans (2024-25) --- (apron salary $199,092,091, over the second apron)
  3. New Orleans outgoing salary = $12,197,308 (Isaiah Duval $7,032,805, Kobe Boateng $5,164,503)
  4. New Orleans incoming salary = $13,987,983 (Brennan Reddish $13,987,983)
  5. VIOLATION -- second-apron aggregation ban (New Orleans is over the second apron ($199,092,091 vs $188,931,000) and may not combine 2 salaries in one trade)
  6. New Orleans matching limit = $12,197,308 (100% of outgoing salary (team is over the first apron))
  7. VIOLATION -- salary matching (New Orleans takes back $13,987,983 but may only absorb $12,197,308 under 100% of outgoing salary (team is over the first apron) -- over by $1,790,675)
  8. New Orleans apron salary after the trade = $200,882,766
  9. Verdict: ILLEGAL
```


## Scenario 11 -- trade_legality

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
player,salary,unlikely_incentives,years_remaining
Zion Boateng,2660871,0,2
Elijah Amadi,39980841,0,1
Luka Kearns,27202970,0,1
Kobe Ellington,3221624,0,1
Luka Achiuwa,13539314,0,3
Kobe Halvorsen,8063461,0,3
Nikola Jokubaitis,2553751,0,4
Darnell Reddish,7214434,0,4
Trey Duval,3477700,0,2
Jalil Duval,8870054,0,1
Bogdan Lindqvist,36349625,0,3
Jaylen Petrov,6309811,0,3
Zion Achiuwa,18095320,0,1

Roster count: 13

We're discussing a trade that sends Elijah Amadi and Bogdan Lindqvist to another team for Tobias Rees at $102,566,716. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 76330466, "incoming_salary": 102566716, "max_incoming": 95663082, "matching_rule": "125% + $250,000 (outgoing above $29,974,000)", "apron_level": "over the tax line", "apron_salary_after": 203776026, "hard_cap_triggered": "first apron", "violations": ["Utah: salary matching -- Utah takes back $102,566,716 but may only absorb $95,663,082 under 125% + $250,000 (outgoing above $29,974,000) -- over by $6,903,634", "Utah: hard cap exceeded -- Utah would sit at $203,776,026, above its first apron hard cap of $178,132,000 -- over by $25,644,026"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $76,330,466, $102,566,716, $95,663,082

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Utah
  2. --- Utah (2024-25) --- (apron salary $177,539,776, over the tax line)
  3. Utah outgoing salary = $76,330,466 (Elijah Amadi $39,980,841, Bogdan Lindqvist $36,349,625)
  4. Utah incoming salary = $102,566,716 (Tobias Rees $102,566,716)
  5. Utah matching limit = $95,663,082 (125% + $250,000 (outgoing above $29,974,000))
  6. VIOLATION -- salary matching (Utah takes back $102,566,716 but may only absorb $95,663,082 under 125% + $250,000 (outgoing above $29,974,000) -- over by $6,903,634)
  7. Utah hard-capped at the first apron = $178,132,000 (took back more than 100% of outgoing salary)
  8. Utah hard-capped at the second apron = $188,931,000 (aggregated two or more salaries in one trade)
  9. Two hard caps triggered -- the tighter one governs = $178,132,000
  10. Utah apron salary after the trade = $203,776,026
  11. VIOLATION -- hard cap exceeded (Utah would sit at $203,776,026, above its first apron hard cap of $178,132,000 -- over by $25,644,026)
  12. Verdict: ILLEGAL
```


## Scenario 12 -- buyout_market

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
player,salary,unlikely_incentives,years_remaining
Cam Sabonis,3212209,0,2
Malik Ibarra,51408946,0,4
Terrance Beauchamp,8937056,0,3
Isaiah Sabonis,7078917,0,1
Nikola Brantley,7027844,0,1
Jalil Beauchamp,4551553,0,3
Darnell Kearns,4418544,0,2
Nikola Ellington,8970892,0,4
Dante Kearns,7054022,0,1
Cam Amadi,3043867,0,1
Jaylen Ferreira,26316096,0,4
Malik Osei,2966462,0,1
Dante Brantley,7642830,0,4
Kellen Novak,9033566,0,4
Andre Kalinic,54126450,0,1

Roster count: 15

Santi Okoro is about to be bought out -- he was making $13,200,000 before the waiver. Can we sign him?
```

**Ground truth:** {"allowed": true, "pre_waiver_salary": 13200000, "non_taxpayer_mle": 14104000, "apron_level": "over the first apron", "reason": "the player's pre-waiver salary of $13,200,000 did not exceed the non-taxpayer mid-level, so Orlando may sign him despite being over the first apron"}

**Verdict:** ALLOWED

**Required figures (must all appear):** $13,200,000, $14,104,000

**Computation trace (the only figures you may use):**

```
  1. Orlando apron status = $205,789,254 (over the first apron)
  2. Player's pre-waiver salary = $13,200,000
  3. 2025-26 non-taxpayer mid-level = $14,104,000
  4. Allowed (the player's pre-waiver salary of $13,200,000 did not exceed the non-taxpayer mid-level, so Orlando may sign him despite being over the first apron)
```


## Scenario 13 -- buyout_market

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
Nico Novak             $10,569,879
Trey Amadi             $54,126,450
Jalil Boateng           $7,626,416
Devonte Marsh           $9,941,642
Kellen Beauchamp       $10,448,607
Tobias Dumont           $9,086,308
Malik Jokubaitis       $17,334,804
Jalil Ferreira          $5,625,127
Julian Novak           $16,975,203
Marcus Rees            $12,120,330
Deni Rees               $8,386,463
Amari Ibarra           $10,851,402
Dante Novak            $27,226,575
Andre Dumont            $3,405,858

Roster count: 14

Deni Ibarra is about to be bought out -- he was making $35,400,000 before the waiver. Can we sign him?
```

**Ground truth:** {"allowed": false, "pre_waiver_salary": 35400000, "non_taxpayer_mle": 14104000, "apron_level": "over the first apron", "reason": "Toronto is over the first apron and may not sign a player waived during the regular season whose pre-waiver salary ($35,400,000) exceeded the non-taxpayer mid-level ($14,104,000)"}

**Verdict:** NOT ALLOWED

**Required figures (must all appear):** $35,400,000, $14,104,000

**Computation trace (the only figures you may use):**

```
  1. Toronto apron status = $203,725,064 (over the first apron)
  2. Player's pre-waiver salary = $35,400,000
  3. 2025-26 non-taxpayer mid-level = $14,104,000
  4. VIOLATION -- buyout-market ban (Toronto is over the first apron and may not sign a player waived during the regular season whose pre-waiver salary ($35,400,000) exceeded the non-taxpayer mid-level ($14,104,000))
```


## Scenario 14 -- exception_survey

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

MEMPHIS -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Cam Nakamura,2810147,0,1
Elijah Vasquez,5315885,0,4
Jalil Reddish,29476625,0,3
Kristaps Sabonis,8606982,0,2
Tobias Whitfield,4119405,0,2
Kellen Rees,8751828,0,3
Kobe Beauchamp,51808031,0,4
Trey Kalinic,18259546,0,1
Kristaps Amadi,3774184,0,1
Isaiah Novak,7813172,0,3
Darnell Ellington,47498349,0,4
Bogdan Ibarra,5653048,0,1
Nico Duval,13908171,0,4
Rashad Ferreira,13283693,0,3

Roster count: 14

What signing exceptions do we still have available, and what does using each one cost us?
```

**Ground truth:** {"apron_level": "over the second apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the second apron -- no mid-level of any kind", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Memphis apron salary = $221,079,066 (over the second apron)
  2. 2025-26 first apron = $195,945,000
  3. 2025-26 second apron = $207,824,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: unavailable (unavailable over the second apron -- no mid-level of any kind)
  6. bi-annual exception: unavailable (unavailable over the first apron)
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

MIAMI -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Santi Marsh,8529190,0,4
Santi Okoro,10932832,0,1
Nico Lindqvist,11117203,0,1
Zion Dumont,3008688,0,4
Nico Achiuwa,8604787,0,3
Corey Novak,10841783,0,4
Deni Beauchamp,7727605,0,2
Kellen Brantley,15632866,0,1
Devonte Ellington,7427845,0,4
Trey Vasquez,7993851,0,2
Trey Nakamura,48984062,0,2
Santi Cordero,7128110,0,4
Zion Rees,49205800,0,4
Malik Achiuwa,8840127,0,4

Roster count: 14

We're discussing a trade that sends Trey Nakamura to another team for Jalil Lindqvist at $40,940,761. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 48984062, "incoming_salary": 40940761, "max_incoming": 48984062, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 197931448, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $48,984,062, $40,940,761, $48,984,062

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Miami
  2. --- Miami (2024-25) --- (apron salary $205,974,749, over the second apron)
  3. Miami outgoing salary = $48,984,062 (Trey Nakamura $48,984,062)
  4. Miami incoming salary = $40,940,761 (Jalil Lindqvist $40,940,761)
  5. Miami matching limit = $48,984,062 (100% of outgoing salary (team is over the first apron))
  6. Miami apron salary after the trade = $197,931,448
  7. Verdict: LEGAL
```


## Scenario 16 -- stretch_provision

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

If we waive and stretch Deni Petrov -- $89,800,000 left over 1 year -- what does the dead money look like, and is it even allowed?
```

**Ground truth:** {"legal": false, "remaining_salary": 89800000, "years_remaining": 1, "stretch_years": 3, "annual_dead_money": 29933333, "existing_stretched": 14700000, "limit": 21088200, "givebacks_required": 70635399, "reason": "the stretch is not legal as structured: $44,633,333 of dead money would exceed the $21,088,200 ceiling by $23,545,133 per season. The player would have to give back roughly $70,635,399 for the waiver to work"}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $29,933,333, $21,088,200

**Computation trace (the only figures you may use):**

```
  1. Salary remaining on the contract = $89,800,000
  2. Years remaining (1)
  3. Stretch period (2 x 1 + 1 = 3 seasons)
  4. Annual dead money if stretched = $29,933,333 ($89,800,000 / 3)
  5. Dead money already stretched = $14,700,000
  6. Total stretched dead money = $44,633,333
  7. Limit (15% of the 2024-25 cap) = $21,088,200 (15% x $140,588,000)
  8. VIOLATION -- exceeds the dead-money ceiling = $23,545,133
  9. Approximate giveback required = $70,635,399 ($23,545,133 x 3 seasons)
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

HOUSTON -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Jalil Okoro,4859290,0,3
Julian Ellington,12235587,0,2
Elijah Duval,3155105,0,3
Marcus Achiuwa,7969652,0,4
Terrance Whitfield,44948866,0,2
Alperen Whitfield,10632965,0,1
Kobe Beauchamp,10494533,0,4
Malik Beauchamp,3832367,0,1
Luka Novak,3435700,0,4
Elijah Novak,9066393,0,2
Deni Petrov,44075899,0,1
Kristaps Duval,12336279,0,2
Brennan Lindqvist,8276877,0,4
Bogdan Sabonis,8054923,0,4
Corey Ibarra,6984837,0,4

Roster count: 15
Repeater taxpayer: yes

What's our luxury tax bill this season? Walk me through the brackets.
```

**Ground truth:** {"tax_salary": 190359273, "tax_line": 170814000, "amount_over": 19545273, "is_repeater": true, "total": 62395410, "brackets": [{"index": 1, "amount": 5168000, "rate": 2.5, "owed": 12920000}, {"index": 2, "amount": 5168000, "rate": 2.75, "owed": 14212000}, {"index": 3, "amount": 5168000, "rate": 3.5, "owed": 18088000}, {"index": 4, "amount": 4041273, "rate": 4.25, "owed": 17175410}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $62,395,410, $19,545,273

**Computation trace (the only figures you may use):**

```
  1. Houston tax salary = $190,359,273
  2. 2024-25 luxury tax line = $170,814,000
  3. Amount over the tax line = $19,545,273 ($190,359,273 - $170,814,000)
  4. Rate schedule: repeater (2024-25) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $5,168,000 at $2.50 per dollar = $12,920,000
  6. Bracket 2: $5,168,000 at $2.75 per dollar = $14,212,000
  7. Bracket 3: $5,168,000 at $3.50 per dollar = $18,088,000
  8. Bracket 4: $4,041,273 at $4.25 per dollar = $17,175,410
  9. Total luxury tax owed = $62,395,410
  10. Repeater status applies (paid the tax in 3 of the prior 4 seasons)
  11. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
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

SACRAMENTO -- 2026-27 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Alperen Beauchamp,11639339,0,1
Andre Okoro,4237312,0,4
Rashad Whitfield,38403659,0,3
Goran Beauchamp,57736350,0,4
Brennan Petrov,10737997,0,2
Nico Beauchamp,7607091,0,2
Nico Amadi,22832761,0,1
Elijah Okoro,5649706,0,4
Elijah Amadi,4333947,0,1
Isaiah Vasquez,4908305,0,4
Zion Stavros,6908895,0,2
Rashad Duval,11151575,0,4
Isaiah Brantley,11994055,0,2
Goran Sabonis,10995899,0,2
Kristaps Whitfield,7269992,0,1

Roster count: 15
Repeater taxpayer: yes

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 216406883, "tax_line": 200428000, "amount_over": 15978883, "is_repeater": true, "total": 59079856, "brackets": [{"index": 1, "amount": 6064000, "rate": 3.0, "owed": 18192000}, {"index": 2, "amount": 6064000, "rate": 3.25, "owed": 19708000}, {"index": 3, "amount": 3850883, "rate": 5.5, "owed": 21179856}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $59,079,856, $15,978,883

**Computation trace (the only figures you may use):**

```
  1. Sacramento tax salary = $216,406,883
  2. 2026-27 luxury tax line = $200,428,000
  3. Amount over the tax line = $15,978,883 ($216,406,883 - $200,428,000)
  4. Rate schedule: repeater (2026-27) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $6,064,000 at $3.00 per dollar = $18,192,000
  6. Bracket 2: $6,064,000 at $3.25 per dollar = $19,708,000
  7. Bracket 3: $3,850,883 at $5.50 per dollar = $21,179,856
  8. Total luxury tax owed = $59,079,856
  9. Repeater status applies (paid the tax in 3 of the prior 4 seasons)
  10. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 19 -- scenario_planning

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
Corey Jokubaitis        $21,845,034
Luka Jokubaitis          $7,459,184
Brennan Whitfield        $7,760,916
Zion Amadi               $8,399,205
Jalil Cordero            $6,317,936
Corey Marsh             $11,158,855
Rashad Brantley          $4,818,182
Jalil Novak             $49,205,800
Jalil Vasquez            $9,610,535
Dante Halvorsen         $24,655,626
Kellen Halvorsen        $11,207,978
Elijah Beauchamp        $10,781,046
Marcus Ibarra           $11,330,951
Terrance Vasquez        $17,333,485
Nikola Petrov           $10,054,233

Roster count: 15

We need to get under the second apron before the deadline. What are our options, and what are we giving up?
```

**Ground truth:** {"apron_salary": 211938966, "second_apron": 188931000, "overage": 23007966, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Dante Halvorsen", "salary": 24655626, "surplus": 1647660}, {"player": "Jalil Novak", "salary": 49205800, "surplus": 26197834}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $23,007,966

**Computation trace (the only figures you may use):**

```
  1. Toronto apron salary = $211,938,966
  2. 2024-25 second apron = $188,931,000
  3. Amount over the second apron = $23,007,966
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Dante Halvorsen alone clears the gap = $1,647,660 ($24,655,626 out against $23,007,966 of overage, assuming no salary comes back)
  7. Moving Jalil Novak alone clears the gap = $26,197,834 ($49,205,800 out against $23,007,966 of overage, assuming no salary comes back)
```


## Scenario 20 -- apron_status

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
| Kobe Petrov | $49,844,729 | -- | 4 |
| Julian Dumont | $5,136,206 | $1,633,333 | 4 |
| Nico Petrov | $3,282,584 | -- | 1 |
| Deni Brantley | $5,420,046 | -- | 2 |
| Rashad Ibarra | $43,141,632 | -- | 3 |
| Nico Kearns | $6,880,474 | $1,633,333 | 4 |
| Bogdan Ferreira | $4,674,642 | -- | 4 |
| Rashad Reddish | $21,761,116 | $1,633,334 | 2 |
| Alperen Marsh | $19,014,178 | -- | 1 |
| Elijah Ibarra | $11,180,596 | -- | 1 |
| Bogdan Dumont | $6,399,869 | -- | 3 |
| Darnell Duval | $5,769,343 | -- | 4 |
| Alperen Whitfield | $6,552,242 | -- | 1 |
| Amari Nakamura | $6,823,474 | -- | 4 |
| Isaiah Kalinic | $6,803,572 | -- | 3 |

Roster count: 15

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 202684703, "unlikely_incentives": 4900000, "apron_salary": 207584703, "apron_level": "over the tax line", "room_to_first_apron": 1430297, "room_to_second_apron": 14101297}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $207,584,703

**Computation trace (the only figures you may use):**

```
  1. Houston salaries plus likely incentives = $202,684,703
  2. Unlikely incentives = $4,900,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $207,584,703
  4. 2026-27 luxury tax line = $200,428,000
  5. 2026-27 first apron = $209,015,000
  6. 2026-27 second apron = $221,686,000
  7. Position: over the tax line
  8. Amount above the tax line = $7,156,703
  9. Room below the first apron = $1,430,297
  10. Room below the second apron = $14,101,297
```


## Scenario 21 -- trade_legality

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

CHICAGO -- 2025-26 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Cam Ibarra | $2,296,001 | -- | 3 |
| Amari Ferreira | $2,728,150 | -- | 3 |
| Terrance Reddish | $2,296,001 | -- | 4 |
| Zion Cordero | $8,141,256 | -- | 1 |
| Nikola Brantley | $4,531,105 | -- | 2 |
| Julian Amadi | $3,707,866 | -- | 4 |
| Jalil Cordero | $18,997,292 | -- | 3 |
| Alperen Reddish | $6,303,828 | -- | 4 |
| Andre Whitfield | $3,269,864 | -- | 2 |
| Nikola Ferreira | $4,494,865 | -- | 3 |
| Andre Stavros | $39,925,720 | -- | 1 |
| Malik Halvorsen | $2,374,706 | -- | 1 |
| Alperen Jokubaitis | $40,195,793 | -- | 1 |

Roster count: 13

We're discussing a trade that sends Julian Amadi and Zion Cordero to another team for Micah Amadi at $16,949,667. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 11849122, "incoming_salary": 16949667, "max_incoming": 20376122, "matching_rule": "outgoing + $8,527,000 (middle band)", "apron_level": "under the tax line", "apron_salary_after": 144362992, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $11,849,122, $16,949,667, $20,376,122

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Chicago
  2. --- Chicago (2025-26) --- (apron salary $139,262,447, under the tax line)
  3. Chicago outgoing salary = $11,849,122 (Julian Amadi $3,707,866, Zion Cordero $8,141,256)
  4. Chicago incoming salary = $16,949,667 (Micah Amadi $16,949,667)
  5. Chicago matching limit = $20,376,122 (outgoing + $8,527,000 (middle band))
  6. Chicago hard-capped at the first apron = $195,945,000 (took back more than 100% of outgoing salary)
  7. Chicago hard-capped at the second apron = $207,824,000 (aggregated two or more salaries in one trade)
  8. Two hard caps triggered -- the tighter one governs = $195,945,000
  9. Chicago apron salary after the trade = $144,362,992
  10. Chicago stays under its first apron hard cap = $51,582,008 ($195,945,000 - $144,362,992 of room to spare)
  11. Verdict: LEGAL
```


## Scenario 22 -- tax_bill

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

CHICAGO -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Cam Osei,7275464,0,4
Bogdan Whitfield,25402695,0,1
Alperen Reddish,5437169,0,1
Amari Jokubaitis,54126450,0,2
Kristaps Novak,7329446,0,3
Dante Jokubaitis,6182595,0,2
Malik Brantley,7729157,0,3
Luka Beauchamp,25700806,0,1
Rashad Lindqvist,4778110,0,2
Bogdan Nakamura,11638818,0,3
Alperen Nakamura,6402708,0,1
Kellen Halvorsen,11401220,0,4
Kristaps Nakamura,4359996,0,2
Julian Duval,9697030,0,4
Nico Okoro,4069284,0,4

Roster count: 15

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 191530948, "tax_line": 187895000, "amount_over": 3635948, "is_repeater": false, "total": 3635948, "brackets": [{"index": 1, "amount": 3635948, "rate": 1.0, "owed": 3635948}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $3,635,948, $3,635,948

**Computation trace (the only figures you may use):**

```
  1. Chicago tax salary = $191,530,948
  2. 2025-26 luxury tax line = $187,895,000
  3. Amount over the tax line = $3,635,948 ($191,530,948 - $187,895,000)
  4. Rate schedule: standard (2025-26) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $3,635,948 at $1.00 per dollar = $3,635,948
  6. Total luxury tax owed = $3,635,948
  7. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 23 -- apron_status

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
Jaylen Sabonis            $13,569,696   (+$1,600,000 unlikely)
Luka Sabonis              $16,550,612
Kristaps Reddish          $10,449,413   (+$1,600,000 unlikely)
Alperen Reddish            $9,313,886
Kobe Nakamura             $11,868,915
Tobias Marsh               $6,399,790
Terrance Kalinic           $8,724,724
Santi Cordero              $8,917,206
Kristaps Jokubaitis       $57,736,350
Isaiah Kalinic             $8,992,996
Zion Ibarra               $23,359,476
Nico Achiuwa              $10,586,415
Kellen Ibarra              $5,665,792
Brennan Vasquez            $5,735,363   (+$1,600,000 unlikely)
Nikola Ibarra              $6,974,260

Roster count: 15

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 204844894, "unlikely_incentives": 4800000, "apron_salary": 209644894, "apron_level": "over the first apron", "room_to_first_apron": -629894, "room_to_second_apron": 12041106}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $209,644,894

**Computation trace (the only figures you may use):**

```
  1. Utah salaries plus likely incentives = $204,844,894
  2. Unlikely incentives = $4,800,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $209,644,894
  4. 2026-27 luxury tax line = $200,428,000
  5. 2026-27 first apron = $209,015,000
  6. 2026-27 second apron = $221,686,000
  7. Position: over the first apron
  8. Amount above the tax line = $9,216,894
  9. Amount above the first apron = $629,894
  10. Room below the second apron = $12,041,106
```


## Scenario 24 -- trade_legality

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

CHARLOTTE -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Rashad Okoro,3877610,0,3
Micah Lindqvist,12452393,0,4
Jalil Amadi,31728270,0,4
Deni Brantley,5492852,0,3
Bogdan Okoro,24675715,0,1
Trey Sabonis,6914855,0,1
Darnell Lindqvist,2444776,0,2
Elijah Kearns,20379073,0,3
Julian Cordero,4293246,0,1
Alperen Kalinic,7536564,0,1
Darnell Osei,9398856,0,4
Deni Kearns,3452262,0,4
Luka Novak,6079785,0,3
Amari Boateng,37800953,0,3
Jaylen Lindqvist,6007734,0,4

Roster count: 15

We're discussing a trade that sends Micah Lindqvist to another team for Nikola Ibarra at $13,842,874. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 12452393, "incoming_salary": 13842874, "max_incoming": 12452393, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 183925425, "hard_cap_triggered": "none", "violations": ["Charlotte: salary matching -- Charlotte takes back $13,842,874 but may only absorb $12,452,393 under 100% of outgoing salary (team is over the first apron) -- over by $1,390,481"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $12,452,393, $13,842,874, $12,452,393

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Charlotte
  2. --- Charlotte (2024-25) --- (apron salary $182,534,944, over the first apron)
  3. Charlotte outgoing salary = $12,452,393 (Micah Lindqvist $12,452,393)
  4. Charlotte incoming salary = $13,842,874 (Nikola Ibarra $13,842,874)
  5. Charlotte matching limit = $12,452,393 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (Charlotte takes back $13,842,874 but may only absorb $12,452,393 under 100% of outgoing salary (team is over the first apron) -- over by $1,390,481)
  7. Charlotte apron salary after the trade = $183,925,425
  8. Verdict: ILLEGAL
```


## Scenario 25 -- scenario_planning

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

CHICAGO -- 2026-27 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Nikola Marsh,8434869,0,4
Santi Achiuwa,22605404,0,2
Santi Okoro,11255506,0,3
Luka Ibarra,21912524,0,4
Corey Rees,6158571,0,3
Nico Jokubaitis,10065598,0,2
Jaylen Petrov,5986311,0,2
Bogdan Cordero,8833069,0,3
Tobias Ibarra,57736350,0,2
Marcus Osei,27943553,0,3
Goran Cordero,12216812,0,3
Kobe Sabonis,14247502,0,2
Micah Petrov,6545261,0,2
Darnell Beauchamp,12438531,0,2
Malik Vasquez,10993668,0,1

Roster count: 15

Ownership wants us out of the second apron. Walk me through how we do it.
```

**Ground truth:** {"apron_salary": 237373529, "second_apron": 221686000, "overage": 15687529, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Luka Ibarra", "salary": 21912524, "surplus": 6224995}, {"player": "Santi Achiuwa", "salary": 22605404, "surplus": 6917875}, {"player": "Marcus Osei", "salary": 27943553, "surplus": 12256024}, {"player": "Tobias Ibarra", "salary": 57736350, "surplus": 42048821}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $15,687,529

**Computation trace (the only figures you may use):**

```
  1. Chicago apron salary = $237,373,529
  2. 2026-27 second apron = $221,686,000
  3. Amount over the second apron = $15,687,529
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Luka Ibarra alone clears the gap = $6,224,995 ($21,912,524 out against $15,687,529 of overage, assuming no salary comes back)
  7. Moving Santi Achiuwa alone clears the gap = $6,917,875 ($22,605,404 out against $15,687,529 of overage, assuming no salary comes back)
  8. Moving Marcus Osei alone clears the gap = $12,256,024 ($27,943,553 out against $15,687,529 of overage, assuming no salary comes back)
  9. Moving Tobias Ibarra alone clears the gap = $42,048,821 ($57,736,350 out against $15,687,529 of overage, assuming no salary comes back)
```


## Scenario 26 -- exception_survey

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

PORTLAND -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Tobias Achiuwa,4498705,0,2
Marcus Reddish,6167689,0,3
Corey Kearns,5376653,0,3
Nikola Amadi,5801399,0,2
Brennan Dumont,6098883,0,3
Bogdan Boateng,29500928,0,2
Kellen Ellington,54126450,0,1
Darnell Halvorsen,10120124,0,2
Cam Vasquez,11084689,0,1
Dante Ferreira,19221073,0,2
Andre Stavros,10246935,0,1
Bogdan Achiuwa,10979012,0,2
Brennan Marsh,5137298,0,2
Darnell Duval,10164925,0,1
Deni Dumont,11190944,0,3

Roster count: 15

What signing exceptions do we still have available, and what does using each one cost us?
```

**Ground truth:** {"apron_level": "over the first apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 5685000, "reason": "available at $5,685,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Portland apron salary = $199,715,707 (over the first apron)
  2. 2025-26 first apron = $195,945,000
  3. 2025-26 second apron = $207,824,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: available = $5,685,000 (available at $5,685,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: unavailable (unavailable over the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 27 -- exception_survey

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

SACRAMENTO -- 2024-25 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Kellen Lindqvist | $3,154,758 | -- | 4 |
| Isaiah Cordero | $7,172,139 | -- | 2 |
| Tobias Kalinic | $2,088,000 | -- | 3 |
| Isaiah Kearns | $7,247,452 | -- | 3 |
| Deni Sabonis | $14,083,706 | -- | 4 |
| Trey Halvorsen | $5,405,085 | -- | 2 |
| Luka Amadi | $3,733,473 | -- | 3 |
| Tobias Kearns | $3,110,880 | -- | 1 |
| Marcus Ellington | $18,648,814 | -- | 2 |
| Deni Okoro | $6,660,291 | -- | 2 |
| Kobe Jokubaitis | $6,554,066 | -- | 1 |
| Santi Marsh | $33,856,058 | -- | 2 |
| Jaylen Okoro | $20,673,978 | -- | 4 |
| Marcus Amadi | $4,203,394 | -- | 2 |
| Bogdan Vasquez | $3,536,549 | -- | 1 |

Roster count: 15

What signing exceptions do we still have available, and what does using each one cost us?
```

**Ground truth:** {"apron_level": "under the tax line", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": 12822000, "reason": "a team with cap space uses the room exception instead", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": false, "amount": 5168000, "reason": "a team with cap space uses the room exception instead", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "a team with cap space uses the room exception instead", "hard_cap": "first apron"}, {"name": "room exception", "available": true, "amount": 7983000, "reason": "available at $7,983,000 once cap space is used; triggers no hard cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Sacramento apron salary = $140,128,643 (under the tax line)
  2. 2024-25 first apron = $178,132,000
  3. 2024-25 second apron = $188,931,000
  4. non-taxpayer mid-level exception: unavailable = $12,822,000 (a team with cap space uses the room exception instead)
  5. taxpayer mid-level exception: unavailable = $5,168,000 (a team with cap space uses the room exception instead)
  6. bi-annual exception: unavailable (a team with cap space uses the room exception instead)
  7. room exception: available = $7,983,000 (available at $7,983,000 once cap space is used; triggers no hard cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 28 -- scenario_planning

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
Trey Sabonis            $11,161,200
Kellen Vasquez          $20,073,111
Andre Brantley          $25,094,979
Goran Vasquez           $34,340,488
Santi Jokubaitis         $3,219,190
Jaylen Ellington         $5,482,924
Bogdan Reddish           $5,148,157
Tobias Ibarra            $3,684,190
Santi Petrov            $48,448,329
Terrance Kalinic         $2,773,842
Bogdan Jokubaitis        $8,827,747
Jalil Reddish            $4,789,528
Zion Halvorsen           $7,248,615
Goran Osei              $11,293,601
Kobe Petrov             $19,765,720

Roster count: 15

Ownership wants us out of the second apron. Walk me through how we do it.
```

**Ground truth:** {"apron_salary": 211351621, "second_apron": 188931000, "overage": 22420621, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Andre Brantley", "salary": 25094979, "surplus": 2674358}, {"player": "Goran Vasquez", "salary": 34340488, "surplus": 11919867}, {"player": "Santi Petrov", "salary": 48448329, "surplus": 26027708}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $22,420,621

**Computation trace (the only figures you may use):**

```
  1. Washington apron salary = $211,351,621
  2. 2024-25 second apron = $188,931,000
  3. Amount over the second apron = $22,420,621
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Andre Brantley alone clears the gap = $2,674,358 ($25,094,979 out against $22,420,621 of overage, assuming no salary comes back)
  7. Moving Goran Vasquez alone clears the gap = $11,919,867 ($34,340,488 out against $22,420,621 of overage, assuming no salary comes back)
  8. Moving Santi Petrov alone clears the gap = $26,027,708 ($48,448,329 out against $22,420,621 of overage, assuming no salary comes back)
```


## Scenario 29 -- trade_legality

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

CHARLOTTE -- 2024-25 CAP SHEET
Dante Boateng          $10,434,607
Santi Ellington         $9,365,834
Luka Beauchamp         $11,332,781
Andre Jokubaitis        $6,398,457
Cam Boateng            $13,157,603
Devonte Cordero        $18,591,540
Corey Lindqvist        $10,023,356
Santi Whitfield         $6,979,835
Jalil Vasquez           $8,076,682
Corey Ibarra           $49,205,800
Tobias Sabonis          $4,728,286
Elijah Kearns          $12,791,489
Goran Duval            $20,973,390

Roster count: 13

We're discussing a trade that sends Andre Jokubaitis to another team for Andre Cordero at $6,656,044. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 6398457, "incoming_salary": 6656044, "max_incoming": 6398457, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 182317247, "hard_cap_triggered": "none", "violations": ["Charlotte: salary matching -- Charlotte takes back $6,656,044 but may only absorb $6,398,457 under 100% of outgoing salary (team is over the first apron) -- over by $257,587"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $6,398,457, $6,656,044, $6,398,457

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Charlotte
  2. --- Charlotte (2024-25) --- (apron salary $182,059,660, over the first apron)
  3. Charlotte outgoing salary = $6,398,457 (Andre Jokubaitis $6,398,457)
  4. Charlotte incoming salary = $6,656,044 (Andre Cordero $6,656,044)
  5. Charlotte matching limit = $6,398,457 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (Charlotte takes back $6,656,044 but may only absorb $6,398,457 under 100% of outgoing salary (team is over the first apron) -- over by $257,587)
  7. Charlotte apron salary after the trade = $182,317,247
  8. Verdict: ILLEGAL
```


## Scenario 30 -- tax_bill

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Dante Vasquez | $2,778,252 | -- | 1 |
| Malik Achiuwa | $48,905,427 | -- | 3 |
| Rashad Dumont | $3,959,379 | -- | 4 |
| Marcus Ellington | $8,511,578 | -- | 1 |
| Santi Amadi | $4,564,072 | -- | 1 |
| Malik Novak | $8,995,011 | -- | 2 |
| Terrance Duval | $22,286,582 | -- | 3 |
| Brennan Kearns | $6,158,875 | -- | 4 |
| Rashad Whitfield | $4,587,806 | -- | 3 |
| Andre Marsh | $10,169,855 | -- | 4 |
| Darnell Kearns | $33,418,676 | -- | 2 |
| Corey Ferreira | $8,939,785 | -- | 1 |
| Kellen Beauchamp | $27,299,993 | -- | 2 |
| Alperen Kalinic | $5,882,182 | -- | 1 |
| Kristaps Halvorsen | $8,715,073 | -- | 4 |

Roster count: 15
Repeater taxpayer: yes

Ownership wants the tax number. What do we owe, and how does it break down?
```

**Ground truth:** {"tax_salary": 205172546, "tax_line": 170814000, "amount_over": 34358546, "is_repeater": true, "total": 138129640, "brackets": [{"index": 1, "amount": 5168000, "rate": 2.5, "owed": 12920000}, {"index": 2, "amount": 5168000, "rate": 2.75, "owed": 14212000}, {"index": 3, "amount": 5168000, "rate": 3.5, "owed": 18088000}, {"index": 4, "amount": 5168000, "rate": 4.25, "owed": 21964000}, {"index": 5, "amount": 5168000, "rate": 4.75, "owed": 24548000}, {"index": 6, "amount": 5168000, "rate": 5.25, "owed": 27132000}, {"index": 7, "amount": 3350546, "rate": 5.75, "owed": 19265640}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $138,129,640, $34,358,546

**Computation trace (the only figures you may use):**

```
  1. Orlando tax salary = $205,172,546
  2. 2024-25 luxury tax line = $170,814,000
  3. Amount over the tax line = $34,358,546 ($205,172,546 - $170,814,000)
  4. Rate schedule: repeater (2024-25) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $5,168,000 at $2.50 per dollar = $12,920,000
  6. Bracket 2: $5,168,000 at $2.75 per dollar = $14,212,000
  7. Bracket 3: $5,168,000 at $3.50 per dollar = $18,088,000
  8. Bracket 4: $5,168,000 at $4.25 per dollar = $21,964,000
  9. Bracket 5: $5,168,000 at $4.75 per dollar = $24,548,000
  10. Bracket 6: $5,168,000 at $5.25 per dollar = $27,132,000
  11. Bracket 7: $3,350,546 at $5.75 per dollar = $19,265,640
  12. Total luxury tax owed = $138,129,640
  13. Repeater status applies (paid the tax in 3 of the prior 4 seasons)
  14. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 31 -- trade_legality

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
Jalil Amadi             $7,110,241
Bogdan Achiuwa          $6,866,110
Micah Sabonis          $54,126,450
Micah Rees              $4,356,365
Malik Jokubaitis        $5,224,084
Amari Reddish           $4,738,265
Jalil Duval            $25,406,027
Julian Okoro           $11,524,895
Malik Dumont            $8,743,167
Jaylen Amadi            $9,003,854
Kellen Amadi           $10,439,047
Tobias Achiuwa         $13,841,112
Corey Ferreira         $22,924,883
Alperen Novak           $6,729,538

Roster count: 14

We're discussing a trade that sends Kellen Amadi to another team for Devonte Okoro at $17,453,399. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 10439047, "incoming_salary": 17453399, "max_incoming": 18966047, "matching_rule": "outgoing + $8,527,000 (middle band)", "apron_level": "over the tax line", "apron_salary_after": 198048390, "hard_cap_triggered": "first apron", "violations": ["Toronto: hard cap exceeded -- Toronto would sit at $198,048,390, above its first apron hard cap of $195,945,000 -- over by $2,103,390"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $10,439,047, $17,453,399, $18,966,047

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Toronto
  2. --- Toronto (2025-26) --- (apron salary $191,034,038, over the tax line)
  3. Toronto outgoing salary = $10,439,047 (Kellen Amadi $10,439,047)
  4. Toronto incoming salary = $17,453,399 (Devonte Okoro $17,453,399)
  5. Toronto matching limit = $18,966,047 (outgoing + $8,527,000 (middle band))
  6. Toronto hard-capped at the first apron = $195,945,000 (took back more than 100% of outgoing salary)
  7. Toronto apron salary after the trade = $198,048,390
  8. VIOLATION -- hard cap exceeded (Toronto would sit at $198,048,390, above its first apron hard cap of $195,945,000 -- over by $2,103,390)
  9. Verdict: ILLEGAL
```


## Scenario 32 -- trade_legality

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

MEMPHIS -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Santi Marsh,54126450,0,1
Isaiah Vasquez,5173313,0,1
Nico Ferreira,4461706,0,3
Tobias Whitfield,7119880,0,2
Cam Osei,9725974,0,2
Jaylen Reddish,8865910,0,4
Brennan Jokubaitis,10862667,0,2
Isaiah Petrov,11013641,0,3
Terrance Jokubaitis,10115479,0,1
Micah Ellington,33637415,0,2
Santi Vasquez,8359782,0,2
Amari Osei,11040033,0,4
Dante Ibarra,7703057,0,3
Kobe Brantley,6608636,0,4
Darnell Brantley,36810320,0,3

Roster count: 15

We're discussing a trade that sends Amari Osei and Jaylen Reddish to another team for Devonte Achiuwa at $20,672,743. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 19905943, "incoming_salary": 20672743, "max_incoming": 19905943, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 226391063, "hard_cap_triggered": "none", "violations": ["Memphis: second-apron aggregation ban -- Memphis is over the second apron ($225,624,263 vs $207,824,000) and may not combine 2 salaries in one trade", "Memphis: salary matching -- Memphis takes back $20,672,743 but may only absorb $19,905,943 under 100% of outgoing salary (team is over the first apron) -- over by $766,800"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $19,905,943, $20,672,743, $19,905,943

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Memphis
  2. --- Memphis (2025-26) --- (apron salary $225,624,263, over the second apron)
  3. Memphis outgoing salary = $19,905,943 (Amari Osei $11,040,033, Jaylen Reddish $8,865,910)
  4. Memphis incoming salary = $20,672,743 (Devonte Achiuwa $20,672,743)
  5. VIOLATION -- second-apron aggregation ban (Memphis is over the second apron ($225,624,263 vs $207,824,000) and may not combine 2 salaries in one trade)
  6. Memphis matching limit = $19,905,943 (100% of outgoing salary (team is over the first apron))
  7. VIOLATION -- salary matching (Memphis takes back $20,672,743 but may only absorb $19,905,943 under 100% of outgoing salary (team is over the first apron) -- over by $766,800)
  8. Memphis apron salary after the trade = $226,391,063
  9. Verdict: ILLEGAL
```


## Scenario 33 -- anti_staleness

**What the user said:**

```
2027-28 LEAGUE THRESHOLDS
  Salary cap:          $149,024,000
  Luxury tax line:     $181,064,000
  First apron:         $188,821,000
  Second apron:        $200,268,000
  Non-taxpayer MLE:    $13,591,000
  Taxpayer MLE:        $5,478,000
  Room exception:      $8,462,000
  Tax bracket width:   $5,478,000
  Bi-annual exception: $5,300,000

ORLANDO -- 2027-28 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Zion Sabonis,9568192,0,1
Andre Kalinic,4365305,0,4
Jalil Osei,22099418,0,1
Zion Ferreira,6026522,0,2
Devonte Reddish,5915363,0,2
Deni Boateng,52158400,0,1
Malik Rees,9567731,0,4
Jalil Cordero,5730604,0,4
Isaiah Okoro,9810051,0,4
Julian Okoro,3445342,0,3
Rashad Dumont,35793958,0,4
Dante Ellington,4612375,0,2
Luka Petrov,20419965,0,4
Goran Kearns,6439476,0,2

Roster count: 14

Using the 2027-28 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2027-28", "apron_salary": 195952702, "apron_level": "over the first apron", "first_apron_provided": 188821000, "second_apron_provided": 200268000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $195,952,702, $200,268,000

**Computation trace (the only figures you may use):**

```
  1. Orlando apron salary = $195,952,702
  2. 2027-28 first apron (from the figures provided) = $188,821,000
  3. 2027-28 second apron (from the figures provided) = $200,268,000
  4. Position: over the first apron
  5. Room below the second apron = $4,315,298
```


## Scenario 34 -- trade_legality

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
| Santi Rees | $13,252,256 | -- | 4 |
| Jalil Ferreira | $57,736,350 | -- | 1 |
| Julian Achiuwa | $32,950,716 | -- | 4 |
| Goran Ferreira | $6,305,306 | -- | 1 |
| Nico Lindqvist | $42,564,522 | -- | 1 |
| Zion Ferreira | $6,869,533 | -- | 2 |
| Goran Ellington | $14,037,910 | -- | 3 |
| Kristaps Okoro | $8,767,778 | -- | 1 |
| Malik Whitfield | $10,015,363 | -- | 4 |
| Devonte Ibarra | $8,033,016 | -- | 1 |
| Micah Petrov | $7,574,712 | -- | 4 |
| Kristaps Ellington | $8,902,921 | -- | 4 |
| Deni Lindqvist | $15,236,264 | -- | 3 |

Roster count: 13

We're discussing a trade that sends Deni Lindqvist and Jalil Ferreira to another team for Santi Petrov at $86,486,071. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 72972614, "incoming_salary": 86486071, "max_incoming": 72972614, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 245760104, "hard_cap_triggered": "none", "violations": ["Houston: second-apron aggregation ban -- Houston is over the second apron ($232,246,647 vs $221,686,000) and may not combine 2 salaries in one trade", "Houston: salary matching -- Houston takes back $86,486,071 but may only absorb $72,972,614 under 100% of outgoing salary (team is over the first apron) -- over by $13,513,457"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $72,972,614, $86,486,071, $72,972,614

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Houston
  2. --- Houston (2026-27) --- (apron salary $232,246,647, over the second apron)
  3. Houston outgoing salary = $72,972,614 (Deni Lindqvist $15,236,264, Jalil Ferreira $57,736,350)
  4. Houston incoming salary = $86,486,071 (Santi Petrov $86,486,071)
  5. VIOLATION -- second-apron aggregation ban (Houston is over the second apron ($232,246,647 vs $221,686,000) and may not combine 2 salaries in one trade)
  6. Houston matching limit = $72,972,614 (100% of outgoing salary (team is over the first apron))
  7. VIOLATION -- salary matching (Houston takes back $86,486,071 but may only absorb $72,972,614 under 100% of outgoing salary (team is over the first apron) -- over by $13,513,457)
  8. Houston apron salary after the trade = $245,760,104
  9. Verdict: ILLEGAL
```


## Scenario 35 -- anti_staleness

**What the user said:**

```
2028-29 LEAGUE THRESHOLDS
  Salary cap:          $165,187,000
  Luxury tax line:     $200,701,000
  First apron:         $209,300,000
  Second apron:        $221,988,000
  Non-taxpayer MLE:    $15,065,000
  Taxpayer MLE:        $6,072,000
  Room exception:      $9,379,000
  Tax bracket width:   $6,072,000
  Bi-annual exception: $5,341,000

HOUSTON -- 2028-29 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Malik Ferreira | $9,088,117 | -- | 1 |
| Kristaps Reddish | $24,429,825 | -- | 2 |
| Goran Ellington | $6,428,570 | -- | 3 |
| Cam Stavros | $56,093,403 | -- | 4 |
| Kobe Cordero | $20,570,901 | -- | 4 |
| Alperen Reddish | $5,569,778 | -- | 4 |
| Malik Rees | $9,036,032 | -- | 3 |
| Jalil Osei | $6,218,185 | -- | 2 |
| Nico Ellington | $8,553,885 | -- | 1 |
| Andre Lindqvist | $6,814,353 | -- | 3 |
| Alperen Whitfield | $3,611,124 | -- | 4 |
| Kristaps Okoro | $57,815,450 | -- | 3 |
| Kellen Nakamura | $5,892,048 | -- | 4 |

Roster count: 13

Using the 2028-29 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2028-29", "apron_salary": 220121671, "apron_level": "over the first apron", "first_apron_provided": 209300000, "second_apron_provided": 221988000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $220,121,671, $221,988,000

**Computation trace (the only figures you may use):**

```
  1. Houston apron salary = $220,121,671
  2. 2028-29 first apron (from the figures provided) = $209,300,000
  3. 2028-29 second apron (from the figures provided) = $221,988,000
  4. Position: over the first apron
  5. Room below the second apron = $1,866,329
```


## Scenario 36 -- anti_staleness

**What the user said:**

```
2028-29 LEAGUE THRESHOLDS
  Salary cap:          $169,886,000
  Luxury tax line:     $206,410,000
  First apron:         $215,254,000
  Second apron:        $228,303,000
  Non-taxpayer MLE:    $15,494,000
  Taxpayer MLE:        $6,245,000
  Room exception:      $9,646,000
  Tax bracket width:   $6,245,000
  Bi-annual exception: $5,493,000

OKLAHOMA CITY -- 2028-29 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Malik Beauchamp,8575916,0,3
Isaiah Reddish,5667703,0,3
Isaiah Rees,31942432,0,2
Jalil Kearns,8323510,0,4
Marcus Duval,6659151,0,3
Dante Osei,10959210,0,1
Nikola Lindqvist,6661785,0,1
Jaylen Nakamura,5921316,0,3
Zion Brantley,16545063,0,3
Trey Jokubaitis,9014465,0,4
Kobe Sabonis,10729595,0,3
Terrance Nakamura,8084370,0,1
Nikola Ibarra,59460099,0,2
Marcus Kearns,6836810,0,1
Corey Stavros,27254066,0,3

Roster count: 15

Using the 2028-29 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2028-29", "apron_salary": 222635491, "apron_level": "over the first apron", "first_apron_provided": 215254000, "second_apron_provided": 228303000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $222,635,491, $228,303,000

**Computation trace (the only figures you may use):**

```
  1. Oklahoma City apron salary = $222,635,491
  2. 2028-29 first apron (from the figures provided) = $215,254,000
  3. 2028-29 second apron (from the figures provided) = $228,303,000
  4. Position: over the first apron
  5. Room below the second apron = $5,667,509
```


## Scenario 37 -- hard_cap_consequence

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
player,salary,unlikely_incentives,years_remaining
Kellen Ferreira,6924971,0,3
Andre Petrov,6976806,0,3
Brennan Reddish,4876390,0,4
Brennan Marsh,7007479,0,4
Rashad Achiuwa,42984958,0,4
Alperen Kalinic,39240580,0,4
Goran Sabonis,8281764,0,1
Marcus Whitfield,5689896,0,3
Rashad Sabonis,5175203,0,4
Luka Kalinic,2646923,0,3
Luka Jokubaitis,6717424,0,4
Darnell Amadi,3526512,0,4
Terrance Ibarra,9976814,0,3
Dante Whitfield,26582006,0,4

Roster count: 14
Hard cap: first apron

We're hard-capped at the first apron. Can we add Kristaps Ellington at $952,431?
```

**Ground truth:** {"legal": true, "hard_cap": "first apron", "hard_cap_limit": 178132000, "room_below_hard_cap": 1524274, "salary": 952431, "apron_salary_after": 177560157, "reasons": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $952,431, $178,132,000

**Computation trace (the only figures you may use):**

```
  1. Washington apron salary before signing = $176,607,726 (over the tax line)
  2. Proposed salary for Kristaps Ellington = $952,431
  3. Exception: minimum salary exception
  4. Washington apron salary after signing = $177,560,157
  5. Hard cap: first apron = $178,132,000
  6. Room below the hard cap = $571,843
  7. Verdict: LEGAL
  8. Room below the first apron hard cap before signing = $1,524,274 ($178,132,000 - $176,607,726)
```


## Scenario 38 -- exception_eligibility

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
Santi Whitfield,5260496,0,1
Devonte Rees,7447955,0,4
Kellen Kearns,7610741,0,3
Terrance Petrov,15352395,0,4
Kobe Marsh,5108784,0,2
Brennan Sabonis,8423363,0,4
Terrance Stavros,19576261,0,3
Cam Kalinic,11851627,0,2
Alperen Kearns,5319287,0,3
Marcus Sabonis,54126450,0,1
Amari Petrov,9752957,0,4
Rashad Vasquez,11016975,0,1
Zion Brantley,54126450,0,3
Cam Ferreira,5205555,0,3

Roster count: 14

Can we sign Micah Marsh for $4,738,912 using the bi-annual exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "bi-annual exception", "salary": 4738912, "hard_cap_triggered": "none", "apron_level": "over the second apron", "apron_salary_after": 224918208, "reasons": ["bi-annual exception is unavailable over the first apron"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $4,738,912

**Computation trace (the only figures you may use):**

```
  1. Houston apron salary before signing = $220,179,296 (over the second apron)
  2. Proposed salary for Micah Marsh = $4,738,912
  3. Exception: bi-annual exception
  4. VIOLATION -- bi-annual exception unavailable (unavailable over the first apron)
  5. Houston apron salary after signing = $224,918,208
  6. Verdict: ILLEGAL
```


## Scenario 39 -- trade_legality

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

SACRAMENTO -- 2025-26 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Deni Ellington | $5,264,573 | -- | 4 |
| Devonte Sabonis | $47,557,721 | -- | 3 |
| Dante Marsh | $6,352,667 | -- | 3 |
| Alperen Rees | $11,679,030 | -- | 4 |
| Luka Brantley | $4,236,907 | -- | 4 |
| Bogdan Okoro | $6,280,316 | -- | 3 |
| Malik Ferreira | $4,265,172 | -- | 3 |
| Zion Ibarra | $4,316,398 | -- | 3 |
| Trey Rees | $25,744,529 | -- | 2 |
| Darnell Jokubaitis | $48,169,564 | -- | 3 |
| Nikola Rees | $21,885,572 | -- | 1 |
| Kristaps Stavros | $26,325,644 | -- | 3 |
| Kellen Novak | $6,836,102 | -- | 3 |

Roster count: 13

We're discussing a trade that sends Kellen Novak and Trey Rees to another team for Deni Achiuwa at $37,344,722. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 32580631, "incoming_salary": 37344722, "max_incoming": 32580631, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 223678286, "hard_cap_triggered": "none", "violations": ["Sacramento: second-apron aggregation ban -- Sacramento is over the second apron ($218,914,195 vs $207,824,000) and may not combine 2 salaries in one trade", "Sacramento: salary matching -- Sacramento takes back $37,344,722 but may only absorb $32,580,631 under 100% of outgoing salary (team is over the first apron) -- over by $4,764,091"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $32,580,631, $37,344,722, $32,580,631

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Sacramento
  2. --- Sacramento (2025-26) --- (apron salary $218,914,195, over the second apron)
  3. Sacramento outgoing salary = $32,580,631 (Kellen Novak $6,836,102, Trey Rees $25,744,529)
  4. Sacramento incoming salary = $37,344,722 (Deni Achiuwa $37,344,722)
  5. VIOLATION -- second-apron aggregation ban (Sacramento is over the second apron ($218,914,195 vs $207,824,000) and may not combine 2 salaries in one trade)
  6. Sacramento matching limit = $32,580,631 (100% of outgoing salary (team is over the first apron))
  7. VIOLATION -- salary matching (Sacramento takes back $37,344,722 but may only absorb $32,580,631 under 100% of outgoing salary (team is over the first apron) -- over by $4,764,091)
  8. Sacramento apron salary after the trade = $223,678,286
  9. Verdict: ILLEGAL
```


