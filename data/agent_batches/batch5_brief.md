# Writing batch 5

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

Write one JSON object per line to `data/agent_batches/batch5_responses.jsonl`, nothing else in the file:

    {"id": 0, "response": "**Verdict: ILLEGAL.** ..."}

The `id` must match the scenario number below.

---

## Scenario 0 -- anti_staleness

**What the user said:**

```
2028-29 LEAGUE THRESHOLDS
  Salary cap:          $152,060,000
  Luxury tax line:     $184,752,000
  First apron:         $192,668,000
  Second apron:        $204,348,000
  Non-taxpayer MLE:    $13,868,000
  Taxpayer MLE:        $5,590,000
  Room exception:      $8,634,000
  Tax bracket width:   $5,590,000
  Bi-annual exception: $5,408,000

PORTLAND -- 2028-29 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Jalil Whitfield,39335214,0,4
Cam Lindqvist,8673925,0,4
Devonte Sabonis,7921736,0,1
Julian Ellington,3748952,0,3
Cam Stavros,7875515,0,4
Corey Ellington,5857991,0,4
Zion Rees,50506957,0,1
Micah Okoro,8785026,0,1
Kellen Novak,7270537,0,3
Dante Duval,4797971,0,1
Darnell Kalinic,18545688,0,1
Rashad Ibarra,2892494,0,2
Devonte Okoro,25429146,0,3

Roster count: 13

Using the 2028-29 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2028-29", "apron_salary": 191641152, "apron_level": "over the tax line", "first_apron_provided": 192668000, "second_apron_provided": 204348000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $191,641,152, $204,348,000

**Computation trace (the only figures you may use):**

```
  1. Portland apron salary = $191,641,152
  2. 2028-29 first apron (from the figures provided) = $192,668,000
  3. 2028-29 second apron (from the figures provided) = $204,348,000
  4. Position: over the tax line
  5. Room below the second apron = $12,706,848
```


## Scenario 1 -- trade_legality

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
Goran Ibarra             $30,530,236
Amari Whitfield           $9,710,045
Luka Duval               $16,895,961
Santi Brantley            $7,621,026
Zion Beauchamp           $28,908,409
Dante Dumont              $7,331,894
Jalil Achiuwa            $12,813,648
Devonte Brantley          $4,276,807
Bogdan Whitfield          $9,841,019
Amari Stavros            $12,599,400
Corey Kearns             $54,126,450
Devonte Jokubaitis       $12,364,221
Amari Reddish             $5,753,859
Amari Cordero             $5,694,808
Luka Dumont               $6,316,316

Roster count: 15

We're discussing a trade that sends Bogdan Whitfield to another team for Kellen Marsh at $8,379,098. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 9841019, "incoming_salary": 8379098, "max_incoming": 9841019, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 223322178, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $9,841,019, $8,379,098, $9,841,019

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Atlanta
  2. --- Atlanta (2025-26) --- (apron salary $224,784,099, over the second apron)
  3. Atlanta outgoing salary = $9,841,019 (Bogdan Whitfield $9,841,019)
  4. Atlanta incoming salary = $8,379,098 (Kellen Marsh $8,379,098)
  5. Atlanta matching limit = $9,841,019 (100% of outgoing salary (team is over the first apron))
  6. Atlanta apron salary after the trade = $223,322,178
  7. Verdict: LEGAL
```


## Scenario 2 -- trade_legality

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
Isaiah Lindqvist       $16,204,221
Julian Reddish         $15,487,269
Isaiah Dumont           $7,260,413
Trey Osei               $2,661,427
Kellen Marsh            $3,365,754
Zion Boateng            $7,833,918
Terrance Duval         $40,012,192
Jaylen Duval            $3,165,738
Cam Jokubaitis          $6,540,152
Kobe Osei               $3,349,036
Isaiah Kalinic         $21,925,644
Bogdan Reddish          $4,540,018
Malik Stavros           $3,050,110
Alperen Okoro          $38,859,610
Deni Kearns             $2,531,945

Roster count: 15

We're discussing a trade that sends Terrance Duval and Isaiah Dumont to another team for Dante Kalinic at $60,724,355. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 47272605, "incoming_salary": 60724355, "max_incoming": 59340756, "matching_rule": "125% + $250,000 (outgoing above $29,974,000)", "apron_level": "over the tax line", "apron_salary_after": 190239197, "hard_cap_triggered": "first apron", "violations": ["Brooklyn: salary matching -- Brooklyn takes back $60,724,355 but may only absorb $59,340,756 under 125% + $250,000 (outgoing above $29,974,000) -- over by $1,383,599", "Brooklyn: hard cap exceeded -- Brooklyn would sit at $190,239,197, above its first apron hard cap of $178,132,000 -- over by $12,107,197"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $47,272,605, $60,724,355, $59,340,756

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Brooklyn
  2. --- Brooklyn (2024-25) --- (apron salary $176,787,447, over the tax line)
  3. Brooklyn outgoing salary = $47,272,605 (Terrance Duval $40,012,192, Isaiah Dumont $7,260,413)
  4. Brooklyn incoming salary = $60,724,355 (Dante Kalinic $60,724,355)
  5. Brooklyn matching limit = $59,340,756 (125% + $250,000 (outgoing above $29,974,000))
  6. VIOLATION -- salary matching (Brooklyn takes back $60,724,355 but may only absorb $59,340,756 under 125% + $250,000 (outgoing above $29,974,000) -- over by $1,383,599)
  7. Brooklyn hard-capped at the first apron = $178,132,000 (took back more than 100% of outgoing salary)
  8. Brooklyn hard-capped at the second apron = $188,931,000 (aggregated two or more salaries in one trade)
  9. Two hard caps triggered -- the tighter one governs = $178,132,000
  10. Brooklyn apron salary after the trade = $190,239,197
  11. VIOLATION -- hard cap exceeded (Brooklyn would sit at $190,239,197, above its first apron hard cap of $178,132,000 -- over by $12,107,197)
  12. Verdict: ILLEGAL
```


## Scenario 3 -- trade_legality

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
player,salary,unlikely_incentives,years_remaining
Darnell Ellington,5248931,0,3
Kobe Petrov,10113115,0,3
Alperen Duval,14259219,0,1
Kristaps Rees,25827044,0,3
Devonte Ferreira,3672812,0,3
Kellen Achiuwa,3653391,0,1
Cam Jokubaitis,7070653,0,3
Amari Dumont,10110933,0,1
Nikola Ibarra,45082278,0,1
Nico Stavros,7497665,0,1
Elijah Brantley,9463792,0,2
Isaiah Amadi,23665327,0,1
Kobe Halvorsen,6030166,0,1
Rashad Ibarra,7249193,0,2

Roster count: 14

We're discussing a trade that sends Kellen Achiuwa and Amari Dumont to another team for Darnell Stavros at $16,483,763. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 13764324, "incoming_salary": 16483763, "max_incoming": 13764324, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 181663958, "hard_cap_triggered": "second apron", "violations": ["New Orleans: salary matching -- New Orleans takes back $16,483,763 but may only absorb $13,764,324 under 100% of outgoing salary (team is over the first apron) -- over by $2,719,439"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $13,764,324, $16,483,763, $13,764,324

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: New Orleans
  2. --- New Orleans (2024-25) --- (apron salary $178,944,519, over the first apron)
  3. New Orleans outgoing salary = $13,764,324 (Kellen Achiuwa $3,653,391, Amari Dumont $10,110,933)
  4. New Orleans incoming salary = $16,483,763 (Darnell Stavros $16,483,763)
  5. New Orleans matching limit = $13,764,324 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (New Orleans takes back $16,483,763 but may only absorb $13,764,324 under 100% of outgoing salary (team is over the first apron) -- over by $2,719,439)
  7. New Orleans hard-capped at the second apron = $188,931,000 (aggregated two or more salaries in one trade)
  8. New Orleans apron salary after the trade = $181,663,958
  9. New Orleans stays under its second apron hard cap = $7,267,042 ($188,931,000 - $181,663,958 of room to spare)
  10. Verdict: ILLEGAL
```


## Scenario 4 -- trade_legality

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
Devonte Duval          $11,354,543
Elijah Kalinic          $9,371,695
Kobe Lindqvist         $54,126,450
Amari Marsh            $36,128,066
Bogdan Halvorsen        $5,082,329
Julian Novak            $5,369,295
Amari Cordero          $19,337,368
Rashad Ibarra           $6,277,234
Nikola Ibarra           $4,214,385
Dante Rees             $21,458,645
Marcus Rees             $7,014,084
Kellen Kearns           $5,809,986
Zion Jokubaitis         $9,453,294
Jaylen Rees             $8,485,265

Roster count: 14

We're discussing a trade that sends Amari Marsh to another team for Kobe Boateng at $46,527,858. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 36128066, "incoming_salary": 46527858, "max_incoming": 36128066, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 213882431, "hard_cap_triggered": "none", "violations": ["Detroit: salary matching -- Detroit takes back $46,527,858 but may only absorb $36,128,066 under 100% of outgoing salary (team is over the first apron) -- over by $10,399,792"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $36,128,066, $46,527,858, $36,128,066

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Detroit
  2. --- Detroit (2025-26) --- (apron salary $203,482,639, over the first apron)
  3. Detroit outgoing salary = $36,128,066 (Amari Marsh $36,128,066)
  4. Detroit incoming salary = $46,527,858 (Kobe Boateng $46,527,858)
  5. Detroit matching limit = $36,128,066 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (Detroit takes back $46,527,858 but may only absorb $36,128,066 under 100% of outgoing salary (team is over the first apron) -- over by $10,399,792)
  7. Detroit apron salary after the trade = $213,882,431
  8. Verdict: ILLEGAL
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

TORONTO -- 2024-25 CAP SHEET
Dante Vasquez          $17,872,498
Brennan Dumont         $13,505,091
Zion Sabonis            $8,006,876
Malik Lindqvist        $22,053,491
Cam Vasquez             $6,400,918
Rashad Beauchamp        $6,890,143
Rashad Boateng         $36,463,914
Andre Cordero           $4,717,849
Malik Halvorsen         $5,200,552
Kristaps Okoro          $4,882,652
Goran Beauchamp        $34,891,708
Darnell Ferreira        $6,325,820
Deni Amadi              $5,961,710
Isaiah Duval            $5,626,552

Roster count: 14

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 178799774, "unlikely_incentives": 0, "apron_salary": 178799774, "apron_level": "over the first apron", "room_to_first_apron": -667774, "room_to_second_apron": 10131226}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $178,799,774

**Computation trace (the only figures you may use):**

```
  1. Toronto salaries plus likely incentives = $178,799,774
  2. Apron salary = $178,799,774
  3. 2024-25 luxury tax line = $170,814,000
  4. 2024-25 first apron = $178,132,000
  5. 2024-25 second apron = $188,931,000
  6. Position: over the first apron
  7. Amount above the tax line = $7,985,774
  8. Amount above the first apron = $667,774
  9. Room below the second apron = $10,131,226
```


## Scenario 6 -- trade_legality

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
| Elijah Lindqvist | $8,034,482 | -- | 1 |
| Marcus Kalinic | $7,858,103 | -- | 3 |
| Corey Cordero | $7,319,697 | -- | 4 |
| Kobe Okoro | $2,587,266 | -- | 4 |
| Corey Dumont | $8,511,668 | -- | 4 |
| Julian Marsh | $11,998,850 | -- | 1 |
| Nico Rees | $5,648,455 | -- | 2 |
| Jalil Okoro | $5,950,097 | -- | 3 |
| Kellen Duval | $27,303,283 | -- | 2 |
| Kellen Vasquez | $6,920,891 | -- | 4 |
| Malik Lindqvist | $23,325,093 | -- | 1 |
| Isaiah Jokubaitis | $41,217,350 | -- | 4 |
| Bogdan Beauchamp | $4,604,562 | -- | 2 |
| Micah Novak | $21,989,175 | -- | 2 |
| Santi Sabonis | $7,033,610 | -- | 1 |

Roster count: 15

We're discussing a trade that sends Santi Sabonis to another team for Kellen Lindqvist at $10,979,813. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 7033610, "incoming_salary": 10979813, "max_incoming": 14317220, "matching_rule": "200% + $250,000 (outgoing at or below $8,527,000)", "apron_level": "over the tax line", "apron_salary_after": 194248785, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $7,033,610, $10,979,813, $14,317,220

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Sacramento
  2. --- Sacramento (2025-26) --- (apron salary $190,302,582, over the tax line)
  3. Sacramento outgoing salary = $7,033,610 (Santi Sabonis $7,033,610)
  4. Sacramento incoming salary = $10,979,813 (Kellen Lindqvist $10,979,813)
  5. Sacramento matching limit = $14,317,220 (200% + $250,000 (outgoing at or below $8,527,000))
  6. Sacramento hard-capped at the first apron = $195,945,000 (took back more than 100% of outgoing salary)
  7. Sacramento apron salary after the trade = $194,248,785
  8. Sacramento stays under its first apron hard cap = $1,696,215 ($195,945,000 - $194,248,785 of room to spare)
  9. Verdict: LEGAL
```


## Scenario 7 -- anti_staleness

**What the user said:**

```
2029-30 LEAGUE THRESHOLDS
  Salary cap:          $171,751,000
  Luxury tax line:     $208,678,000
  First apron:         $217,618,000
  Second apron:        $230,811,000
  Non-taxpayer MLE:    $15,663,000
  Taxpayer MLE:        $6,314,000
  Room exception:      $9,752,000
  Tax bracket width:   $6,314,000
  Bi-annual exception: $5,702,000

ORLANDO -- 2029-30 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Marcus Achiuwa | $7,283,642 | -- | 4 |
| Tobias Beauchamp | $7,162,370 | -- | 3 |
| Tobias Amadi | $5,178,677 | -- | 2 |
| Isaiah Brantley | $7,442,429 | -- | 3 |
| Marcus Brantley | $31,575,024 | -- | 3 |
| Marcus Halvorsen | $9,373,185 | -- | 4 |
| Luka Stavros | $9,778,007 | -- | 2 |
| Nikola Duval | $60,112,849 | -- | 1 |
| Santi Cordero | $8,308,490 | -- | 2 |
| Jaylen Marsh | $53,816,607 | -- | 3 |
| Kristaps Osei | $2,908,339 | -- | 1 |
| Trey Ellington | $9,222,031 | -- | 3 |
| Amari Vasquez | $17,554,488 | -- | 4 |

Roster count: 13

Using the 2029-30 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2029-30", "apron_salary": 229716138, "apron_level": "over the first apron", "first_apron_provided": 217618000, "second_apron_provided": 230811000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $229,716,138, $230,811,000

**Computation trace (the only figures you may use):**

```
  1. Orlando apron salary = $229,716,138
  2. 2029-30 first apron (from the figures provided) = $217,618,000
  3. 2029-30 second apron (from the figures provided) = $230,811,000
  4. Position: over the first apron
  5. Room below the second apron = $1,094,862
```


## Scenario 8 -- scenario_planning

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
player,salary,unlikely_incentives,years_remaining
Tobias Marsh,53187963,0,3
Amari Novak,4005532,0,2
Deni Beauchamp,2982828,0,3
Alperen Kearns,3947333,0,3
Isaiah Petrov,4076360,0,2
Goran Sabonis,4453137,0,2
Corey Halvorsen,23598803,0,2
Tobias Boateng,9293586,0,1
Brennan Reddish,24780667,0,2
Kobe Lindqvist,4384606,0,3
Marcus Jokubaitis,9529317,0,2
Nico Ibarra,10183757,0,2
Jaylen Jokubaitis,8721930,0,2
Micah Cordero,50807571,0,3
Julian Ellington,4253503,0,3

Roster count: 15

We need to get under the second apron before the deadline. What are our options, and what are we giving up?
```

**Ground truth:** {"apron_salary": 218206893, "second_apron": 207824000, "overage": 10382893, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Corey Halvorsen", "salary": 23598803, "surplus": 13215910}, {"player": "Brennan Reddish", "salary": 24780667, "surplus": 14397774}, {"player": "Micah Cordero", "salary": 50807571, "surplus": 40424678}, {"player": "Tobias Marsh", "salary": 53187963, "surplus": 42805070}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $10,382,893

**Computation trace (the only figures you may use):**

```
  1. Washington apron salary = $218,206,893
  2. 2025-26 second apron = $207,824,000
  3. Amount over the second apron = $10,382,893
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Corey Halvorsen alone clears the gap = $13,215,910 ($23,598,803 out against $10,382,893 of overage, assuming no salary comes back)
  7. Moving Brennan Reddish alone clears the gap = $14,397,774 ($24,780,667 out against $10,382,893 of overage, assuming no salary comes back)
  8. Moving Micah Cordero alone clears the gap = $40,424,678 ($50,807,571 out against $10,382,893 of overage, assuming no salary comes back)
  9. Moving Tobias Marsh alone clears the gap = $42,805,070 ($53,187,963 out against $10,382,893 of overage, assuming no salary comes back)
```


## Scenario 9 -- exception_eligibility

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

OKLAHOMA CITY -- 2026-27 CAP SHEET
Isaiah Reddish            $9,624,864
Marcus Ibarra            $21,091,984
Andre Nakamura           $11,341,470
Amari Duval              $21,639,694
Kristaps Halvorsen        $9,534,900
Marcus Osei              $29,574,412
Malik Sabonis             $8,310,631
Goran Achiuwa            $57,736,350
Devonte Lindqvist         $6,264,756
Dante Sabonis            $25,564,115
Santi Halvorsen           $7,616,066
Brennan Nakamura          $6,625,866
Goran Beauchamp          $11,863,587

Roster count: 13

Can we sign Malik Novak for $2,320,483 using the minimum salary exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": true, "exception": "minimum salary exception", "salary": 2320483, "hard_cap_triggered": "none", "apron_level": "over the second apron", "apron_salary_after": 229109178, "reasons": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $2,320,483

**Computation trace (the only figures you may use):**

```
  1. Oklahoma City apron salary before signing = $226,788,695 (over the second apron)
  2. Proposed salary for Malik Novak = $2,320,483
  3. Exception: minimum salary exception
  4. Oklahoma City apron salary after signing = $229,109,178
  5. Verdict: LEGAL
```


## Scenario 10 -- draft_penalty

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Kristaps Dumont | $26,047,577 | -- | 4 |
| Andre Dumont | $23,354,145 | -- | 1 |
| Andre Beauchamp | $5,755,834 | -- | 2 |
| Terrance Brantley | $4,864,825 | -- | 3 |
| Elijah Lindqvist | $49,205,800 | -- | 4 |
| Kellen Ellington | $3,729,177 | -- | 1 |
| Devonte Brantley | $6,198,665 | -- | 1 |
| Malik Brantley | $31,058,718 | -- | 2 |
| Luka Boateng | $7,846,067 | -- | 1 |
| Kellen Beauchamp | $2,896,103 | -- | 3 |
| Cam Boateng | $8,477,302 | -- | 1 |
| Kristaps Beauchamp | $9,672,340 | -- | 4 |
| Trey Boateng | $6,354,660 | -- | 1 |
| Malik Novak | $2,974,174 | -- | 2 |
| Cam Dumont | $7,174,276 | -- | 4 |

Roster count: 15

If we finish the season at this payroll, what happens to our draft picks? We've been over the second apron in 1 of the last five seasons.
```

**Ground truth:** {"pick_frozen": true, "frozen_draft_year": 2031, "pick_demoted": false, "seasons_over": 1, "reason": "Memphis finishes over the second apron, freezing its 2031 first-round pick. It unfreezes only after finishing below the second apron in 3 of the following 4 seasons"}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Memphis apron salary = $195,609,663 (over the second apron)
  2. Seasons finished over the second apron (within the window) (1)
  3. First-round pick frozen (the 2031 first-rounder (7 drafts out) becomes untradeable)
  4. Pick not yet demoted (demotion requires 3 of 5 seasons over the second apron)
```


## Scenario 11 -- draft_penalty

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
Darnell Ellington          $6,309,987
Micah Petrov              $16,792,125
Alperen Reddish            $3,150,588
Kobe Dumont                $6,275,550
Terrance Jokubaitis        $3,803,347
Rashad Halvorsen           $6,249,260
Amari Osei                $40,679,228
Marcus Marsh               $2,334,783
Zion Petrov               $44,052,089
Cam Nakamura               $2,553,149
Luka Sabonis               $4,256,685
Andre Osei                $19,965,273
Santi Ibarra               $9,080,530
Bogdan Achiuwa             $6,743,860
Zion Amadi                 $7,495,521

Roster count: 15

If we finish the season at this payroll, what happens to our draft picks? We've been over the second apron in 2 of the last five seasons.
```

**Ground truth:** {"pick_frozen": false, "frozen_draft_year": null, "pick_demoted": false, "seasons_over": 2, "reason": "Charlotte is not over the second apron, so no draft penalty attaches"}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Charlotte apron salary = $179,741,975 (over the first apron)
  2. Seasons finished over the second apron (within the window) (2)
  3. No penalty (Charlotte is not over the second apron, so no draft penalty attaches)
```


## Scenario 12 -- trade_legality

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
| Nikola Ellington | $18,854,100 | -- | 1 |
| Terrance Jokubaitis | $14,401,331 | -- | 1 |
| Kristaps Achiuwa | $14,192,014 | -- | 1 |
| Corey Jokubaitis | $4,485,256 | -- | 1 |
| Darnell Osei | $54,126,450 | -- | 2 |
| Zion Boateng | $7,813,744 | -- | 3 |
| Julian Stavros | $10,369,562 | -- | 4 |
| Bogdan Beauchamp | $8,958,747 | -- | 4 |
| Kellen Nakamura | $8,025,131 | -- | 4 |
| Alperen Ellington | $10,385,875 | -- | 3 |
| Andre Whitfield | $4,378,253 | -- | 2 |
| Zion Nakamura | $7,115,767 | -- | 1 |
| Dante Boateng | $11,554,109 | -- | 2 |
| Santi Stavros | $7,920,695 | -- | 4 |
| Bogdan Petrov | $40,516,862 | -- | 4 |

Roster count: 15

We're discussing a trade that sends Bogdan Beauchamp to another team for Elijah Ellington at $8,362,905. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 8958747, "incoming_salary": 8362905, "max_incoming": 8958747, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 222502054, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $8,958,747, $8,362,905, $8,958,747

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: San Antonio
  2. --- San Antonio (2025-26) --- (apron salary $223,097,896, over the second apron)
  3. San Antonio outgoing salary = $8,958,747 (Bogdan Beauchamp $8,958,747)
  4. San Antonio incoming salary = $8,362,905 (Elijah Ellington $8,362,905)
  5. San Antonio matching limit = $8,958,747 (100% of outgoing salary (team is over the first apron))
  6. San Antonio apron salary after the trade = $222,502,054
  7. Verdict: LEGAL
```


## Scenario 13 -- draft_penalty

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
| Isaiah Sabonis | $13,536,285 | -- | 4 |
| Corey Ibarra | $7,956,767 | -- | 1 |
| Rashad Achiuwa | $23,997,429 | -- | 2 |
| Kristaps Petrov | $9,389,440 | -- | 1 |
| Elijah Cordero | $49,205,800 | -- | 1 |
| Darnell Osei | $5,155,101 | -- | 1 |
| Brennan Ibarra | $7,625,967 | -- | 2 |
| Rashad Halvorsen | $6,888,069 | -- | 2 |
| Deni Achiuwa | $12,350,992 | -- | 1 |
| Corey Lindqvist | $12,980,338 | -- | 4 |
| Julian Vasquez | $8,492,818 | -- | 3 |
| Deni Ibarra | $10,675,900 | -- | 2 |
| Tobias Cordero | $13,020,613 | -- | 2 |
| Nico Novak | $6,505,061 | -- | 1 |

Roster count: 14

If we finish the season at this payroll, what happens to our draft picks? We've been over the second apron in 4 of the last five seasons.
```

**Ground truth:** {"pick_frozen": false, "frozen_draft_year": null, "pick_demoted": false, "seasons_over": 4, "reason": "Miami is not over the second apron, so no draft penalty attaches"}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Miami apron salary = $187,780,580 (over the first apron)
  2. Seasons finished over the second apron (within the window) (4)
  3. No penalty (Miami is not over the second apron, so no draft penalty attaches)
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

TORONTO -- 2026-27 CAP SHEET
Jaylen Nakamura          $25,318,798
Luka Duval                $6,152,600
Corey Petrov              $4,581,395
Kellen Rees              $49,244,168
Dante Marsh               $5,852,048
Isaiah Ferreira           $7,417,813
Luka Rees                 $4,143,781
Terrance Whitfield       $53,691,193
Malik Osei                $5,469,894
Nikola Kearns             $3,096,725
Terrance Duval           $27,670,950
Micah Ibarra              $6,929,119
Jaylen Beauchamp          $6,796,510
Nikola Ferreira           $7,211,814
Darnell Vasquez           $6,206,049

Roster count: 15

We're discussing a trade that sends Jaylen Beauchamp and Micah Ibarra to another team for Darnell Osei at $10,622,326. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 13725629, "incoming_salary": 10622326, "max_incoming": 13725629, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 216679554, "hard_cap_triggered": "second apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $13,725,629, $10,622,326, $13,725,629

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Toronto
  2. --- Toronto (2026-27) --- (apron salary $219,782,857, over the first apron)
  3. Toronto outgoing salary = $13,725,629 (Jaylen Beauchamp $6,796,510, Micah Ibarra $6,929,119)
  4. Toronto incoming salary = $10,622,326 (Darnell Osei $10,622,326)
  5. Toronto matching limit = $13,725,629 (100% of outgoing salary (team is over the first apron))
  6. Toronto hard-capped at the second apron = $221,686,000 (aggregated two or more salaries in one trade)
  7. Toronto apron salary after the trade = $216,679,554
  8. Toronto stays under its second apron hard cap = $5,006,446 ($221,686,000 - $216,679,554 of room to spare)
  9. Verdict: LEGAL
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

MEMPHIS -- 2024-25 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Santi Boateng | $4,796,111 | -- | 1 |
| Kobe Halvorsen | $5,647,756 | -- | 4 |
| Julian Marsh | $49,205,800 | -- | 2 |
| Elijah Amadi | $2,763,134 | -- | 1 |
| Darnell Whitfield | $12,575,656 | -- | 1 |
| Corey Marsh | $4,047,883 | -- | 1 |
| Rashad Stavros | $5,621,450 | -- | 1 |
| Marcus Osei | $49,205,800 | -- | 4 |
| Brennan Achiuwa | $27,840,938 | -- | 2 |
| Jaylen Brantley | $3,500,302 | -- | 1 |
| Kellen Beauchamp | $3,777,171 | -- | 3 |
| Kellen Lindqvist | $5,551,788 | -- | 1 |
| Corey Kalinic | $4,113,500 | -- | 2 |

Roster count: 13

We're discussing a trade that sends Darnell Whitfield to another team for Brennan Halvorsen at $14,867,119. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 12575656, "incoming_salary": 14867119, "max_incoming": 12575656, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 180938752, "hard_cap_triggered": "none", "violations": ["Memphis: salary matching -- Memphis takes back $14,867,119 but may only absorb $12,575,656 under 100% of outgoing salary (team is over the first apron) -- over by $2,291,463"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $12,575,656, $14,867,119, $12,575,656

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Memphis
  2. --- Memphis (2024-25) --- (apron salary $178,647,289, over the first apron)
  3. Memphis outgoing salary = $12,575,656 (Darnell Whitfield $12,575,656)
  4. Memphis incoming salary = $14,867,119 (Brennan Halvorsen $14,867,119)
  5. Memphis matching limit = $12,575,656 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (Memphis takes back $14,867,119 but may only absorb $12,575,656 under 100% of outgoing salary (team is over the first apron) -- over by $2,291,463)
  7. Memphis apron salary after the trade = $180,938,752
  8. Verdict: ILLEGAL
```


## Scenario 16 -- trade_legality

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
| Andre Cordero | $6,338,821 | -- | 4 |
| Cam Okoro | $25,547,236 | -- | 2 |
| Darnell Kalinic | $4,288,589 | -- | 2 |
| Jaylen Nakamura | $11,036,879 | -- | 4 |
| Zion Osei | $54,126,450 | -- | 1 |
| Goran Rees | $27,857,005 | -- | 3 |
| Deni Reddish | $5,733,285 | -- | 1 |
| Brennan Rees | $10,137,506 | -- | 1 |
| Santi Brantley | $20,813,009 | -- | 4 |
| Corey Vasquez | $8,482,646 | -- | 4 |
| Brennan Boateng | $3,701,393 | -- | 4 |
| Amari Ferreira | $6,480,346 | -- | 1 |
| Cam Amadi | $4,557,361 | -- | 3 |

Roster count: 13

We're discussing a trade that sends Deni Reddish and Darnell Kalinic to another team for Amari Dumont at $21,031,935. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 10021874, "incoming_salary": 21031935, "max_incoming": 18548874, "matching_rule": "outgoing + $8,527,000 (middle band)", "apron_level": "over the tax line", "apron_salary_after": 200110587, "hard_cap_triggered": "first apron", "violations": ["Chicago: salary matching -- Chicago takes back $21,031,935 but may only absorb $18,548,874 under outgoing + $8,527,000 (middle band) -- over by $2,483,061", "Chicago: hard cap exceeded -- Chicago would sit at $200,110,587, above its first apron hard cap of $195,945,000 -- over by $4,165,587"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $10,021,874, $21,031,935, $18,548,874

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Chicago
  2. --- Chicago (2025-26) --- (apron salary $189,100,526, over the tax line)
  3. Chicago outgoing salary = $10,021,874 (Deni Reddish $5,733,285, Darnell Kalinic $4,288,589)
  4. Chicago incoming salary = $21,031,935 (Amari Dumont $21,031,935)
  5. Chicago matching limit = $18,548,874 (outgoing + $8,527,000 (middle band))
  6. VIOLATION -- salary matching (Chicago takes back $21,031,935 but may only absorb $18,548,874 under outgoing + $8,527,000 (middle band) -- over by $2,483,061)
  7. Chicago hard-capped at the first apron = $195,945,000 (took back more than 100% of outgoing salary)
  8. Chicago hard-capped at the second apron = $207,824,000 (aggregated two or more salaries in one trade)
  9. Two hard caps triggered -- the tighter one governs = $195,945,000
  10. Chicago apron salary after the trade = $200,110,587
  11. VIOLATION -- hard cap exceeded (Chicago would sit at $200,110,587, above its first apron hard cap of $195,945,000 -- over by $4,165,587)
  12. Verdict: ILLEGAL
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

CHICAGO -- 2024-25 CAP SHEET
Nico Nakamura          $8,301,896
Devonte Marsh          $5,565,225
Dante Novak           $19,285,787
Andre Rees             $6,549,021
Santi Ellington       $24,314,630
Dante Stavros         $22,924,740
Darnell Duval          $8,445,922
Cam Dumont             $3,801,832
Kellen Dumont         $10,719,880
Trey Dumont            $4,505,334
Nico Boateng           $7,045,679
Goran Dumont           $4,830,741
Rashad Kalinic        $49,205,800
Cam Amadi             $10,194,882

Roster count: 14

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 185691369, "unlikely_incentives": 0, "apron_salary": 185691369, "apron_level": "over the first apron", "room_to_first_apron": -7559369, "room_to_second_apron": 3239631}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $185,691,369

**Computation trace (the only figures you may use):**

```
  1. Chicago salaries plus likely incentives = $185,691,369
  2. Apron salary = $185,691,369
  3. 2024-25 luxury tax line = $170,814,000
  4. 2024-25 first apron = $178,132,000
  5. 2024-25 second apron = $188,931,000
  6. Position: over the first apron
  7. Amount above the tax line = $14,877,369
  8. Amount above the first apron = $7,559,369
  9. Room below the second apron = $3,239,631
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

MIAMI -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Trey Whitfield | $4,204,401 | -- | 2 |
| Terrance Brantley | $8,423,572 | -- | 4 |
| Jaylen Amadi | $16,148,416 | -- | 4 |
| Andre Kearns | $8,622,606 | -- | 4 |
| Micah Duval | $9,010,027 | -- | 1 |
| Nikola Cordero | $4,389,933 | -- | 2 |
| Deni Sabonis | $47,870,273 | -- | 3 |
| Brennan Cordero | $5,798,571 | -- | 4 |
| Nikola Stavros | $15,727,041 | -- | 1 |
| Marcus Brantley | $22,570,707 | -- | 1 |
| Santi Lindqvist | $3,669,084 | -- | 3 |
| Jalil Sabonis | $5,571,591 | -- | 1 |
| Brennan Reddish | $50,089,213 | -- | 3 |

Roster count: 13
Repeater taxpayer: yes

Ownership wants the tax number. What do we owe, and how does it break down?
```

**Ground truth:** {"tax_salary": 202095435, "tax_line": 200428000, "amount_over": 1667435, "is_repeater": true, "total": 5002305, "brackets": [{"index": 1, "amount": 1667435, "rate": 3.0, "owed": 5002305}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $5,002,305, $1,667,435

**Computation trace (the only figures you may use):**

```
  1. Miami tax salary = $202,095,435
  2. 2026-27 luxury tax line = $200,428,000
  3. Amount over the tax line = $1,667,435 ($202,095,435 - $200,428,000)
  4. Rate schedule: repeater (2026-27) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $1,667,435 at $3.00 per dollar = $5,002,305
  6. Total luxury tax owed = $5,002,305
  7. Repeater status applies (paid the tax in 3 of the prior 4 seasons)
  8. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 19 -- hard_cap_consequence

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Corey Kearns | $35,103,147 | -- | 2 |
| Trey Amadi | $29,046,380 | -- | 3 |
| Malik Rees | $2,820,033 | -- | 4 |
| Luka Amadi | $10,611,847 | -- | 3 |
| Bogdan Rees | $7,308,860 | -- | 3 |
| Malik Boateng | $6,036,942 | -- | 3 |
| Tobias Jokubaitis | $10,061,001 | -- | 4 |
| Rashad Halvorsen | $6,659,184 | -- | 4 |
| Andre Stavros | $4,846,936 | -- | 3 |
| Marcus Stavros | $5,334,135 | -- | 1 |
| Andre Vasquez | $49,205,800 | -- | 2 |
| Dante Nakamura | $8,365,140 | -- | 3 |
| Deni Achiuwa | $4,323,811 | -- | 4 |

Roster count: 13
Hard cap: second apron

We're hard-capped at the second apron. Can we add Marcus Jokubaitis at $9,586,494?
```

**Ground truth:** {"legal": false, "hard_cap": "second apron", "hard_cap_limit": 188931000, "room_below_hard_cap": 9207784, "salary": 9586494, "apron_salary_after": 189309710, "reasons": ["the signing would put Atlanta at $189,309,710, above its second apron hard cap of $188,931,000"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $9,586,494, $188,931,000

**Computation trace (the only figures you may use):**

```
  1. Atlanta apron salary before signing = $179,723,216 (over the first apron)
  2. Proposed salary for Marcus Jokubaitis = $9,586,494
  3. Exception: minimum salary exception
  4. Atlanta apron salary after signing = $189,309,710
  5. Hard cap: second apron = $188,931,000
  6. VIOLATION -- hard cap exceeded = $378,710
  7. Verdict: ILLEGAL
  8. Room below the second apron hard cap before signing = $9,207,784 ($188,931,000 - $179,723,216)
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

SAN ANTONIO -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Corey Stavros,8835320,0,4
Marcus Whitfield,3618545,0,3
Devonte Ellington,35577078,0,2
Santi Petrov,5713230,0,3
Elijah Ibarra,8195405,0,2
Elijah Reddish,6554225,0,3
Corey Jokubaitis,6070380,0,1
Deni Duval,9631344,0,1
Malik Rees,7950825,0,1
Kobe Boateng,24389009,0,3
Rashad Petrov,6657106,0,2
Devonte Boateng,54126450,0,3
Tobias Kalinic,7785773,0,4
Jalil Kalinic,7244130,0,4

Roster count: 14

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 192348820, "unlikely_incentives": 0, "apron_salary": 192348820, "apron_level": "over the tax line", "room_to_first_apron": 3596180, "room_to_second_apron": 15475180}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $192,348,820

**Computation trace (the only figures you may use):**

```
  1. San Antonio salaries plus likely incentives = $192,348,820
  2. Apron salary = $192,348,820
  3. 2025-26 luxury tax line = $187,895,000
  4. 2025-26 first apron = $195,945,000
  5. 2025-26 second apron = $207,824,000
  6. Position: over the tax line
  7. Amount above the tax line = $4,453,820
  8. Room below the first apron = $3,596,180
  9. Room below the second apron = $15,475,180
```


## Scenario 21 -- tax_bill

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
| Zion Ferreira | $2,229,555 | -- | 4 |
| Nico Jokubaitis | $6,784,713 | -- | 4 |
| Trey Halvorsen | $4,844,678 | -- | 4 |
| Brennan Ferreira | $8,226,351 | -- | 3 |
| Trey Stavros | $21,872,125 | -- | 3 |
| Dante Beauchamp | $3,024,698 | -- | 2 |
| Deni Osei | $40,504,716 | -- | 3 |
| Nico Marsh | $46,045,605 | -- | 2 |
| Nikola Duval | $5,444,016 | -- | 3 |
| Trey Osei | $8,252,962 | -- | 4 |
| Cam Kearns | $8,334,417 | -- | 1 |
| Tobias Boateng | $3,603,421 | -- | 3 |
| Isaiah Jokubaitis | $23,601,304 | -- | 3 |
| Alperen Cordero | $5,729,752 | -- | 3 |
| Tobias Ibarra | $5,767,410 | -- | 2 |

Roster count: 15
Repeater taxpayer: yes

What's our luxury tax bill this season? Walk me through the brackets.
```

**Ground truth:** {"tax_salary": 194265723, "tax_line": 170814000, "amount_over": 23451723, "is_repeater": true, "total": 80387684, "brackets": [{"index": 1, "amount": 5168000, "rate": 2.5, "owed": 12920000}, {"index": 2, "amount": 5168000, "rate": 2.75, "owed": 14212000}, {"index": 3, "amount": 5168000, "rate": 3.5, "owed": 18088000}, {"index": 4, "amount": 5168000, "rate": 4.25, "owed": 21964000}, {"index": 5, "amount": 2779723, "rate": 4.75, "owed": 13203684}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $80,387,684, $23,451,723

**Computation trace (the only figures you may use):**

```
  1. Orlando tax salary = $194,265,723
  2. 2024-25 luxury tax line = $170,814,000
  3. Amount over the tax line = $23,451,723 ($194,265,723 - $170,814,000)
  4. Rate schedule: repeater (2024-25) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $5,168,000 at $2.50 per dollar = $12,920,000
  6. Bracket 2: $5,168,000 at $2.75 per dollar = $14,212,000
  7. Bracket 3: $5,168,000 at $3.50 per dollar = $18,088,000
  8. Bracket 4: $5,168,000 at $4.25 per dollar = $21,964,000
  9. Bracket 5: $2,779,723 at $4.75 per dollar = $13,203,684
  10. Total luxury tax owed = $80,387,684
  11. Repeater status applies (paid the tax in 3 of the prior 4 seasons)
  12. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 22 -- trade_legality

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
| Trey Brantley | $9,527,045 | -- | 3 |
| Bogdan Brantley | $3,998,535 | -- | 2 |
| Malik Lindqvist | $6,270,165 | -- | 1 |
| Luka Okoro | $9,588,831 | -- | 4 |
| Nikola Ferreira | $5,985,535 | -- | 3 |
| Deni Beauchamp | $26,771,639 | -- | 1 |
| Deni Osei | $6,148,837 | -- | 2 |
| Malik Whitfield | $8,475,283 | -- | 3 |
| Devonte Petrov | $8,648,134 | -- | 2 |
| Elijah Petrov | $29,643,200 | -- | 3 |
| Zion Cordero | $4,389,391 | -- | 2 |
| Kristaps Marsh | $22,707,433 | -- | 4 |
| Jaylen Kalinic | $8,260,283 | -- | 3 |
| Julian Marsh | $55,920,853 | -- | 1 |

Roster count: 14

We're discussing a trade that sends Elijah Petrov and Zion Cordero to another team for Amari Petrov at $42,085,897. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 34032591, "incoming_salary": 42085897, "max_incoming": 43128591, "matching_rule": "outgoing + $9,096,000 (middle band)", "apron_level": "over the tax line", "apron_salary_after": 214388470, "hard_cap_triggered": "first apron", "violations": ["Houston: hard cap exceeded -- Houston would sit at $214,388,470, above its first apron hard cap of $209,015,000 -- over by $5,373,470"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $34,032,591, $42,085,897, $43,128,591

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Houston
  2. --- Houston (2026-27) --- (apron salary $206,335,164, over the tax line)
  3. Houston outgoing salary = $34,032,591 (Elijah Petrov $29,643,200, Zion Cordero $4,389,391)
  4. Houston incoming salary = $42,085,897 (Amari Petrov $42,085,897)
  5. Houston matching limit = $43,128,591 (outgoing + $9,096,000 (middle band))
  6. Houston hard-capped at the first apron = $209,015,000 (took back more than 100% of outgoing salary)
  7. Houston hard-capped at the second apron = $221,686,000 (aggregated two or more salaries in one trade)
  8. Two hard caps triggered -- the tighter one governs = $209,015,000
  9. Houston apron salary after the trade = $214,388,470
  10. VIOLATION -- hard cap exceeded (Houston would sit at $214,388,470, above its first apron hard cap of $209,015,000 -- over by $5,373,470)
  11. Verdict: ILLEGAL
```


## Scenario 23 -- scenario_planning

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
player,salary,unlikely_incentives,years_remaining
Elijah Brantley,11764023,0,4
Terrance Osei,25508757,0,2
Malik Dumont,54126450,0,2
Nico Lindqvist,12150458,0,3
Bogdan Boateng,4920404,0,1
Cam Vasquez,10065060,0,4
Isaiah Osei,26681478,0,1
Darnell Marsh,17637773,0,4
Deni Brantley,6784632,0,3
Malik Ibarra,9963205,0,2
Darnell Kalinic,8978876,0,1
Kristaps Halvorsen,6676436,0,4
Terrance Halvorsen,4828903,0,1
Deni Rees,9494219,0,1
Amari Cordero,12492680,0,2

Roster count: 15

We need to get under the second apron before the deadline. What are our options, and what are we giving up?
```

**Ground truth:** {"apron_salary": 222073354, "second_apron": 207824000, "overage": 14249354, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Darnell Marsh", "salary": 17637773, "surplus": 3388419}, {"player": "Terrance Osei", "salary": 25508757, "surplus": 11259403}, {"player": "Isaiah Osei", "salary": 26681478, "surplus": 12432124}, {"player": "Malik Dumont", "salary": 54126450, "surplus": 39877096}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $14,249,354

**Computation trace (the only figures you may use):**

```
  1. Washington apron salary = $222,073,354
  2. 2025-26 second apron = $207,824,000
  3. Amount over the second apron = $14,249,354
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Darnell Marsh alone clears the gap = $3,388,419 ($17,637,773 out against $14,249,354 of overage, assuming no salary comes back)
  7. Moving Terrance Osei alone clears the gap = $11,259,403 ($25,508,757 out against $14,249,354 of overage, assuming no salary comes back)
  8. Moving Isaiah Osei alone clears the gap = $12,432,124 ($26,681,478 out against $14,249,354 of overage, assuming no salary comes back)
  9. Moving Malik Dumont alone clears the gap = $39,877,096 ($54,126,450 out against $14,249,354 of overage, assuming no salary comes back)
```


## Scenario 24 -- scenario_planning

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
Nikola Boateng           $13,553,264
Devonte Ferreira         $14,800,002
Devonte Jokubaitis        $8,501,520
Malik Achiuwa             $8,138,936
Amari Whitfield           $8,511,759
Trey Ferreira            $49,205,800
Cam Halvorsen             $7,433,793
Jaylen Nakamura           $9,137,894
Marcus Whitfield          $5,926,264
Luka Stavros             $19,430,495
Devonte Beauchamp        $11,896,138
Rashad Sabonis           $11,186,257
Darnell Rees              $7,460,712
Jaylen Kearns            $14,287,545
Kobe Ibarra              $13,500,871

Roster count: 15

What's the cleanest path under the second apron from here?
```

**Ground truth:** {"apron_salary": 202971250, "second_apron": 188931000, "overage": 14040250, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Jaylen Kearns", "salary": 14287545, "surplus": 247295}, {"player": "Devonte Ferreira", "salary": 14800002, "surplus": 759752}, {"player": "Luka Stavros", "salary": 19430495, "surplus": 5390245}, {"player": "Trey Ferreira", "salary": 49205800, "surplus": 35165550}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $14,040,250

**Computation trace (the only figures you may use):**

```
  1. Brooklyn apron salary = $202,971,250
  2. 2024-25 second apron = $188,931,000
  3. Amount over the second apron = $14,040,250
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Jaylen Kearns alone clears the gap = $247,295 ($14,287,545 out against $14,040,250 of overage, assuming no salary comes back)
  7. Moving Devonte Ferreira alone clears the gap = $759,752 ($14,800,002 out against $14,040,250 of overage, assuming no salary comes back)
  8. Moving Luka Stavros alone clears the gap = $5,390,245 ($19,430,495 out against $14,040,250 of overage, assuming no salary comes back)
  9. Moving Trey Ferreira alone clears the gap = $35,165,550 ($49,205,800 out against $14,040,250 of overage, assuming no salary comes back)
```


## Scenario 25 -- anti_staleness

**What the user said:**

```
2027-28 LEAGUE THRESHOLDS
  Salary cap:          $148,433,000
  Luxury tax line:     $180,345,000
  First apron:         $188,071,000
  Second apron:        $199,473,000
  Non-taxpayer MLE:    $13,537,000
  Taxpayer MLE:        $5,456,000
  Room exception:      $8,428,000
  Tax bracket width:   $5,456,000
  Bi-annual exception: $5,279,000

HOUSTON -- 2027-28 CAP SHEET
Elijah Marsh             $4,850,682
Andre Ibarra            $46,121,998
Marcus Ferreira         $24,357,912
Luka Petrov              $4,417,559
Amari Okoro              $6,360,660
Santi Vasquez           $36,747,591
Tobias Ferreira         $24,214,251
Darnell Duval            $3,620,937
Tobias Brantley         $11,833,456
Jalil Dumont             $8,217,375
Brennan Vasquez          $7,798,284
Kristaps Ferreira        $7,796,968
Deni Reddish             $5,517,541
Jalil Okoro              $3,593,386

Roster count: 14

Using the 2027-28 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2027-28", "apron_salary": 195448600, "apron_level": "over the first apron", "first_apron_provided": 188071000, "second_apron_provided": 199473000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $195,448,600, $199,473,000

**Computation trace (the only figures you may use):**

```
  1. Houston apron salary = $195,448,600
  2. 2027-28 first apron (from the figures provided) = $188,071,000
  3. 2027-28 second apron (from the figures provided) = $199,473,000
  4. Position: over the first apron
  5. Room below the second apron = $4,024,400
```


## Scenario 26 -- trade_legality

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
| Devonte Vasquez | $4,220,792 | -- | 1 |
| Deni Rees | $2,866,493 | -- | 4 |
| Alperen Lindqvist | $2,290,148 | -- | 1 |
| Marcus Rees | $8,862,785 | -- | 4 |
| Alperen Petrov | $4,096,388 | -- | 2 |
| Deni Osei | $4,990,500 | -- | 2 |
| Julian Ferreira | $30,614,745 | -- | 3 |
| Rashad Petrov | $11,323,561 | -- | 3 |
| Kristaps Brantley | $2,884,797 | -- | 1 |
| Jaylen Beauchamp | $5,268,169 | -- | 3 |
| Malik Beauchamp | $8,675,453 | -- | 2 |
| Jalil Dumont | $14,585,635 | -- | 3 |
| Rashad Halvorsen | $5,511,164 | -- | 3 |
| Rashad Jokubaitis | $29,023,754 | -- | 4 |

Roster count: 14

We're discussing a trade that sends Julian Ferreira and Rashad Petrov to another team for Kristaps Boateng at $51,019,678. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 41938306, "incoming_salary": 51019678, "max_incoming": 52672882, "matching_rule": "125% + $250,000 (outgoing above $29,974,000)", "apron_level": "under the tax line", "apron_salary_after": 144295756, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $41,938,306, $51,019,678, $52,672,882

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Chicago
  2. --- Chicago (2024-25) --- (apron salary $135,214,384, under the tax line)
  3. Chicago outgoing salary = $41,938,306 (Julian Ferreira $30,614,745, Rashad Petrov $11,323,561)
  4. Chicago incoming salary = $51,019,678 (Kristaps Boateng $51,019,678)
  5. Chicago matching limit = $52,672,882 (125% + $250,000 (outgoing above $29,974,000))
  6. Chicago hard-capped at the first apron = $178,132,000 (took back more than 100% of outgoing salary)
  7. Chicago hard-capped at the second apron = $188,931,000 (aggregated two or more salaries in one trade)
  8. Two hard caps triggered -- the tighter one governs = $178,132,000
  9. Chicago apron salary after the trade = $144,295,756
  10. Chicago stays under its first apron hard cap = $33,836,244 ($178,132,000 - $144,295,756 of room to spare)
  11. Verdict: LEGAL
```


## Scenario 27 -- exception_eligibility

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
| Kobe Kearns | $2,768,181 | -- | 4 |
| Nico Dumont | $8,192,525 | -- | 2 |
| Alperen Jokubaitis | $6,132,967 | -- | 3 |
| Nico Okoro | $3,232,928 | -- | 3 |
| Amari Dumont | $57,288,732 | -- | 3 |
| Terrance Reddish | $18,217,573 | -- | 4 |
| Cam Ibarra | $5,746,509 | -- | 3 |
| Elijah Ferreira | $9,059,599 | -- | 3 |
| Deni Okoro | $8,963,817 | -- | 4 |
| Goran Sabonis | $48,576,433 | -- | 2 |
| Cam Kalinic | $7,081,469 | -- | 4 |
| Amari Brantley | $27,649,893 | -- | 4 |
| Tobias Cordero | $4,753,544 | -- | 2 |

Roster count: 13

Can we sign Marcus Kearns for $12,236,142 using the non-taxpayer mid-level exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "non-taxpayer mid-level exception", "salary": 12236142, "hard_cap_triggered": "none", "apron_level": "over the tax line", "apron_salary_after": 219900312, "reasons": ["the signing would put Sacramento at $219,900,312, above its first apron hard cap of $209,015,000"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $12,236,142

**Computation trace (the only figures you may use):**

```
  1. Sacramento apron salary before signing = $207,664,170 (over the tax line)
  2. Proposed salary for Marcus Kearns = $12,236,142
  3. Exception: non-taxpayer mid-level exception
  4. non-taxpayer mid-level exception maximum = $15,044,000
  5. Room remaining within the exception = $2,807,858
  6. Sacramento apron salary after signing = $219,900,312
  7. Hard cap: first apron = $209,015,000
  8. VIOLATION -- hard cap exceeded = $10,885,312
  9. Verdict: ILLEGAL
```


## Scenario 28 -- anti_staleness

**What the user said:**

```
2027-28 LEAGUE THRESHOLDS
  Salary cap:          $165,164,000
  Luxury tax line:     $200,673,000
  First apron:         $209,270,000
  Second apron:        $221,957,000
  Non-taxpayer MLE:    $15,063,000
  Taxpayer MLE:        $6,072,000
  Room exception:      $9,378,000
  Tax bracket width:   $6,072,000
  Bi-annual exception: $5,340,000

DETROIT -- 2027-28 CAP SHEET
Nikola Achiuwa        $29,208,172
Corey Sabonis          $7,949,703
Darnell Reddish       $11,098,260
Malik Cordero         $13,485,025
Cam Marsh              $8,665,920
Kellen Dumont         $18,148,993
Alperen Dumont        $57,807,400
Cam Cordero            $7,659,323
Devonte Kalinic       $12,150,275
Devonte Novak         $11,599,492
Alperen Novak          $9,132,566
Malik Halvorsen        $4,226,294
Corey Okoro           $12,742,836

Roster count: 13

Using the 2027-28 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2027-28", "apron_salary": 203874259, "apron_level": "over the tax line", "first_apron_provided": 209270000, "second_apron_provided": 221957000, "would_be_wrong_using_published_figures": "over the first apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $203,874,259, $221,957,000

**Computation trace (the only figures you may use):**

```
  1. Detroit apron salary = $203,874,259
  2. 2027-28 first apron (from the figures provided) = $209,270,000
  3. 2027-28 second apron (from the figures provided) = $221,957,000
  4. Position: over the tax line
  5. Room below the second apron = $18,082,741
```


## Scenario 29 -- hard_cap_consequence

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

MIAMI -- 2026-27 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Nikola Stavros,7119941,0,3
Rashad Kearns,3604269,0,3
Malik Novak,56503053,0,1
Goran Boateng,5207938,0,3
Trey Osei,17350222,0,2
Trey Halvorsen,8977137,0,4
Alperen Nakamura,47538303,0,2
Andre Cordero,19466343,0,4
Terrance Okoro,6326935,0,3
Deni Kearns,4106293,0,3
Elijah Marsh,8521832,0,1
Amari Lindqvist,8035729,0,4
Cam Reddish,4499929,0,4
Corey Kalinic,7700132,0,3

Roster count: 14
Hard cap: first apron

We're hard-capped at the first apron. Can we add Jaylen Whitfield at $4,559,738?
```

**Ground truth:** {"legal": false, "hard_cap": "first apron", "hard_cap_limit": 209015000, "room_below_hard_cap": 4056944, "salary": 4559738, "apron_salary_after": 209517794, "reasons": ["the signing would put Miami at $209,517,794, above its first apron hard cap of $209,015,000"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $4,559,738, $209,015,000

**Computation trace (the only figures you may use):**

```
  1. Miami apron salary before signing = $204,958,056 (over the tax line)
  2. Proposed salary for Jaylen Whitfield = $4,559,738
  3. Exception: minimum salary exception
  4. Miami apron salary after signing = $209,517,794
  5. Hard cap: first apron = $209,015,000
  6. VIOLATION -- hard cap exceeded = $502,794
  7. Verdict: ILLEGAL
  8. Room below the first apron hard cap before signing = $4,056,944 ($209,015,000 - $204,958,056)
```


## Scenario 30 -- trade_legality

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
Isaiah Kearns,6012723,0,2
Trey Kearns,25275863,0,2
Nico Amadi,8196265,0,4
Andre Lindqvist,22738161,0,3
Zion Ellington,8987458,0,1
Trey Petrov,3852381,0,4
Devonte Reddish,8232416,0,2
Micah Kalinic,3373618,0,4
Kristaps Reddish,7862721,0,1
Jaylen Boateng,50746454,0,2
Luka Dumont,4910798,0,1
Corey Boateng,4231981,0,3
Bogdan Sabonis,4926529,0,1
Isaiah Cordero,2719328,0,1
Elijah Petrov,26904613,0,1

Roster count: 15

We're discussing a trade that sends Jaylen Boateng to another team for Devonte Duval at $52,158,869. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 50746454, "incoming_salary": 52158869, "max_incoming": 63683067, "matching_rule": "125% + $250,000 (outgoing above $32,971,000)", "apron_level": "over the tax line", "apron_salary_after": 190383724, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $50,746,454, $52,158,869, $63,683,067

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Orlando
  2. --- Orlando (2025-26) --- (apron salary $188,971,309, over the tax line)
  3. Orlando outgoing salary = $50,746,454 (Jaylen Boateng $50,746,454)
  4. Orlando incoming salary = $52,158,869 (Devonte Duval $52,158,869)
  5. Orlando matching limit = $63,683,067 (125% + $250,000 (outgoing above $32,971,000))
  6. Orlando hard-capped at the first apron = $195,945,000 (took back more than 100% of outgoing salary)
  7. Orlando apron salary after the trade = $190,383,724
  8. Orlando stays under its first apron hard cap = $5,561,276 ($195,945,000 - $190,383,724 of room to spare)
  9. Verdict: LEGAL
```


## Scenario 31 -- scenario_planning

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
player,salary,unlikely_incentives,years_remaining
Brennan Osei,41716964,0,2
Luka Stavros,7534512,0,1
Malik Beauchamp,6024852,0,3
Santi Amadi,7092263,0,1
Marcus Petrov,6069831,0,4
Dante Beauchamp,3012100,0,2
Trey Dumont,9322382,0,2
Rashad Boateng,7165964,0,4
Cam Rees,41843121,0,2
Dante Brantley,8122936,0,4
Jaylen Halvorsen,5504372,0,4
Elijah Okoro,29772783,0,2
Jaylen Ellington,2549439,0,4
Goran Lindqvist,8843636,0,4
Corey Nakamura,23353585,0,2

Roster count: 15

What's the cleanest path under the second apron from here?
```

**Ground truth:** {"apron_salary": 207928740, "second_apron": 188931000, "overage": 18997740, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Corey Nakamura", "salary": 23353585, "surplus": 4355845}, {"player": "Elijah Okoro", "salary": 29772783, "surplus": 10775043}, {"player": "Brennan Osei", "salary": 41716964, "surplus": 22719224}, {"player": "Cam Rees", "salary": 41843121, "surplus": 22845381}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $18,997,740

**Computation trace (the only figures you may use):**

```
  1. Toronto apron salary = $207,928,740
  2. 2024-25 second apron = $188,931,000
  3. Amount over the second apron = $18,997,740
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Corey Nakamura alone clears the gap = $4,355,845 ($23,353,585 out against $18,997,740 of overage, assuming no salary comes back)
  7. Moving Elijah Okoro alone clears the gap = $10,775,043 ($29,772,783 out against $18,997,740 of overage, assuming no salary comes back)
  8. Moving Brennan Osei alone clears the gap = $22,719,224 ($41,716,964 out against $18,997,740 of overage, assuming no salary comes back)
  9. Moving Cam Rees alone clears the gap = $22,845,381 ($41,843,121 out against $18,997,740 of overage, assuming no salary comes back)
```


## Scenario 32 -- scenario_planning

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
Goran Novak                $7,666,001
Julian Vasquez            $24,519,796
Rashad Ellington           $7,898,521
Kobe Nakamura             $14,882,451
Zion Dumont                $8,620,798
Isaiah Osei               $56,538,732
Nico Jokubaitis            $4,699,678
Brennan Vasquez            $6,728,495
Terrance Jokubaitis        $7,244,598
Corey Novak                $7,619,070
Kellen Boateng            $57,736,350
Jalil Brantley             $5,860,307
Zion Duval                 $8,339,899
Luka Novak                $11,949,228
Zion Ibarra               $10,093,578

Roster count: 15

Ownership wants us out of the second apron. Walk me through how we do it.
```

**Ground truth:** {"apron_salary": 240397502, "second_apron": 221686000, "overage": 18711502, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Julian Vasquez", "salary": 24519796, "surplus": 5808294}, {"player": "Isaiah Osei", "salary": 56538732, "surplus": 37827230}, {"player": "Kellen Boateng", "salary": 57736350, "surplus": 39024848}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $18,711,502

**Computation trace (the only figures you may use):**

```
  1. Detroit apron salary = $240,397,502
  2. 2026-27 second apron = $221,686,000
  3. Amount over the second apron = $18,711,502
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Julian Vasquez alone clears the gap = $5,808,294 ($24,519,796 out against $18,711,502 of overage, assuming no salary comes back)
  7. Moving Isaiah Osei alone clears the gap = $37,827,230 ($56,538,732 out against $18,711,502 of overage, assuming no salary comes back)
  8. Moving Kellen Boateng alone clears the gap = $39,024,848 ($57,736,350 out against $18,711,502 of overage, assuming no salary comes back)
```


## Scenario 33 -- exception_survey

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
| Santi Beauchamp | $2,717,835 | -- | 4 |
| Rashad Kearns | $7,149,423 | -- | 3 |
| Jaylen Duval | $10,893,192 | -- | 4 |
| Nico Rees | $49,325,706 | -- | 2 |
| Kellen Achiuwa | $6,691,355 | -- | 3 |
| Kristaps Lindqvist | $7,029,507 | -- | 3 |
| Nikola Sabonis | $7,575,695 | -- | 3 |
| Cam Kearns | $11,065,267 | -- | 3 |
| Elijah Lindqvist | $8,262,736 | -- | 1 |
| Goran Beauchamp | $45,957,576 | -- | 2 |
| Micah Nakamura | $10,958,623 | -- | 3 |
| Luka Beauchamp | $20,370,054 | -- | 2 |
| Micah Lindqvist | $5,536,251 | -- | 4 |

Roster count: 13

What signing exceptions do we still have available, and what does using each one cost us?
```

**Ground truth:** {"apron_level": "under the tax line", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": true, "amount": 15044000, "reason": "available at $15,044,000; using it hard-caps the team at the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 6064000, "reason": "available at $6,064,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": true, "amount": 5477000, "reason": "available at $5,477,000; using it hard-caps the team at the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Indiana apron salary = $193,533,220 (under the tax line)
  2. 2026-27 first apron = $209,015,000
  3. 2026-27 second apron = $221,686,000
  4. non-taxpayer mid-level exception: available = $15,044,000 (available at $15,044,000; using it hard-caps the team at the first apron)
  5. taxpayer mid-level exception: available = $6,064,000 (available at $6,064,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: available = $5,477,000 (available at $5,477,000; using it hard-caps the team at the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 34 -- trade_legality

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
Brennan Ibarra          $9,308,314
Nikola Beauchamp       $35,907,088
Kellen Whitfield        $5,492,496
Tobias Ibarra          $10,184,246
Rashad Marsh            $4,343,816
Jaylen Kalinic         $13,336,460
Julian Brantley        $49,205,800
Zion Cordero            $5,476,114
Micah Beauchamp        $26,950,674
Trey Whitfield         $23,254,711
Julian Ibarra           $7,441,064
Dante Cordero           $4,985,566
Rashad Boateng          $7,495,028
Micah Boateng           $3,933,420

Roster count: 14

We're discussing a trade that sends Rashad Marsh to another team for Corey Amadi at $5,164,407. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 4343816, "incoming_salary": 5164407, "max_incoming": 4343816, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 208135388, "hard_cap_triggered": "none", "violations": ["Charlotte: salary matching -- Charlotte takes back $5,164,407 but may only absorb $4,343,816 under 100% of outgoing salary (team is over the first apron) -- over by $820,591"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $4,343,816, $5,164,407, $4,343,816

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Charlotte
  2. --- Charlotte (2024-25) --- (apron salary $207,314,797, over the second apron)
  3. Charlotte outgoing salary = $4,343,816 (Rashad Marsh $4,343,816)
  4. Charlotte incoming salary = $5,164,407 (Corey Amadi $5,164,407)
  5. Charlotte matching limit = $4,343,816 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (Charlotte takes back $5,164,407 but may only absorb $4,343,816 under 100% of outgoing salary (team is over the first apron) -- over by $820,591)
  7. Charlotte apron salary after the trade = $208,135,388
  8. Verdict: ILLEGAL
```


## Scenario 35 -- tax_bill

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
Nico Dumont            $9,008,530
Jaylen Duval          $10,121,694
Andre Boateng         $10,176,049
Kellen Vasquez        $42,385,061
Jalil Kearns           $8,518,194
Devonte Okoro          $6,057,163
Cam Jokubaitis        $19,406,967
Goran Kalinic          $3,982,180
Bogdan Reddish         $3,049,436
Kobe Vasquez          $49,205,800
Amari Vasquez          $3,488,474
Trey Jokubaitis        $6,305,399
Nico Reddish           $5,603,117

Roster count: 13

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 177308064, "tax_line": 170814000, "amount_over": 6494064, "is_repeater": false, "total": 10072612, "brackets": [{"index": 1, "amount": 5168000, "rate": 1.5, "owed": 7752000}, {"index": 2, "amount": 1326064, "rate": 1.75, "owed": 2320612}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $10,072,612, $6,494,064

**Computation trace (the only figures you may use):**

```
  1. Charlotte tax salary = $177,308,064
  2. 2024-25 luxury tax line = $170,814,000
  3. Amount over the tax line = $6,494,064 ($177,308,064 - $170,814,000)
  4. Rate schedule: standard (2024-25) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $5,168,000 at $1.50 per dollar = $7,752,000
  6. Bracket 2: $1,326,064 at $1.75 per dollar = $2,320,612
  7. Total luxury tax owed = $10,072,612
  8. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 36 -- trade_legality

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
Alperen Nakamura       $10,140,949
Malik Beauchamp        $13,142,184
Goran Amadi             $5,854,599
Corey Okoro            $12,725,545
Corey Rees              $6,982,640
Malik Ibarra            $7,441,286
Nikola Halvorsen       $11,616,954
Jaylen Kalinic          $7,772,939
Marcus Ferreira        $30,066,056
Elijah Lindqvist       $54,126,450
Dante Ibarra            $9,806,657
Luka Duval             $14,709,727
Isaiah Stavros          $6,040,659
Devonte Stavros        $23,755,820

Roster count: 14

We're discussing a trade that sends Goran Amadi to another team for Andre Whitfield at $6,346,959. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 5854599, "incoming_salary": 6346959, "max_incoming": 5854599, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 214674825, "hard_cap_triggered": "none", "violations": ["San Antonio: salary matching -- San Antonio takes back $6,346,959 but may only absorb $5,854,599 under 100% of outgoing salary (team is over the first apron) -- over by $492,360"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $5,854,599, $6,346,959, $5,854,599

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: San Antonio
  2. --- San Antonio (2025-26) --- (apron salary $214,182,465, over the second apron)
  3. San Antonio outgoing salary = $5,854,599 (Goran Amadi $5,854,599)
  4. San Antonio incoming salary = $6,346,959 (Andre Whitfield $6,346,959)
  5. San Antonio matching limit = $5,854,599 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (San Antonio takes back $6,346,959 but may only absorb $5,854,599 under 100% of outgoing salary (team is over the first apron) -- over by $492,360)
  7. San Antonio apron salary after the trade = $214,674,825
  8. Verdict: ILLEGAL
```


## Scenario 37 -- trade_legality

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
Kellen Sabonis          $14,348,068
Elijah Cordero           $4,953,949
Zion Marsh              $16,776,923
Nikola Osei              $3,575,780
Amari Halvorsen          $4,957,823
Nico Amadi               $2,564,365
Micah Ellington         $29,953,626
Darnell Dumont           $8,129,995
Dante Ferreira           $8,229,776
Bogdan Lindqvist         $8,855,661
Darnell Beauchamp        $4,365,464
Deni Kalinic             $7,725,114
Micah Reddish            $4,465,056
Terrance Petrov         $27,126,127
Isaiah Okoro            $52,904,414

Roster count: 15

We're discussing a trade that sends Isaiah Okoro and Amari Halvorsen to another team for Alperen Ferreira at $54,932,682. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 57862237, "incoming_salary": 54932682, "max_incoming": 57862237, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 196002586, "hard_cap_triggered": "second apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $57,862,237, $54,932,682, $57,862,237

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Sacramento
  2. --- Sacramento (2025-26) --- (apron salary $198,932,141, over the first apron)
  3. Sacramento outgoing salary = $57,862,237 (Isaiah Okoro $52,904,414, Amari Halvorsen $4,957,823)
  4. Sacramento incoming salary = $54,932,682 (Alperen Ferreira $54,932,682)
  5. Sacramento matching limit = $57,862,237 (100% of outgoing salary (team is over the first apron))
  6. Sacramento hard-capped at the second apron = $207,824,000 (aggregated two or more salaries in one trade)
  7. Sacramento apron salary after the trade = $196,002,586
  8. Sacramento stays under its second apron hard cap = $11,821,414 ($207,824,000 - $196,002,586 of room to spare)
  9. Verdict: LEGAL
```


## Scenario 38 -- hard_cap_consequence

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Darnell Beauchamp | $8,413,112 | -- | 2 |
| Deni Marsh | $54,004,193 | -- | 2 |
| Santi Cordero | $8,806,045 | -- | 4 |
| Alperen Reddish | $3,649,130 | -- | 4 |
| Kristaps Beauchamp | $31,362,108 | -- | 2 |
| Malik Stavros | $29,241,741 | -- | 3 |
| Kobe Whitfield | $2,746,268 | -- | 2 |
| Tobias Whitfield | $14,023,693 | -- | 2 |
| Amari Halvorsen | $2,896,920 | -- | 4 |
| Micah Ellington | $6,986,106 | -- | 1 |
| Andre Osei | $3,294,617 | -- | 4 |
| Kristaps Reddish | $4,182,482 | -- | 4 |
| Rashad Kearns | $6,746,648 | -- | 3 |
| Isaiah Dumont | $6,658,852 | -- | 4 |
| Santi Beauchamp | $8,238,973 | -- | 2 |

Roster count: 15
Hard cap: first apron

We're hard-capped at the first apron. Can we add Brennan Achiuwa at $6,415,797?
```

**Ground truth:** {"legal": false, "hard_cap": "first apron", "hard_cap_limit": 195945000, "room_below_hard_cap": 4694112, "salary": 6415797, "apron_salary_after": 197666685, "reasons": ["the signing would put Washington at $197,666,685, above its first apron hard cap of $195,945,000", "Washington already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $6,415,797, $195,945,000

**Computation trace (the only figures you may use):**

```
  1. Washington apron salary before signing = $191,250,888 (over the tax line)
  2. Proposed salary for Brennan Achiuwa = $6,415,797
  3. Exception: minimum salary exception
  4. Washington apron salary after signing = $197,666,685
  5. Hard cap: first apron = $195,945,000
  6. VIOLATION -- hard cap exceeded = $1,721,685
  7. VIOLATION -- roster is full (15-man limit reached)
  8. Verdict: ILLEGAL
  9. Room below the first apron hard cap before signing = $4,694,112 ($195,945,000 - $191,250,888)
```


## Scenario 39 -- exception_survey

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
Jalil Jokubaitis        $8,063,314
Dante Jokubaitis       $10,365,686
Rashad Novak           $31,414,936
Kellen Cordero         $17,545,621
Julian Boateng          $8,413,561
Alperen Ferreira        $7,364,551
Devonte Okoro           $7,264,624
Bogdan Boateng          $4,674,276
Corey Rees              $3,834,791
Cam Vasquez            $57,736,350
Elijah Halvorsen        $8,102,874
Dante Vasquez          $17,556,969
Micah Marsh            $18,209,248
Devonte Kalinic         $8,807,826
Jalil Okoro             $5,655,273

Roster count: 15

Which exceptions can we actually use at this payroll?
```

**Ground truth:** {"apron_level": "over the first apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 6064000, "reason": "available at $6,064,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Orlando apron salary = $215,009,900 (over the first apron)
  2. 2026-27 first apron = $209,015,000
  3. 2026-27 second apron = $221,686,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: available = $6,064,000 (available at $6,064,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: unavailable (unavailable over the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


