# Writing batch 4

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

Write one JSON object per line to `/tmp/rexport/batch4_responses.jsonl`, nothing else in the file:

    {"id": 0, "response": "**Verdict: ILLEGAL.** ..."}

The `id` must match the scenario number below.

---

## Scenario 0 -- trade_legality

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

PORTLAND -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Alperen Okoro,2088000,0,1
Kellen Okoro,6697643,0,1
Jalil Amadi,4412331,0,3
Jalil Halvorsen,2088000,0,1
Kristaps Kearns,6504640,0,2
Nico Lindqvist,3509954,0,4
Luka Duval,2223804,0,4
Rashad Boateng,6306554,0,4
Cam Amadi,28192572,0,4
Jalil Rees,15988526,0,2
Devonte Jokubaitis,18226289,0,3
Deni Osei,35212517,0,2
Jaylen Lindqvist,6589192,0,1

Roster count: 13

We're discussing a trade that sends Cam Amadi and Kellen Okoro to another team for Goran Boateng at $43,183,713. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 34890215, "incoming_salary": 43183713, "max_incoming": 43862768, "matching_rule": "125% + $250,000 (outgoing above $29,974,000)", "apron_level": "under the tax line", "apron_salary_after": 146333520, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $34,890,215, $43,183,713, $43,862,768

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Portland
  2. --- Portland (2024-25) --- (apron salary $138,040,022, under the tax line)
  3. Portland outgoing salary = $34,890,215 (Cam Amadi $28,192,572, Kellen Okoro $6,697,643)
  4. Portland incoming salary = $43,183,713 (Goran Boateng $43,183,713)
  5. Portland matching limit = $43,862,768 (125% + $250,000 (outgoing above $29,974,000))
  6. Portland hard-capped at the first apron = $178,132,000 (took back more than 100% of outgoing salary)
  7. Portland hard-capped at the second apron = $188,931,000 (aggregated two or more salaries in one trade)
  8. Two hard caps triggered -- the tighter one governs = $178,132,000
  9. Portland apron salary after the trade = $146,333,520
  10. Portland stays under its first apron hard cap = $31,798,480 ($178,132,000 - $146,333,520 of room to spare)
  11. Verdict: LEGAL
```


## Scenario 1 -- scenario_planning

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

NEW ORLEANS -- 2026-27 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Andre Marsh,14711466,0,4
Kellen Reddish,10425178,0,3
Nikola Jokubaitis,6183092,0,1
Rashad Rees,18340478,0,2
Goran Nakamura,5801205,0,2
Rashad Dumont,10619327,0,1
Nikola Whitfield,57736350,0,2
Andre Achiuwa,10957443,0,4
Amari Sabonis,5896292,0,1
Marcus Boateng,11857070,0,1
Alperen Kearns,12151633,0,4
Devonte Lindqvist,5482077,0,3
Jaylen Brantley,13964890,0,4
Devonte Ibarra,9254718,0,3
Amari Whitfield,44797109,0,1

Roster count: 15

Ownership wants us out of the second apron. Walk me through how we do it.
```

**Ground truth:** {"apron_salary": 238178328, "second_apron": 221686000, "overage": 16492328, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Rashad Rees", "salary": 18340478, "surplus": 1848150}, {"player": "Amari Whitfield", "salary": 44797109, "surplus": 28304781}, {"player": "Nikola Whitfield", "salary": 57736350, "surplus": 41244022}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $16,492,328

**Computation trace (the only figures you may use):**

```
  1. New Orleans apron salary = $238,178,328
  2. 2026-27 second apron = $221,686,000
  3. Amount over the second apron = $16,492,328
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Rashad Rees alone clears the gap = $1,848,150 ($18,340,478 out against $16,492,328 of overage, assuming no salary comes back)
  7. Moving Amari Whitfield alone clears the gap = $28,304,781 ($44,797,109 out against $16,492,328 of overage, assuming no salary comes back)
  8. Moving Nikola Whitfield alone clears the gap = $41,244,022 ($57,736,350 out against $16,492,328 of overage, assuming no salary comes back)
```


## Scenario 2 -- apron_status

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
Kobe Jokubaitis,4103922,0,1
Julian Dumont,2296000,0,4
Trey Rees,25621648,0,2
Kellen Novak,7086504,0,3
Trey Ibarra,36447746,0,1
Luka Beauchamp,46854594,0,3
Santi Marsh,5238158,0,1
Devonte Lindqvist,3848612,0,1
Dante Duval,3623511,0,2
Luka Rees,2909779,0,2
Jaylen Nakamura,21018758,0,4
Brennan Kalinic,2296000,0,3
Nikola Rees,3664987,0,1

Roster count: 13

Are we over the second apron? How much room do we have?
```

**Ground truth:** {"tax_salary": 165010219, "unlikely_incentives": 0, "apron_salary": 165010219, "apron_level": "under the tax line", "room_to_first_apron": 30934781, "room_to_second_apron": 42813781}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $165,010,219

**Computation trace (the only figures you may use):**

```
  1. Memphis salaries plus likely incentives = $165,010,219
  2. Apron salary = $165,010,219
  3. 2025-26 luxury tax line = $187,895,000
  4. 2025-26 first apron = $195,945,000
  5. 2025-26 second apron = $207,824,000
  6. Position: under the tax line
  7. Room below the tax line = $22,884,781
  8. Room below the first apron = $30,934,781
  9. Room below the second apron = $42,813,781
```


## Scenario 3 -- trade_legality

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
Marcus Duval,45345464,0,2
Malik Boateng,4071275,0,3
Luka Novak,4198295,0,4
Amari Halvorsen,7653133,0,4
Marcus Nakamura,7187375,0,3
Andre Marsh,23603183,0,4
Goran Whitfield,8223596,0,4
Santi Beauchamp,7820337,0,3
Kellen Whitfield,5663405,0,1
Jalil Nakamura,8463676,0,1
Rashad Dumont,4460025,0,1
Goran Sabonis,5701227,0,1
Jaylen Osei,8736237,0,1
Kellen Novak,24998679,0,2

Roster count: 14

We're discussing a trade that sends Luka Novak to another team for Marcus Ferreira at $7,632,522. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 4198295, "incoming_salary": 7632522, "max_incoming": 8646590, "matching_rule": "200% + $250,000 (outgoing at or below $9,096,000)", "apron_level": "under the tax line", "apron_salary_after": 169560134, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $4,198,295, $7,632,522, $8,646,590

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Chicago
  2. --- Chicago (2026-27) --- (apron salary $166,125,907, under the tax line)
  3. Chicago outgoing salary = $4,198,295 (Luka Novak $4,198,295)
  4. Chicago incoming salary = $7,632,522 (Marcus Ferreira $7,632,522)
  5. Chicago matching limit = $8,646,590 (200% + $250,000 (outgoing at or below $9,096,000))
  6. Chicago hard-capped at the first apron = $209,015,000 (took back more than 100% of outgoing salary)
  7. Chicago apron salary after the trade = $169,560,134
  8. Chicago stays under its first apron hard cap = $39,454,866 ($209,015,000 - $169,560,134 of room to spare)
  9. Verdict: LEGAL
```


## Scenario 4 -- tax_bill

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
Cam Sabonis,7280682,0,1
Brennan Lindqvist,9375543,0,3
Micah Lindqvist,6599951,0,1
Luka Amadi,7127664,0,2
Terrance Ibarra,12710504,0,1
Cam Lindqvist,5474902,0,2
Dante Jokubaitis,8605083,0,1
Nikola Lindqvist,21301273,0,3
Isaiah Vasquez,54126450,0,4
Kristaps Stavros,30130829,0,4
Cam Brantley,35858110,0,4
Brennan Reddish,6525809,0,2
Marcus Jokubaitis,6423469,0,3
Santi Sabonis,5468824,0,1
Alperen Novak,4799300,0,3

Roster count: 15

What's our luxury tax bill this season? Walk me through the brackets.
```

**Ground truth:** {"tax_salary": 221808393, "tax_line": 187895000, "amount_over": 33913393, "is_repeater": false, "total": 121097010, "brackets": [{"index": 1, "amount": 5685000, "rate": 1.0, "owed": 5685000}, {"index": 2, "amount": 5685000, "rate": 1.25, "owed": 7106250}, {"index": 3, "amount": 5685000, "rate": 3.5, "owed": 19897500}, {"index": 4, "amount": 5685000, "rate": 4.75, "owed": 27003750}, {"index": 5, "amount": 5685000, "rate": 5.25, "owed": 29846250}, {"index": 6, "amount": 5488393, "rate": 5.75, "owed": 31558260}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $121,097,010, $33,913,393

**Computation trace (the only figures you may use):**

```
  1. Brooklyn tax salary = $221,808,393
  2. 2025-26 luxury tax line = $187,895,000
  3. Amount over the tax line = $33,913,393 ($221,808,393 - $187,895,000)
  4. Rate schedule: standard (2025-26) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $5,685,000 at $1.00 per dollar = $5,685,000
  6. Bracket 2: $5,685,000 at $1.25 per dollar = $7,106,250
  7. Bracket 3: $5,685,000 at $3.50 per dollar = $19,897,500
  8. Bracket 4: $5,685,000 at $4.75 per dollar = $27,003,750
  9. Bracket 5: $5,685,000 at $5.25 per dollar = $29,846,250
  10. Bracket 6: $5,488,393 at $5.75 per dollar = $31,558,260
  11. Total luxury tax owed = $121,097,010
  12. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
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

WASHINGTON -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Marcus Nakamura,7117515,0,2
Amari Ellington,2465997,0,3
Kristaps Kalinic,42585082,0,2
Jaylen Dumont,6674114,0,3
Kristaps Beauchamp,8946261,0,1
Nico Kalinic,5765857,0,4
Bogdan Marsh,3038392,0,4
Elijah Petrov,3156977,0,2
Jaylen Novak,4480973,0,3
Terrance Ellington,7059684,0,4
Kristaps Reddish,5394916,0,2
Andre Halvorsen,27192977,0,3
Elijah Kalinic,2476175,0,1
Amari Duval,53598830,0,3
Corey Vasquez,23943664,0,2

Roster count: 15

We're discussing a trade that sends Nico Kalinic to another team for Jalil Jokubaitis at $6,033,582. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 5765857, "incoming_salary": 6033582, "max_incoming": 5765857, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 204165139, "hard_cap_triggered": "none", "violations": ["Washington: salary matching -- Washington takes back $6,033,582 but may only absorb $5,765,857 under 100% of outgoing salary (team is over the first apron) -- over by $267,725"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $5,765,857, $6,033,582, $5,765,857

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Washington
  2. --- Washington (2025-26) --- (apron salary $203,897,414, over the first apron)
  3. Washington outgoing salary = $5,765,857 (Nico Kalinic $5,765,857)
  4. Washington incoming salary = $6,033,582 (Jalil Jokubaitis $6,033,582)
  5. Washington matching limit = $5,765,857 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (Washington takes back $6,033,582 but may only absorb $5,765,857 under 100% of outgoing salary (team is over the first apron) -- over by $267,725)
  7. Washington apron salary after the trade = $204,165,139
  8. Verdict: ILLEGAL
```


## Scenario 6 -- anti_staleness

**What the user said:**

```
2029-30 LEAGUE THRESHOLDS
  Salary cap:          $148,148,000
  Luxury tax line:     $179,999,000
  First apron:         $187,710,000
  Second apron:        $199,090,000
  Non-taxpayer MLE:    $13,511,000
  Taxpayer MLE:        $5,446,000
  Room exception:      $8,412,000
  Tax bracket width:   $5,446,000
  Bi-annual exception: $5,269,000

ATLANTA -- 2029-30 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Andre Marsh,9161703,0,2
Darnell Marsh,7509771,0,2
Luka Rees,5768925,0,2
Cam Kalinic,24412775,0,4
Cam Whitfield,5447177,0,2
Jaylen Rees,6398011,0,1
Corey Osei,9663373,0,1
Bogdan Halvorsen,3943734,0,2
Micah Vasquez,8187783,0,4
Bogdan Ferreira,6614878,0,1
Terrance Amadi,3981621,0,3
Nikola Petrov,44514761,0,4
Deni Kearns,12675339,0,2
Amari Petrov,4734261,0,1
Kellen Brantley,43296875,0,1

Roster count: 15

Using the 2029-30 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2029-30", "apron_salary": 196310987, "apron_level": "over the first apron", "first_apron_provided": 187710000, "second_apron_provided": 199090000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $196,310,987, $199,090,000

**Computation trace (the only figures you may use):**

```
  1. Atlanta apron salary = $196,310,987
  2. 2029-30 first apron (from the figures provided) = $187,710,000
  3. 2029-30 second apron (from the figures provided) = $199,090,000
  4. Position: over the first apron
  5. Room below the second apron = $2,779,013
```


## Scenario 7 -- trade_legality

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
| Kellen Marsh | $44,668,866 | -- | 2 |
| Andre Whitfield | $46,163,572 | -- | 1 |
| Trey Ellington | $6,155,002 | -- | 4 |
| Elijah Ferreira | $6,695,491 | -- | 1 |
| Bogdan Petrov | $29,603,072 | -- | 1 |
| Bogdan Ellington | $7,848,331 | -- | 2 |
| Rashad Okoro | $8,902,338 | -- | 2 |
| Zion Novak | $16,342,933 | -- | 4 |
| Nico Ibarra | $5,874,522 | -- | 3 |
| Corey Petrov | $3,899,843 | -- | 3 |
| Cam Kearns | $6,838,403 | -- | 1 |
| Jaylen Novak | $7,675,725 | -- | 2 |
| Marcus Kearns | $27,426,695 | -- | 2 |
| Goran Boateng | $8,231,542 | -- | 3 |

Roster count: 14

We're discussing a trade that sends Marcus Kearns to another team for Isaiah Nakamura at $22,816,874. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 27426695, "incoming_salary": 22816874, "max_incoming": 27426695, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 221716514, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $27,426,695, $22,816,874, $27,426,695

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Indiana
  2. --- Indiana (2026-27) --- (apron salary $226,326,335, over the second apron)
  3. Indiana outgoing salary = $27,426,695 (Marcus Kearns $27,426,695)
  4. Indiana incoming salary = $22,816,874 (Isaiah Nakamura $22,816,874)
  5. Indiana matching limit = $27,426,695 (100% of outgoing salary (team is over the first apron))
  6. Indiana apron salary after the trade = $221,716,514
  7. Verdict: LEGAL
```


## Scenario 8 -- stretch_provision

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

If we waive and stretch Elijah Rees -- $72,800,000 left over 2 years -- what does the dead money look like, and is it even allowed?
```

**Ground truth:** {"legal": true, "remaining_salary": 72800000, "years_remaining": 2, "stretch_years": 5, "annual_dead_money": 14560000, "existing_stretched": 0, "limit": 23197050, "givebacks_required": 0, "reason": "the stretch is legal: $14,560,000 of total dead money sits below the $23,197,050 ceiling"}

**Verdict:** LEGAL

**Required figures (must all appear):** $14,560,000, $23,197,050

**Computation trace (the only figures you may use):**

```
  1. Salary remaining on the contract = $72,800,000
  2. Years remaining (2)
  3. Stretch period (2 x 2 + 1 = 5 seasons)
  4. Annual dead money if stretched = $14,560,000 ($72,800,000 / 5)
  5. Dead money already stretched = $0
  6. Total stretched dead money = $14,560,000
  7. Limit (15% of the 2025-26 cap) = $23,197,050 (15% x $154,647,000)
  8. Legal = $8,637,050 (room to spare)
```


## Scenario 9 -- exception_survey

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
Zion Boateng,7916872,0,4
Goran Lindqvist,2646162,0,3
Luka Ferreira,17425116,0,3
Luka Petrov,3718336,0,1
Tobias Petrov,25253929,0,3
Rashad Novak,5880146,0,1
Corey Jokubaitis,7047942,0,3
Zion Rees,6450073,0,3
Goran Cordero,7773119,0,4
Corey Nakamura,12354065,0,3
Cam Cordero,42695810,0,4
Alperen Stavros,3790566,0,1
Nico Novak,5936495,0,1
Terrance Nakamura,6428008,0,4

Roster count: 14

Run me through our tools in free agency this summer.
```

**Ground truth:** {"apron_level": "under the tax line", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": 15044000, "reason": "a team with cap space uses the room exception instead", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": false, "amount": 6064000, "reason": "a team with cap space uses the room exception instead", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": 5477000, "reason": "a team with cap space uses the room exception instead", "hard_cap": "first apron"}, {"name": "room exception", "available": true, "amount": 9366000, "reason": "available at $9,366,000 once cap space is used; triggers no hard cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Miami apron salary = $155,316,639 (under the tax line)
  2. 2026-27 first apron = $209,015,000
  3. 2026-27 second apron = $221,686,000
  4. non-taxpayer mid-level exception: unavailable = $15,044,000 (a team with cap space uses the room exception instead)
  5. taxpayer mid-level exception: unavailable = $6,064,000 (a team with cap space uses the room exception instead)
  6. bi-annual exception: unavailable = $5,477,000 (a team with cap space uses the room exception instead)
  7. room exception: available = $9,366,000 (available at $9,366,000 once cap space is used; triggers no hard cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
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

INDIANA -- 2024-25 CAP SHEET
Andre Achiuwa           $4,003,621
Luka Achiuwa           $43,047,724
Amari Ellington         $5,894,878
Nico Marsh              $3,143,181
Kristaps Kalinic        $8,398,527
Jaylen Reddish          $4,853,463
Luka Nakamura           $4,892,122
Andre Kalinic           $5,084,934
Julian Beauchamp        $4,868,202
Kristaps Novak         $15,178,841
Dante Reddish           $3,508,882
Nico Vasquez            $4,851,782
Kellen Petrov          $44,705,044
Zion Jokubaitis        $23,732,776
Julian Ellington        $8,662,564

Roster count: 15

We're discussing a trade that sends Julian Beauchamp to another team for Rashad Sabonis at $3,584,836. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 4868202, "incoming_salary": 3584836, "max_incoming": 4868202, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 183543175, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $4,868,202, $3,584,836, $4,868,202

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Indiana
  2. --- Indiana (2024-25) --- (apron salary $184,826,541, over the first apron)
  3. Indiana outgoing salary = $4,868,202 (Julian Beauchamp $4,868,202)
  4. Indiana incoming salary = $3,584,836 (Rashad Sabonis $3,584,836)
  5. Indiana matching limit = $4,868,202 (100% of outgoing salary (team is over the first apron))
  6. Indiana apron salary after the trade = $183,543,175
  7. Verdict: LEGAL
```


## Scenario 11 -- tax_bill

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
| Kobe Petrov | $3,443,587 | -- | 1 |
| Micah Lindqvist | $5,884,521 | -- | 3 |
| Tobias Boateng | $7,099,271 | -- | 3 |
| Isaiah Jokubaitis | $6,222,766 | -- | 3 |
| Deni Duval | $5,899,859 | -- | 1 |
| Zion Achiuwa | $56,596,518 | -- | 2 |
| Trey Novak | $8,422,152 | -- | 3 |
| Malik Jokubaitis | $23,429,143 | -- | 2 |
| Corey Amadi | $8,304,297 | -- | 4 |
| Jaylen Beauchamp | $8,770,341 | -- | 4 |
| Marcus Amadi | $49,643,697 | -- | 1 |
| Nikola Lindqvist | $6,127,378 | -- | 4 |
| Isaiah Nakamura | $8,623,137 | -- | 4 |
| Dante Rees | $4,806,407 | -- | 3 |
| Malik Rees | $8,515,110 | -- | 4 |

Roster count: 15

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 211788184, "tax_line": 200428000, "amount_over": 11360184, "is_repeater": false, "total": 12684230, "brackets": [{"index": 1, "amount": 6064000, "rate": 1.0, "owed": 6064000}, {"index": 2, "amount": 5296184, "rate": 1.25, "owed": 6620230}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $12,684,230, $11,360,184

**Computation trace (the only figures you may use):**

```
  1. Toronto tax salary = $211,788,184
  2. 2026-27 luxury tax line = $200,428,000
  3. Amount over the tax line = $11,360,184 ($211,788,184 - $200,428,000)
  4. Rate schedule: standard (2026-27) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $6,064,000 at $1.00 per dollar = $6,064,000
  6. Bracket 2: $5,296,184 at $1.25 per dollar = $6,620,230
  7. Total luxury tax owed = $12,684,230
  8. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 12 -- exception_eligibility

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Zion Cordero | $4,778,384 | -- | 1 |
| Jalil Okoro | $5,530,679 | -- | 4 |
| Darnell Nakamura | $52,848,421 | -- | 2 |
| Deni Sabonis | $9,023,228 | -- | 2 |
| Deni Cordero | $8,301,447 | -- | 4 |
| Devonte Duval | $9,899,475 | -- | 2 |
| Tobias Ferreira | $9,506,902 | -- | 3 |
| Marcus Amadi | $26,509,231 | -- | 1 |
| Jalil Halvorsen | $10,420,713 | -- | 3 |
| Jaylen Ibarra | $3,520,463 | -- | 3 |
| Darnell Lindqvist | $4,630,654 | -- | 4 |
| Zion Jokubaitis | $8,562,379 | -- | 3 |
| Dante Reddish | $5,439,677 | -- | 1 |
| Julian Okoro | $48,969,559 | -- | 4 |
| Jalil Vasquez | $4,557,089 | -- | 2 |

Roster count: 15

Can we sign Malik Okoro for $4,678,503 using the taxpayer mid-level exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "taxpayer mid-level exception", "salary": 4678503, "hard_cap_triggered": "none", "apron_level": "over the first apron", "apron_salary_after": 217176804, "reasons": ["San Antonio already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $4,678,503

**Computation trace (the only figures you may use):**

```
  1. San Antonio apron salary before signing = $212,498,301 (over the first apron)
  2. Proposed salary for Malik Okoro = $4,678,503
  3. Exception: taxpayer mid-level exception
  4. taxpayer mid-level exception maximum = $6,064,000
  5. Room remaining within the exception = $1,385,497
  6. San Antonio apron salary after signing = $217,176,804
  7. Hard cap: second apron = $221,686,000
  8. Room below the hard cap = $4,509,196
  9. VIOLATION -- roster is full (15-man limit reached)
  10. Verdict: ILLEGAL
```


## Scenario 13 -- exception_survey

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
Brennan Rees             $4,941,245
Zion Kalinic            $15,253,301
Marcus Marsh             $4,890,716
Andre Rees               $2,306,244
Brennan Duval            $9,441,047
Jaylen Novak             $3,581,714
Andre Halvorsen          $5,280,209
Alperen Whitfield        $6,817,712
Micah Petrov            $12,838,292
Santi Reddish           $42,424,264
Malik Halvorsen         $42,027,638
Corey Boateng            $4,630,583
Rashad Reddish          $16,272,692
Deni Ellington           $6,230,716
Corey Petrov             $3,842,016

Roster count: 15

Which exceptions can we actually use at this payroll?
```

**Ground truth:** {"apron_level": "over the first apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 5168000, "reason": "available at $5,168,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Utah apron salary = $180,778,389 (over the first apron)
  2. 2024-25 first apron = $178,132,000
  3. 2024-25 second apron = $188,931,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: available = $5,168,000 (available at $5,168,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: unavailable (unavailable over the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 14 -- trade_legality

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
Deni Cordero,5598843,0,4
Kristaps Rees,7966374,0,1
Malik Vasquez,8569265,0,1
Rashad Sabonis,11443918,0,4
Zion Whitfield,4840699,0,1
Cam Marsh,2877420,0,3
Brennan Vasquez,11348888,0,3
Darnell Osei,8840514,0,2
Corey Petrov,6960444,0,3
Darnell Stavros,6340419,0,1
Nikola Ferreira,6937845,0,1
Jaylen Novak,6277088,0,3
Andre Petrov,47037571,0,2
Jalil Petrov,5320085,0,4
Bogdan Reddish,2972660,0,1

Roster count: 15

We're discussing a trade that sends Darnell Osei and Andre Petrov to another team for Corey Reddish at $86,600,772. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 55878085, "incoming_salary": 86600772, "max_incoming": 70097606, "matching_rule": "125% + $250,000 (outgoing above $32,971,000)", "apron_level": "under the tax line", "apron_salary_after": 174054720, "hard_cap_triggered": "first apron", "violations": ["Utah: salary matching -- Utah takes back $86,600,772 but may only absorb $70,097,606 under 125% + $250,000 (outgoing above $32,971,000) -- over by $16,503,166"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $55,878,085, $86,600,772, $70,097,606

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Utah
  2. --- Utah (2025-26) --- (apron salary $143,332,033, under the tax line)
  3. Utah outgoing salary = $55,878,085 (Darnell Osei $8,840,514, Andre Petrov $47,037,571)
  4. Utah incoming salary = $86,600,772 (Corey Reddish $86,600,772)
  5. Utah matching limit = $70,097,606 (125% + $250,000 (outgoing above $32,971,000))
  6. VIOLATION -- salary matching (Utah takes back $86,600,772 but may only absorb $70,097,606 under 125% + $250,000 (outgoing above $32,971,000) -- over by $16,503,166)
  7. Utah hard-capped at the first apron = $195,945,000 (took back more than 100% of outgoing salary)
  8. Utah hard-capped at the second apron = $207,824,000 (aggregated two or more salaries in one trade)
  9. Two hard caps triggered -- the tighter one governs = $195,945,000
  10. Utah apron salary after the trade = $174,054,720
  11. Utah stays under its first apron hard cap = $21,890,280 ($195,945,000 - $174,054,720 of room to spare)
  12. Verdict: ILLEGAL
```


## Scenario 15 -- trade_legality

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
Santi Duval            $28,728,458
Darnell Sabonis         $7,157,033
Santi Beauchamp        $21,453,307
Kobe Rees               $2,866,968
Isaiah Amadi            $4,530,934
Luka Whitfield         $28,481,135
Goran Novak            $25,094,964
Trey Kalinic            $7,558,851
Micah Stavros           $5,940,313
Elijah Ellington        $3,309,246
Goran Reddish           $3,291,481
Darnell Ibarra          $8,467,766
Nikola Ibarra           $8,312,701
Malik Stavros          $51,311,938

Roster count: 14

We're discussing a trade that sends Goran Reddish and Santi Beauchamp to another team for Elijah Reddish at $28,176,969. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 24744788, "incoming_salary": 28176969, "max_incoming": 24744788, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 209937276, "hard_cap_triggered": "second apron", "violations": ["Portland: salary matching -- Portland takes back $28,176,969 but may only absorb $24,744,788 under 100% of outgoing salary (team is over the first apron) -- over by $3,432,181", "Portland: hard cap exceeded -- Portland would sit at $209,937,276, above its second apron hard cap of $207,824,000 -- over by $2,113,276"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $24,744,788, $28,176,969, $24,744,788

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Portland
  2. --- Portland (2025-26) --- (apron salary $206,505,095, over the first apron)
  3. Portland outgoing salary = $24,744,788 (Goran Reddish $3,291,481, Santi Beauchamp $21,453,307)
  4. Portland incoming salary = $28,176,969 (Elijah Reddish $28,176,969)
  5. Portland matching limit = $24,744,788 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (Portland takes back $28,176,969 but may only absorb $24,744,788 under 100% of outgoing salary (team is over the first apron) -- over by $3,432,181)
  7. Portland hard-capped at the second apron = $207,824,000 (aggregated two or more salaries in one trade)
  8. Portland apron salary after the trade = $209,937,276
  9. VIOLATION -- hard cap exceeded (Portland would sit at $209,937,276, above its second apron hard cap of $207,824,000 -- over by $2,113,276)
  10. Verdict: ILLEGAL
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

If we waive and stretch Luka Brantley -- $80,200,000 left over 1 year -- what does the dead money look like, and is it even allowed?
```

**Ground truth:** {"legal": false, "remaining_salary": 80200000, "years_remaining": 1, "stretch_years": 3, "annual_dead_money": 26733333, "existing_stretched": 12100000, "limit": 21088200, "givebacks_required": 53235399, "reason": "the stretch is not legal as structured: $38,833,333 of dead money would exceed the $21,088,200 ceiling by $17,745,133 per season. The player would have to give back roughly $53,235,399 for the waiver to work"}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $26,733,333, $21,088,200

**Computation trace (the only figures you may use):**

```
  1. Salary remaining on the contract = $80,200,000
  2. Years remaining (1)
  3. Stretch period (2 x 1 + 1 = 3 seasons)
  4. Annual dead money if stretched = $26,733,333 ($80,200,000 / 3)
  5. Dead money already stretched = $12,100,000
  6. Total stretched dead money = $38,833,333
  7. Limit (15% of the 2024-25 cap) = $21,088,200 (15% x $140,588,000)
  8. VIOLATION -- exceeds the dead-money ceiling = $17,745,133
  9. Approximate giveback required = $53,235,399 ($17,745,133 x 3 seasons)
```


## Scenario 17 -- trade_legality

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
Isaiah Marsh,50439630,0,2
Amari Ibarra,48533233,0,2
Goran Cordero,2796692,0,1
Brennan Stavros,6810893,0,4
Corey Beauchamp,4252683,0,4
Kobe Kalinic,5291657,0,4
Micah Ibarra,25084794,0,3
Tobias Novak,2527065,0,1
Darnell Jokubaitis,8026806,0,2
Malik Halvorsen,10775952,0,2
Dante Petrov,24094792,0,1
Luka Sabonis,7571022,0,4
Alperen Stavros,14573378,0,4
Marcus Ellington,4533842,0,3

Roster count: 14

We're discussing a trade that sends Micah Ibarra to another team for Dante Rees at $30,684,404. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 25084794, "incoming_salary": 30684404, "max_incoming": 25084794, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 220912049, "hard_cap_triggered": "none", "violations": ["Miami: salary matching -- Miami takes back $30,684,404 but may only absorb $25,084,794 under 100% of outgoing salary (team is over the first apron) -- over by $5,599,610"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $25,084,794, $30,684,404, $25,084,794

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Miami
  2. --- Miami (2026-27) --- (apron salary $215,312,439, over the first apron)
  3. Miami outgoing salary = $25,084,794 (Micah Ibarra $25,084,794)
  4. Miami incoming salary = $30,684,404 (Dante Rees $30,684,404)
  5. Miami matching limit = $25,084,794 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (Miami takes back $30,684,404 but may only absorb $25,084,794 under 100% of outgoing salary (team is over the first apron) -- over by $5,599,610)
  7. Miami apron salary after the trade = $220,912,049
  8. Verdict: ILLEGAL
```


## Scenario 18 -- trade_legality

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
Deni Achiuwa            $7,972,925
Kellen Sabonis         $18,517,894
Micah Marsh             $6,115,101
Terrance Rees          $52,536,072
Alperen Ibarra         $33,269,024
Bogdan Novak            $2,892,072
Darnell Reddish        $53,823,531
Santi Cordero           $8,664,238
Jalil Kearns           $11,930,035
Kristaps Kalinic       $15,341,086
Tobias Kalinic          $7,533,003
Micah Brantley          $2,996,255
Kellen Petrov           $3,683,678

Roster count: 13

We're discussing a trade that sends Jalil Kearns to another team for Julian Rees at $10,232,165. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 11930035, "incoming_salary": 10232165, "max_incoming": 11930035, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 223577044, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $11,930,035, $10,232,165, $11,930,035

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Indiana
  2. --- Indiana (2026-27) --- (apron salary $225,274,914, over the second apron)
  3. Indiana outgoing salary = $11,930,035 (Jalil Kearns $11,930,035)
  4. Indiana incoming salary = $10,232,165 (Julian Rees $10,232,165)
  5. Indiana matching limit = $11,930,035 (100% of outgoing salary (team is over the first apron))
  6. Indiana apron salary after the trade = $223,577,044
  7. Verdict: LEGAL
```


## Scenario 19 -- trade_legality

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Amari Osei | $45,079,120 | -- | 1 |
| Alperen Reddish | $6,454,037 | -- | 2 |
| Kristaps Novak | $5,232,977 | -- | 2 |
| Luka Reddish | $3,796,050 | -- | 3 |
| Goran Stavros | $3,808,076 | -- | 3 |
| Rashad Amadi | $7,370,550 | -- | 2 |
| Kobe Sabonis | $16,104,000 | -- | 3 |
| Kristaps Amadi | $24,815,843 | -- | 2 |
| Amari Nakamura | $9,550,759 | -- | 4 |
| Terrance Ibarra | $49,182,347 | -- | 2 |
| Andre Osei | $6,447,173 | -- | 4 |
| Kristaps Cordero | $10,079,630 | -- | 4 |
| Nikola Kearns | $14,815,930 | -- | 3 |
| Elijah Dumont | $4,874,828 | -- | 3 |
| Alperen Okoro | $5,464,397 | -- | 2 |

Roster count: 15

We're discussing a trade that sends Kristaps Cordero to another team for Darnell Amadi at $7,676,236. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 10079630, "incoming_salary": 7676236, "max_incoming": 10079630, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 210672323, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $10,079,630, $7,676,236, $10,079,630

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Detroit
  2. --- Detroit (2024-25) --- (apron salary $213,075,717, over the second apron)
  3. Detroit outgoing salary = $10,079,630 (Kristaps Cordero $10,079,630)
  4. Detroit incoming salary = $7,676,236 (Darnell Amadi $7,676,236)
  5. Detroit matching limit = $10,079,630 (100% of outgoing salary (team is over the first apron))
  6. Detroit apron salary after the trade = $210,672,323
  7. Verdict: LEGAL
```


## Scenario 20 -- exception_eligibility

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
Corey Kearns             $7,810,434
Cam Kearns              $11,041,701
Rashad Marsh             $6,705,529
Kellen Kearns           $54,126,450
Goran Dumont             $6,257,662
Santi Petrov            $10,275,448
Tobias Nakamura          $7,939,804
Nikola Duval            $30,467,275
Goran Rees               $9,113,216
Jaylen Whitfield        $10,250,226
Elijah Ibarra            $5,365,512
Kristaps Nakamura        $4,270,932
Nikola Amadi            $24,361,367
Kellen Cordero           $9,135,537
Jalil Jokubaitis         $9,643,746

Roster count: 15

Can we sign Devonte Sabonis for $4,325,013 using the bi-annual exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "bi-annual exception", "salary": 4325013, "hard_cap_triggered": "none", "apron_level": "over the first apron", "apron_salary_after": 211089852, "reasons": ["bi-annual exception is unavailable over the first apron", "Sacramento already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $4,325,013

**Computation trace (the only figures you may use):**

```
  1. Sacramento apron salary before signing = $206,764,839 (over the first apron)
  2. Proposed salary for Devonte Sabonis = $4,325,013
  3. Exception: bi-annual exception
  4. VIOLATION -- bi-annual exception unavailable (unavailable over the first apron)
  5. Sacramento apron salary after signing = $211,089,852
  6. VIOLATION -- roster is full (15-man limit reached)
  7. Verdict: ILLEGAL
```


## Scenario 21 -- scenario_planning

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
Nikola Ibarra           $7,810,145
Santi Rees              $7,086,768
Devonte Novak           $9,025,953
Rashad Reddish          $7,381,554
Trey Reddish            $2,703,892
Jalil Stavros          $23,439,338
Santi Lindqvist         $7,228,828
Dante Whitfield        $54,126,450
Deni Jokubaitis        $26,970,614
Kristaps Reddish        $8,685,300
Alperen Reddish         $6,527,478
Micah Dumont            $2,963,869
Bogdan Nakamura         $4,115,970
Isaiah Petrov          $16,145,685
Nikola Stavros         $24,807,452

Roster count: 15

What's the cleanest path under the second apron from here?
```

**Ground truth:** {"apron_salary": 209019296, "second_apron": 207824000, "overage": 1195296, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Trey Reddish", "salary": 2703892, "surplus": 1508596}, {"player": "Micah Dumont", "salary": 2963869, "surplus": 1768573}, {"player": "Bogdan Nakamura", "salary": 4115970, "surplus": 2920674}, {"player": "Alperen Reddish", "salary": 6527478, "surplus": 5332182}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $1,195,296

**Computation trace (the only figures you may use):**

```
  1. Atlanta apron salary = $209,019,296
  2. 2025-26 second apron = $207,824,000
  3. Amount over the second apron = $1,195,296
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Trey Reddish alone clears the gap = $1,508,596 ($2,703,892 out against $1,195,296 of overage, assuming no salary comes back)
  7. Moving Micah Dumont alone clears the gap = $1,768,573 ($2,963,869 out against $1,195,296 of overage, assuming no salary comes back)
  8. Moving Bogdan Nakamura alone clears the gap = $2,920,674 ($4,115,970 out against $1,195,296 of overage, assuming no salary comes back)
  9. Moving Alperen Reddish alone clears the gap = $5,332,182 ($6,527,478 out against $1,195,296 of overage, assuming no salary comes back)
```


## Scenario 22 -- apron_status

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

NEW ORLEANS -- 2026-27 CAP SHEET
Trey Whitfield         $3,113,259   (+$2,033,333 unlikely)
Trey Reddish           $8,587,148
Bogdan Duval           $4,246,822
Alperen Cordero        $9,156,036
Zion Amadi             $5,089,518
Corey Sabonis          $6,599,983
Elijah Dumont          $3,628,342
Nikola Petrov         $41,706,242   (+$2,033,333 unlikely)
Deni Novak             $4,790,362   (+$2,033,334 unlikely)
Dante Dumont          $33,856,876
Devonte Okoro          $5,508,972
Marcus Petrov          $4,754,490
Nikola Stavros         $4,594,593
Jalil Kalinic          $3,710,349
Cam Novak              $9,250,802

Roster count: 15

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 148593794, "unlikely_incentives": 6100000, "apron_salary": 154693794, "apron_level": "under the tax line", "room_to_first_apron": 54321206, "room_to_second_apron": 66992206}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $154,693,794

**Computation trace (the only figures you may use):**

```
  1. New Orleans salaries plus likely incentives = $148,593,794
  2. Unlikely incentives = $6,100,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $154,693,794
  4. 2026-27 luxury tax line = $200,428,000
  5. 2026-27 first apron = $209,015,000
  6. 2026-27 second apron = $221,686,000
  7. Position: under the tax line
  8. Room below the tax line = $45,734,206
  9. Room below the first apron = $54,321,206
  10. Room below the second apron = $66,992,206
```


## Scenario 23 -- exception_survey

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
Micah Novak,4633729,0,4
Tobias Achiuwa,8819453,0,1
Corey Vasquez,4710670,0,4
Nikola Beauchamp,52759917,0,2
Marcus Ibarra,24712237,0,4
Malik Achiuwa,8381405,0,1
Trey Beauchamp,2603582,0,1
Devonte Halvorsen,20746590,0,1
Kobe Rees,24355392,0,1
Darnell Kalinic,12357825,0,1
Cam Novak,43480891,0,1
Tobias Boateng,2579277,0,1
Micah Petrov,3960107,0,4

Roster count: 13

Run me through our tools in free agency this summer.
```

**Ground truth:** {"apron_level": "over the second apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the second apron -- no mid-level of any kind", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Orlando apron salary = $214,101,075 (over the second apron)
  2. 2025-26 first apron = $195,945,000
  3. 2025-26 second apron = $207,824,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: unavailable (unavailable over the second apron -- no mid-level of any kind)
  6. bi-annual exception: unavailable (unavailable over the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 24 -- exception_eligibility

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

CHARLOTTE -- 2025-26 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Tobias Whitfield | $23,142,230 | -- | 1 |
| Micah Cordero | $2,975,078 | -- | 3 |
| Devonte Reddish | $5,932,007 | -- | 3 |
| Isaiah Rees | $6,741,088 | -- | 4 |
| Jaylen Dumont | $8,486,586 | -- | 1 |
| Nico Osei | $6,259,748 | -- | 3 |
| Corey Sabonis | $6,124,778 | -- | 4 |
| Amari Kearns | $3,148,607 | -- | 4 |
| Nico Petrov | $3,374,178 | -- | 4 |
| Zion Brantley | $16,705,401 | -- | 4 |
| Kristaps Duval | $29,029,143 | -- | 2 |
| Isaiah Cordero | $46,572,323 | -- | 4 |
| Julian Beauchamp | $12,700,952 | -- | 1 |
| Nikola Nakamura | $7,107,490 | -- | 2 |
| Darnell Boateng | $3,498,257 | -- | 1 |

Roster count: 15

Can we sign Elijah Osei for $4,462,628 using the taxpayer mid-level exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "taxpayer mid-level exception", "salary": 4462628, "hard_cap_triggered": "none", "apron_level": "under the tax line", "apron_salary_after": 186260494, "reasons": ["Charlotte already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $4,462,628

**Computation trace (the only figures you may use):**

```
  1. Charlotte apron salary before signing = $181,797,866 (under the tax line)
  2. Proposed salary for Elijah Osei = $4,462,628
  3. Exception: taxpayer mid-level exception
  4. taxpayer mid-level exception maximum = $5,685,000
  5. Room remaining within the exception = $1,222,372
  6. Charlotte apron salary after signing = $186,260,494
  7. Hard cap: second apron = $207,824,000
  8. Room below the hard cap = $21,563,506
  9. VIOLATION -- roster is full (15-man limit reached)
  10. Verdict: ILLEGAL
```


## Scenario 25 -- trade_legality

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Jaylen Ibarra | $10,932,579 | -- | 1 |
| Devonte Achiuwa | $48,594,132 | -- | 1 |
| Goran Brantley | $8,663,484 | -- | 2 |
| Brennan Sabonis | $32,171,937 | -- | 1 |
| Nikola Sabonis | $49,205,800 | -- | 2 |
| Tobias Reddish | $4,039,052 | -- | 2 |
| Dante Halvorsen | $6,828,341 | -- | 3 |
| Micah Rees | $5,760,255 | -- | 1 |
| Corey Osei | $5,571,835 | -- | 4 |
| Kristaps Okoro | $10,898,880 | -- | 1 |
| Marcus Whitfield | $3,101,641 | -- | 4 |
| Julian Jokubaitis | $4,925,643 | -- | 4 |
| Dante Rees | $9,051,895 | -- | 3 |
| Nikola Jokubaitis | $9,861,606 | -- | 1 |

Roster count: 14

We're discussing a trade that sends Micah Rees and Jaylen Ibarra to another team for Micah Ferreira at $17,668,846. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 16692834, "incoming_salary": 17668846, "max_incoming": 16692834, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 210583092, "hard_cap_triggered": "none", "violations": ["Washington: second-apron aggregation ban -- Washington is over the second apron ($209,607,080 vs $188,931,000) and may not combine 2 salaries in one trade", "Washington: salary matching -- Washington takes back $17,668,846 but may only absorb $16,692,834 under 100% of outgoing salary (team is over the first apron) -- over by $976,012"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $16,692,834, $17,668,846, $16,692,834

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Washington
  2. --- Washington (2024-25) --- (apron salary $209,607,080, over the second apron)
  3. Washington outgoing salary = $16,692,834 (Micah Rees $5,760,255, Jaylen Ibarra $10,932,579)
  4. Washington incoming salary = $17,668,846 (Micah Ferreira $17,668,846)
  5. VIOLATION -- second-apron aggregation ban (Washington is over the second apron ($209,607,080 vs $188,931,000) and may not combine 2 salaries in one trade)
  6. Washington matching limit = $16,692,834 (100% of outgoing salary (team is over the first apron))
  7. VIOLATION -- salary matching (Washington takes back $17,668,846 but may only absorb $16,692,834 under 100% of outgoing salary (team is over the first apron) -- over by $976,012)
  8. Washington apron salary after the trade = $210,583,092
  9. Verdict: ILLEGAL
```


## Scenario 26 -- apron_status

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
player,salary,unlikely_incentives,years_remaining
Luka Petrov,57736350,0,1
Terrance Whitfield,19107161,0,1
Dante Sabonis,4621862,0,1
Trey Boateng,13496401,0,2
Rashad Rees,7306140,2200000,1
Kobe Amadi,4376850,2200000,1
Elijah Halvorsen,9197397,0,4
Elijah Ibarra,6444866,0,3
Devonte Brantley,7481118,2200000,4
Luka Marsh,28137390,0,3
Terrance Petrov,8190431,0,1
Trey Ellington,57736350,0,3
Terrance Rees,6135935,0,1

Roster count: 13

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 229968251, "unlikely_incentives": 6600000, "apron_salary": 236568251, "apron_level": "over the second apron", "room_to_first_apron": -27553251, "room_to_second_apron": -14882251}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $236,568,251

**Computation trace (the only figures you may use):**

```
  1. Utah salaries plus likely incentives = $229,968,251
  2. Unlikely incentives = $6,600,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $236,568,251
  4. 2026-27 luxury tax line = $200,428,000
  5. 2026-27 first apron = $209,015,000
  6. 2026-27 second apron = $221,686,000
  7. Position: over the second apron
  8. Amount above the tax line = $36,140,251
  9. Amount above the first apron = $27,553,251
  10. Amount above the second apron = $14,882,251
```


## Scenario 27 -- anti_staleness

**What the user said:**

```
2029-30 LEAGUE THRESHOLDS
  Salary cap:          $173,180,000
  Luxury tax line:     $210,414,000
  First apron:         $219,429,000
  Second apron:        $232,731,000
  Non-taxpayer MLE:    $15,794,000
  Taxpayer MLE:        $6,366,000
  Room exception:      $9,833,000
  Tax bracket width:   $6,366,000
  Bi-annual exception: $5,750,000

NEW ORLEANS -- 2029-30 CAP SHEET
Rashad Rees              $19,327,207
Jalil Halvorsen           $8,443,562
Darnell Stavros          $10,624,277
Corey Cordero             $4,528,337
Goran Marsh               $8,183,850
Jalil Okoro              $11,467,695
Malik Marsh              $60,612,999
Kristaps Halvorsen        $3,784,630
Tobias Nakamura          $56,948,777
Brennan Amadi             $4,795,510
Nikola Kalinic           $14,002,999
Dante Kalinic             $6,575,087
Jalil Kalinic             $4,484,749
Marcus Kalinic            $4,166,715
Rashad Kalinic            $5,325,605

Roster count: 15

Using the 2029-30 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2029-30", "apron_salary": 223271999, "apron_level": "over the first apron", "first_apron_provided": 219429000, "second_apron_provided": 232731000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $223,271,999, $232,731,000

**Computation trace (the only figures you may use):**

```
  1. New Orleans apron salary = $223,271,999
  2. 2029-30 first apron (from the figures provided) = $219,429,000
  3. 2029-30 second apron (from the figures provided) = $232,731,000
  4. Position: over the first apron
  5. Room below the second apron = $9,459,001
```


## Scenario 28 -- anti_staleness

**What the user said:**

```
2028-29 LEAGUE THRESHOLDS
  Salary cap:          $146,971,000
  Luxury tax line:     $178,569,000
  First apron:         $186,219,000
  Second apron:        $197,509,000
  Non-taxpayer MLE:    $13,404,000
  Taxpayer MLE:        $5,403,000
  Room exception:      $8,345,000
  Tax bracket width:   $5,403,000
  Bi-annual exception: $5,227,000

HOUSTON -- 2028-29 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Isaiah Vasquez | $4,139,731 | -- | 2 |
| Luka Sabonis | $47,577,189 | -- | 4 |
| Santi Marsh | $5,214,254 | -- | 3 |
| Brennan Ellington | $3,892,023 | -- | 2 |
| Terrance Boateng | $6,212,968 | -- | 4 |
| Rashad Okoro | $18,614,698 | -- | 4 |
| Kobe Ferreira | $2,183,000 | -- | 2 |
| Nico Nakamura | $23,602,945 | -- | 3 |
| Alperen Rees | $7,928,851 | -- | 4 |
| Trey Kearns | $3,302,290 | -- | 2 |
| Terrance Rees | $46,000,865 | -- | 2 |
| Dante Okoro | $2,902,341 | -- | 3 |
| Trey Achiuwa | $3,270,281 | -- | 1 |
| Nico Dumont | $10,704,111 | -- | 4 |

Roster count: 14

Using the 2028-29 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2028-29", "apron_salary": 185545547, "apron_level": "over the tax line", "first_apron_provided": 186219000, "second_apron_provided": 197509000, "would_be_wrong_using_published_figures": "over the first apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $185,545,547, $197,509,000

**Computation trace (the only figures you may use):**

```
  1. Houston apron salary = $185,545,547
  2. 2028-29 first apron (from the figures provided) = $186,219,000
  3. 2028-29 second apron (from the figures provided) = $197,509,000
  4. Position: over the tax line
  5. Room below the second apron = $11,963,453
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

SACRAMENTO -- 2026-27 CAP SHEET
Terrance Beauchamp       $12,288,904
Dante Amadi               $6,180,705
Elijah Halvorsen          $7,039,399
Nikola Kalinic           $11,470,310
Deni Halvorsen           $16,356,464
Rashad Reddish           $57,736,350
Alperen Duval             $7,792,792
Darnell Kearns           $10,936,282
Alperen Marsh             $8,523,460
Isaiah Osei               $5,867,746
Goran Rees                $6,900,700
Jaylen Ellington         $23,789,816
Nico Beauchamp           $18,044,373
Nico Duval                $8,045,406

Roster count: 14
Hard cap: first apron

We're hard-capped at the first apron. Can we add Trey Kalinic at $11,064,045?
```

**Ground truth:** {"legal": false, "hard_cap": "first apron", "hard_cap_limit": 209015000, "room_below_hard_cap": 8042293, "salary": 11064045, "apron_salary_after": 212036752, "reasons": ["the signing would put Sacramento at $212,036,752, above its first apron hard cap of $209,015,000"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $11,064,045, $209,015,000

**Computation trace (the only figures you may use):**

```
  1. Sacramento apron salary before signing = $200,972,707 (over the tax line)
  2. Proposed salary for Trey Kalinic = $11,064,045
  3. Exception: minimum salary exception
  4. Sacramento apron salary after signing = $212,036,752
  5. Hard cap: first apron = $209,015,000
  6. VIOLATION -- hard cap exceeded = $3,021,752
  7. Verdict: ILLEGAL
  8. Room below the first apron hard cap before signing = $8,042,293 ($209,015,000 - $200,972,707)
```


## Scenario 30 -- trade_legality

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
| Corey Lindqvist | $5,741,642 | -- | 4 |
| Micah Marsh | $4,962,280 | -- | 1 |
| Amari Cordero | $26,906,899 | -- | 1 |
| Amari Ibarra | $6,019,751 | -- | 2 |
| Julian Kearns | $12,466,638 | -- | 2 |
| Malik Brantley | $7,499,685 | -- | 4 |
| Isaiah Vasquez | $51,659,699 | -- | 2 |
| Darnell Osei | $7,313,127 | -- | 2 |
| Devonte Boateng | $5,340,780 | -- | 1 |
| Nikola Lindqvist | $16,378,573 | -- | 4 |
| Rashad Kalinic | $53,409,935 | -- | 3 |
| Alperen Cordero | $5,919,981 | -- | 4 |
| Kristaps Ferreira | $6,357,510 | -- | 4 |
| Nico Ferreira | $4,363,949 | -- | 3 |
| Deni Halvorsen | $6,291,581 | -- | 4 |

Roster count: 15

We're discussing a trade that sends Alperen Cordero and Julian Kearns to another team for Deni Amadi at $21,523,253. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 18386619, "incoming_salary": 21523253, "max_incoming": 18386619, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 223768664, "hard_cap_triggered": "second apron", "violations": ["Indiana: salary matching -- Indiana takes back $21,523,253 but may only absorb $18,386,619 under 100% of outgoing salary (team is over the first apron) -- over by $3,136,634", "Indiana: hard cap exceeded -- Indiana would sit at $223,768,664, above its second apron hard cap of $221,686,000 -- over by $2,082,664"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $18,386,619, $21,523,253, $18,386,619

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Indiana
  2. --- Indiana (2026-27) --- (apron salary $220,632,030, over the first apron)
  3. Indiana outgoing salary = $18,386,619 (Alperen Cordero $5,919,981, Julian Kearns $12,466,638)
  4. Indiana incoming salary = $21,523,253 (Deni Amadi $21,523,253)
  5. Indiana matching limit = $18,386,619 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (Indiana takes back $21,523,253 but may only absorb $18,386,619 under 100% of outgoing salary (team is over the first apron) -- over by $3,136,634)
  7. Indiana hard-capped at the second apron = $221,686,000 (aggregated two or more salaries in one trade)
  8. Indiana apron salary after the trade = $223,768,664
  9. VIOLATION -- hard cap exceeded (Indiana would sit at $223,768,664, above its second apron hard cap of $221,686,000 -- over by $2,082,664)
  10. Verdict: ILLEGAL
```


## Scenario 31 -- exception_survey

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
Alperen Achiuwa,8323874,0,4
Goran Amadi,48249192,0,4
Deni Sabonis,9613588,0,2
Amari Ferreira,49205800,0,2
Malik Petrov,25459129,0,1
Corey Petrov,3548728,0,4
Tobias Kalinic,3386470,0,4
Kristaps Ferreira,8254156,0,4
Tobias Boateng,5700538,0,1
Deni Stavros,6803195,0,3
Elijah Ibarra,9244603,0,2
Luka Dumont,16238831,0,2
Goran Boateng,15009004,0,4
Isaiah Cordero,4682150,0,3

Roster count: 14

Which exceptions can we actually use at this payroll?
```

**Ground truth:** {"apron_level": "over the second apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the second apron -- no mid-level of any kind", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Atlanta apron salary = $213,719,258 (over the second apron)
  2. 2024-25 first apron = $178,132,000
  3. 2024-25 second apron = $188,931,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: unavailable (unavailable over the second apron -- no mid-level of any kind)
  6. bi-annual exception: unavailable (unavailable over the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
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
Tobias Kearns          $10,128,245
Darnell Achiuwa        $31,171,749
Terrance Reddish        $9,374,312
Deni Petrov            $10,323,583
Marcus Sabonis          $7,106,742
Kellen Stavros          $8,829,597
Santi Boateng           $3,427,907
Cam Boateng             $8,148,876
Jaylen Amadi            $7,958,064
Kellen Whitfield        $6,705,113
Kobe Amadi             $13,883,163
Micah Duval             $4,394,600
Nico Vasquez           $54,201,811
Andre Osei             $19,080,563
Rashad Osei             $7,380,718

Roster count: 15

We're discussing a trade that sends Rashad Osei to another team for Trey Kalinic at $12,931,232. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 7380718, "incoming_salary": 12931232, "max_incoming": 15011436, "matching_rule": "200% + $250,000 (outgoing at or below $9,096,000)", "apron_level": "over the tax line", "apron_salary_after": 207665557, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $7,380,718, $12,931,232, $15,011,436

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Orlando
  2. --- Orlando (2026-27) --- (apron salary $202,115,043, over the tax line)
  3. Orlando outgoing salary = $7,380,718 (Rashad Osei $7,380,718)
  4. Orlando incoming salary = $12,931,232 (Trey Kalinic $12,931,232)
  5. Orlando matching limit = $15,011,436 (200% + $250,000 (outgoing at or below $9,096,000))
  6. Orlando hard-capped at the first apron = $209,015,000 (took back more than 100% of outgoing salary)
  7. Orlando apron salary after the trade = $207,665,557
  8. Orlando stays under its first apron hard cap = $1,349,443 ($209,015,000 - $207,665,557 of room to spare)
  9. Verdict: LEGAL
```


## Scenario 33 -- exception_eligibility

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
Isaiah Amadi,2088000,0,4
Julian Ibarra,2394884,0,4
Kobe Reddish,4310153,0,3
Julian Osei,4954304,0,3
Jaylen Novak,2217500,0,3
Isaiah Nakamura,24144448,0,1
Julian Beauchamp,9286433,0,2
Amari Osei,27405860,0,2
Darnell Novak,5011136,0,3
Deni Reddish,17790190,0,2
Terrance Kalinic,15147844,0,1
Deni Petrov,2637501,0,2
Julian Novak,9791036,0,4
Devonte Novak,2459085,0,2

Roster count: 14

Can we sign Terrance Boateng for $2,452,751 using the minimum salary exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": true, "exception": "minimum salary exception", "salary": 2452751, "hard_cap_triggered": "none", "apron_level": "under the tax line", "apron_salary_after": 132091125, "reasons": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $2,452,751

**Computation trace (the only figures you may use):**

```
  1. Indiana apron salary before signing = $129,638,374 (under the tax line)
  2. Proposed salary for Terrance Boateng = $2,452,751
  3. Exception: minimum salary exception
  4. Indiana apron salary after signing = $132,091,125
  5. Verdict: LEGAL
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

SAN ANTONIO -- 2024-25 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Goran Okoro,5963067,0,1
Goran Cordero,12799418,0,4
Alperen Brantley,8623338,0,2
Terrance Ibarra,5116866,0,4
Jaylen Kearns,28569487,0,2
Goran Ferreira,12698874,0,2
Goran Ellington,7490833,0,3
Corey Reddish,18761695,0,1
Devonte Kearns,49205800,0,4
Tobias Reddish,6306894,0,3
Kellen Reddish,9387191,0,1
Devonte Nakamura,11932657,0,3
Zion Okoro,6425789,0,3
Rashad Cordero,8868075,0,1

Roster count: 14

We're discussing a trade that sends Terrance Ibarra to another team for Cam Kalinic at $4,207,483. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 5116866, "incoming_salary": 4207483, "max_incoming": 5116866, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the second apron", "apron_salary_after": 191240601, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $5,116,866, $4,207,483, $5,116,866

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: San Antonio
  2. --- San Antonio (2024-25) --- (apron salary $192,149,984, over the second apron)
  3. San Antonio outgoing salary = $5,116,866 (Terrance Ibarra $5,116,866)
  4. San Antonio incoming salary = $4,207,483 (Cam Kalinic $4,207,483)
  5. San Antonio matching limit = $5,116,866 (100% of outgoing salary (team is over the first apron))
  6. San Antonio apron salary after the trade = $191,240,601
  7. Verdict: LEGAL
```


## Scenario 35 -- trade_legality

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Nikola Okoro | $9,073,390 | -- | 1 |
| Luka Amadi | $17,492,751 | -- | 1 |
| Devonte Nakamura | $9,446,506 | -- | 1 |
| Andre Dumont | $9,120,285 | -- | 1 |
| Alperen Ibarra | $5,637,848 | -- | 2 |
| Amari Cordero | $14,566,029 | -- | 3 |
| Jalil Whitfield | $39,931,458 | -- | 3 |
| Malik Petrov | $8,107,604 | -- | 3 |
| Kellen Osei | $8,860,233 | -- | 1 |
| Nico Ibarra | $25,408,475 | -- | 1 |
| Corey Achiuwa | $5,454,047 | -- | 3 |
| Alperen Ellington | $5,023,107 | -- | 3 |
| Marcus Sabonis | $21,321,230 | -- | 4 |

Roster count: 13

We're discussing a trade that sends Devonte Nakamura to another team for Isaiah Beauchamp at $10,436,519. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 9446506, "incoming_salary": 10436519, "max_incoming": 9446506, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 180432976, "hard_cap_triggered": "none", "violations": ["Charlotte: salary matching -- Charlotte takes back $10,436,519 but may only absorb $9,446,506 under 100% of outgoing salary (team is over the first apron) -- over by $990,013"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $9,446,506, $10,436,519, $9,446,506

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Charlotte
  2. --- Charlotte (2024-25) --- (apron salary $179,442,963, over the first apron)
  3. Charlotte outgoing salary = $9,446,506 (Devonte Nakamura $9,446,506)
  4. Charlotte incoming salary = $10,436,519 (Isaiah Beauchamp $10,436,519)
  5. Charlotte matching limit = $9,446,506 (100% of outgoing salary (team is over the first apron))
  6. VIOLATION -- salary matching (Charlotte takes back $10,436,519 but may only absorb $9,446,506 under 100% of outgoing salary (team is over the first apron) -- over by $990,013)
  7. Charlotte apron salary after the trade = $180,432,976
  8. Verdict: ILLEGAL
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

CHARLOTTE -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Santi Beauchamp | $4,389,809 | -- | 3 |
| Rashad Amadi | $7,346,573 | -- | 4 |
| Cam Okoro | $10,889,790 | -- | 4 |
| Micah Duval | $7,601,199 | -- | 3 |
| Darnell Cordero | $23,297,102 | -- | 2 |
| Devonte Halvorsen | $5,603,429 | -- | 1 |
| Nikola Marsh | $5,240,326 | -- | 4 |
| Kellen Nakamura | $22,463,455 | -- | 4 |
| Kristaps Whitfield | $11,024,539 | -- | 1 |
| Corey Sabonis | $7,690,188 | -- | 4 |
| Dante Novak | $11,311,444 | -- | 4 |
| Goran Novak | $57,736,350 | -- | 1 |
| Jaylen Cordero | $11,495,499 | -- | 1 |

Roster count: 13

We're discussing a trade that sends Cam Okoro to another team for Nikola Ibarra at $16,004,227. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 10889790, "incoming_salary": 16004227, "max_incoming": 19985790, "matching_rule": "outgoing + $9,096,000 (middle band)", "apron_level": "under the tax line", "apron_salary_after": 191204140, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $10,889,790, $16,004,227, $19,985,790

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Charlotte
  2. --- Charlotte (2026-27) --- (apron salary $186,089,703, under the tax line)
  3. Charlotte outgoing salary = $10,889,790 (Cam Okoro $10,889,790)
  4. Charlotte incoming salary = $16,004,227 (Nikola Ibarra $16,004,227)
  5. Charlotte matching limit = $19,985,790 (outgoing + $9,096,000 (middle band))
  6. Charlotte hard-capped at the first apron = $209,015,000 (took back more than 100% of outgoing salary)
  7. Charlotte apron salary after the trade = $191,204,140
  8. Charlotte stays under its first apron hard cap = $17,810,860 ($209,015,000 - $191,204,140 of room to spare)
  9. Verdict: LEGAL
```


## Scenario 37 -- buyout_market

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
| Micah Kalinic | $52,587,025 | -- | 1 |
| Brennan Ferreira | $5,834,960 | -- | 2 |
| Andre Okoro | $5,806,303 | -- | 2 |
| Jaylen Osei | $23,944,902 | -- | 3 |
| Rashad Nakamura | $7,689,431 | -- | 1 |
| Dante Beauchamp | $5,827,489 | -- | 2 |
| Corey Kearns | $5,185,025 | -- | 4 |
| Tobias Brantley | $3,298,959 | -- | 2 |
| Kristaps Rees | $6,255,618 | -- | 4 |
| Trey Marsh | $48,594,421 | -- | 3 |
| Micah Petrov | $9,104,579 | -- | 4 |
| Kristaps Sabonis | $7,630,730 | -- | 4 |
| Julian Ferreira | $6,366,299 | -- | 3 |
| Nikola Amadi | $8,516,338 | -- | 3 |
| Jaylen Okoro | $4,933,762 | -- | 3 |

Roster count: 15

Deni Stavros is about to be bought out -- he was making $29,300,000 before the waiver. Can we sign him?
```

**Ground truth:** {"allowed": false, "pre_waiver_salary": 29300000, "non_taxpayer_mle": 14104000, "apron_level": "over the first apron", "reason": "Chicago is over the first apron and may not sign a player waived during the regular season whose pre-waiver salary ($29,300,000) exceeded the non-taxpayer mid-level ($14,104,000)"}

**Verdict:** NOT ALLOWED

**Required figures (must all appear):** $29,300,000, $14,104,000

**Computation trace (the only figures you may use):**

```
  1. Chicago apron status = $201,575,841 (over the first apron)
  2. Player's pre-waiver salary = $29,300,000
  3. 2025-26 non-taxpayer mid-level = $14,104,000
  4. VIOLATION -- buyout-market ban (Chicago is over the first apron and may not sign a player waived during the regular season whose pre-waiver salary ($29,300,000) exceeded the non-taxpayer mid-level ($14,104,000))
```


## Scenario 38 -- scenario_planning

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
| Trey Kearns | $26,677,652 | -- | 4 |
| Deni Okoro | $5,242,262 | -- | 3 |
| Deni Halvorsen | $10,870,902 | -- | 1 |
| Corey Reddish | $9,367,595 | -- | 2 |
| Marcus Vasquez | $8,762,637 | -- | 3 |
| Terrance Jokubaitis | $20,339,148 | -- | 1 |
| Malik Boateng | $8,932,459 | -- | 1 |
| Deni Beauchamp | $22,393,659 | -- | 4 |
| Andre Nakamura | $5,171,087 | -- | 4 |
| Isaiah Kalinic | $8,501,068 | -- | 4 |
| Rashad Marsh | $54,126,450 | -- | 2 |
| Cam Achiuwa | $11,122,161 | -- | 1 |
| Zion Beauchamp | $3,472,574 | -- | 3 |
| Jalil Ibarra | $6,024,584 | -- | 3 |
| Santi Halvorsen | $31,561,899 | -- | 2 |

Roster count: 15

We need to get under the second apron before the deadline. What are our options, and what are we giving up?
```

**Ground truth:** {"apron_salary": 232566137, "second_apron": 207824000, "overage": 24742137, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Trey Kearns", "salary": 26677652, "surplus": 1935515}, {"player": "Santi Halvorsen", "salary": 31561899, "surplus": 6819762}, {"player": "Rashad Marsh", "salary": 54126450, "surplus": 29384313}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $24,742,137

**Computation trace (the only figures you may use):**

```
  1. Sacramento apron salary = $232,566,137
  2. 2025-26 second apron = $207,824,000
  3. Amount over the second apron = $24,742,137
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Trey Kearns alone clears the gap = $1,935,515 ($26,677,652 out against $24,742,137 of overage, assuming no salary comes back)
  7. Moving Santi Halvorsen alone clears the gap = $6,819,762 ($31,561,899 out against $24,742,137 of overage, assuming no salary comes back)
  8. Moving Rashad Marsh alone clears the gap = $29,384,313 ($54,126,450 out against $24,742,137 of overage, assuming no salary comes back)
```


## Scenario 39 -- anti_staleness

**What the user said:**

```
2029-30 LEAGUE THRESHOLDS
  Salary cap:          $148,949,000
  Luxury tax line:     $180,972,000
  First apron:         $188,725,000
  Second apron:        $200,167,000
  Non-taxpayer MLE:    $13,585,000
  Taxpayer MLE:        $5,475,000
  Room exception:      $8,458,000
  Tax bracket width:   $5,475,000
  Bi-annual exception: $5,297,000

MEMPHIS -- 2029-30 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Dante Novak,3369473,0,2
Malik Beauchamp,48385852,0,4
Amari Ferreira,2713647,0,3
Brennan Amadi,8419284,0,3
Jaylen Halvorsen,23255789,0,3
Tobias Duval,8165594,0,3
Jalil Cordero,5266519,0,3
Corey Whitfield,4350743,0,4
Nikola Sabonis,7768004,0,2
Malik Sabonis,6270739,0,4
Amari Amadi,4434089,0,3
Tobias Lindqvist,5612879,0,2
Trey Ellington,5077184,0,3
Dante Cordero,4648226,0,4
Andre Achiuwa,48182457,0,1

Roster count: 15

Using the 2029-30 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2029-30", "apron_salary": 185920479, "apron_level": "over the tax line", "first_apron_provided": 188725000, "second_apron_provided": 200167000, "would_be_wrong_using_published_figures": "over the first apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $185,920,479, $200,167,000

**Computation trace (the only figures you may use):**

```
  1. Memphis apron salary = $185,920,479
  2. 2029-30 first apron (from the figures provided) = $188,725,000
  3. 2029-30 second apron (from the figures provided) = $200,167,000
  4. Position: over the tax line
  5. Room below the second apron = $14,246,521
```


