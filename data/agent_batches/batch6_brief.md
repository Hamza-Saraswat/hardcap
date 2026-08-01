# Writing batch 6

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

Write one JSON object per line to `data/agent_batches/batch6_responses.jsonl`, nothing else in the file:

    {"id": 0, "response": "**Verdict: ILLEGAL.** ..."}

The `id` must match the scenario number below.

---

## Scenario 0 -- apron_status

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
Jalil Nakamura,5227653,0,4
Andre Stavros,4001105,0,3
Micah Marsh,26509655,0,2
Darnell Marsh,5721453,1233334,3
Rashad Cordero,6918597,1233333,1
Trey Whitfield,4701637,0,2
Jalil Osei,6260149,0,4
Brennan Cordero,14846086,0,2
Malik Stavros,2999690,0,1
Marcus Marsh,47000093,0,3
Jaylen Duval,2211583,0,3
Kristaps Petrov,2183342,0,4
Kellen Halvorsen,16077269,0,3
Goran Ibarra,6882641,1233333,4
Corey Cordero,2947264,0,3

Roster count: 15

Are we over the second apron? How much room do we have?
```

**Ground truth:** {"tax_salary": 154488217, "unlikely_incentives": 3700000, "apron_salary": 158188217, "apron_level": "under the tax line", "room_to_first_apron": 19943783, "room_to_second_apron": 30742783}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $158,188,217

**Computation trace (the only figures you may use):**

```
  1. Memphis salaries plus likely incentives = $154,488,217
  2. Unlikely incentives = $3,700,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $158,188,217
  4. 2024-25 luxury tax line = $170,814,000
  5. 2024-25 first apron = $178,132,000
  6. 2024-25 second apron = $188,931,000
  7. Position: under the tax line
  8. Room below the tax line = $12,625,783
  9. Room below the first apron = $19,943,783
  10. Room below the second apron = $30,742,783
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
Deni Sabonis             $5,589,404
Jaylen Dumont           $12,263,264
Zion Achiuwa             $7,353,432
Amari Duval             $19,516,141
Darnell Reddish         $48,936,259
Brennan Nakamura         $4,028,659
Brennan Amadi            $2,839,133
Jalil Vasquez            $4,621,310
Deni Amadi               $2,394,206
Terrance Boateng         $4,671,095
Amari Cordero           $44,122,322
Andre Brantley           $6,808,749
Bogdan Jokubaitis        $6,622,293
Nikola Rees              $7,121,981

Roster count: 14

We're discussing a trade that sends Andre Brantley to another team for Elijah Ellington at $11,348,941. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": false, "outgoing_salary": 6808749, "incoming_salary": 11348941, "max_incoming": 13867498, "matching_rule": "200% + $250,000 (outgoing at or below $7,752,000)", "apron_level": "over the tax line", "apron_salary_after": 181428440, "hard_cap_triggered": "first apron", "violations": ["New Orleans: hard cap exceeded -- New Orleans would sit at $181,428,440, above its first apron hard cap of $178,132,000 -- over by $3,296,440"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $6,808,749, $11,348,941, $13,867,498

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: New Orleans
  2. --- New Orleans (2024-25) --- (apron salary $176,888,248, over the tax line)
  3. New Orleans outgoing salary = $6,808,749 (Andre Brantley $6,808,749)
  4. New Orleans incoming salary = $11,348,941 (Elijah Ellington $11,348,941)
  5. New Orleans matching limit = $13,867,498 (200% + $250,000 (outgoing at or below $7,752,000))
  6. New Orleans hard-capped at the first apron = $178,132,000 (took back more than 100% of outgoing salary)
  7. New Orleans apron salary after the trade = $181,428,440
  8. VIOLATION -- hard cap exceeded (New Orleans would sit at $181,428,440, above its first apron hard cap of $178,132,000 -- over by $3,296,440)
  9. Verdict: ILLEGAL
```


## Scenario 2 -- apron_status

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
Jalil Boateng           $3,216,486
Tobias Achiuwa         $39,425,205
Goran Duval             $4,001,683
Bogdan Okoro            $4,296,611
Bogdan Novak           $42,268,522
Marcus Kearns           $8,807,831
Goran Cordero          $23,393,099
Marcus Petrov          $13,623,492
Micah Jokubaitis        $5,158,286   (+$1,100,000 unlikely)
Brennan Amadi          $14,617,944   (+$1,100,000 unlikely)
Santi Nakamura          $5,275,125
Terrance Boateng        $6,158,626
Luka Duval              $8,979,689   (+$1,100,000 unlikely)

Roster count: 13

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 179222599, "unlikely_incentives": 3300000, "apron_salary": 182522599, "apron_level": "over the first apron", "room_to_first_apron": -4390599, "room_to_second_apron": 6408401}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $182,522,599

**Computation trace (the only figures you may use):**

```
  1. Sacramento salaries plus likely incentives = $179,222,599
  2. Unlikely incentives = $3,300,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $182,522,599
  4. 2024-25 luxury tax line = $170,814,000
  5. 2024-25 first apron = $178,132,000
  6. 2024-25 second apron = $188,931,000
  7. Position: over the first apron
  8. Amount above the tax line = $11,708,599
  9. Amount above the first apron = $4,390,599
  10. Room below the second apron = $6,408,401
```


## Scenario 3 -- exception_survey

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
player,salary,unlikely_incentives,years_remaining
Malik Dumont,20576939,0,4
Malik Kalinic,4846303,0,3
Jalil Okoro,8253920,0,3
Andre Vasquez,8127239,0,1
Andre Jokubaitis,19340647,0,2
Deni Marsh,6559236,0,2
Darnell Ferreira,45266856,0,3
Marcus Duval,8133921,0,2
Santi Beauchamp,6073960,0,4
Elijah Kalinic,7068873,0,4
Corey Petrov,4508773,0,3
Goran Ellington,8317416,0,2
Kristaps Osei,18704853,0,4
Kellen Marsh,40379492,0,2

Roster count: 14

Run me through our tools in free agency this summer.
```

**Ground truth:** {"apron_level": "over the first apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 5685000, "reason": "available at $5,685,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Sacramento apron salary = $206,158,428 (over the first apron)
  2. 2025-26 first apron = $195,945,000
  3. 2025-26 second apron = $207,824,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: available = $5,685,000 (available at $5,685,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: unavailable (unavailable over the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 4 -- apron_status

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

WASHINGTON -- 2026-27 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Devonte Halvorsen,33585251,0,1
Malik Osei,32839571,0,2
Amari Amadi,7024635,0,1
Micah Vasquez,57736350,0,4
Kobe Brantley,5157656,400000,4
Darnell Brantley,9077677,0,1
Santi Brantley,4264097,0,4
Trey Novak,7561990,0,3
Deni Petrov,3493545,400000,3
Darnell Duval,4432617,400000,2
Bogdan Ibarra,20356946,0,3
Amari Whitfield,3947242,0,4
Devonte Duval,14876073,0,2
Rashad Ferreira,4760397,0,3

Roster count: 14

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 209114047, "unlikely_incentives": 1200000, "apron_salary": 210314047, "apron_level": "over the first apron", "room_to_first_apron": -1299047, "room_to_second_apron": 11371953}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $210,314,047

**Computation trace (the only figures you may use):**

```
  1. Washington salaries plus likely incentives = $209,114,047
  2. Unlikely incentives = $1,200,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $210,314,047
  4. 2026-27 luxury tax line = $200,428,000
  5. 2026-27 first apron = $209,015,000
  6. 2026-27 second apron = $221,686,000
  7. Position: over the first apron
  8. Amount above the tax line = $9,886,047
  9. Amount above the first apron = $1,299,047
  10. Room below the second apron = $11,371,953
```


## Scenario 5 -- anti_staleness

**What the user said:**

```
2028-29 LEAGUE THRESHOLDS
  Salary cap:          $154,333,000
  Luxury tax line:     $187,514,000
  First apron:         $195,547,000
  Second apron:        $207,402,000
  Non-taxpayer MLE:    $14,076,000
  Taxpayer MLE:        $5,673,000
  Room exception:      $8,763,000
  Tax bracket width:   $5,673,000
  Bi-annual exception: $5,489,000

BROOKLYN -- 2028-29 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Deni Reddish | $46,948,995 | -- | 4 |
| Marcus Kalinic | $16,312,755 | -- | 1 |
| Terrance Vasquez | $15,567,299 | -- | 1 |
| Kellen Ellington | $8,395,172 | -- | 1 |
| Corey Halvorsen | $7,163,226 | -- | 4 |
| Darnell Sabonis | $51,600,089 | -- | 3 |
| Dante Reddish | $8,068,376 | -- | 4 |
| Kellen Reddish | $8,309,046 | -- | 2 |
| Brennan Osei | $3,504,747 | -- | 3 |
| Elijah Dumont | $9,117,989 | -- | 3 |
| Corey Achiuwa | $3,872,635 | -- | 4 |
| Malik Brantley | $8,904,669 | -- | 4 |
| Darnell Marsh | $6,322,434 | -- | 2 |

Roster count: 13

Using the 2028-29 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2028-29", "apron_salary": 194087432, "apron_level": "over the tax line", "first_apron_provided": 195547000, "second_apron_provided": 207402000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $194,087,432, $207,402,000

**Computation trace (the only figures you may use):**

```
  1. Brooklyn apron salary = $194,087,432
  2. 2028-29 first apron (from the figures provided) = $195,547,000
  3. 2028-29 second apron (from the figures provided) = $207,402,000
  4. Position: over the tax line
  5. Room below the second apron = $13,314,568
```


## Scenario 6 -- anti_staleness

**What the user said:**

```
2027-28 LEAGUE THRESHOLDS
  Salary cap:          $148,296,000
  Luxury tax line:     $180,180,000
  First apron:         $187,899,000
  Second apron:        $199,290,000
  Non-taxpayer MLE:    $13,525,000
  Taxpayer MLE:        $5,451,000
  Room exception:      $8,421,000
  Tax bracket width:   $5,451,000
  Bi-annual exception: $5,274,000

DETROIT -- 2027-28 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Trey Stavros,15496620,0,3
Kellen Kearns,9040615,0,4
Cam Okoro,7888126,0,3
Goran Okoro,9420779,0,2
Andre Kearns,31704837,0,1
Tobias Ferreira,2343256,0,3
Cam Reddish,8308269,0,4
Rashad Kalinic,6654623,0,4
Marcus Marsh,5702208,0,2
Kellen Rees,6725702,0,3
Julian Stavros,49243572,0,2
Darnell Beauchamp,3398650,0,4
Malik Cordero,18707650,0,1
Darnell Jokubaitis,20068922,0,1

Roster count: 14

Using the 2027-28 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2027-28", "apron_salary": 194703829, "apron_level": "over the first apron", "first_apron_provided": 187899000, "second_apron_provided": 199290000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $194,703,829, $199,290,000

**Computation trace (the only figures you may use):**

```
  1. Detroit apron salary = $194,703,829
  2. 2027-28 first apron (from the figures provided) = $187,899,000
  3. 2027-28 second apron (from the figures provided) = $199,290,000
  4. Position: over the first apron
  5. Room below the second apron = $4,586,171
```


## Scenario 7 -- apron_status

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
Goran Duval              $8,696,323
Bogdan Lindqvist         $8,721,221
Cam Jokubaitis           $3,300,555
Bogdan Boateng          $10,308,883
Andre Rees               $6,698,507
Deni Reddish            $13,858,910
Darnell Nakamura        $43,858,638
Kellen Lindqvist         $2,684,604
Micah Halvorsen          $6,830,346
Goran Reddish           $13,310,531
Cam Rees                $41,857,976
Dante Kearns             $7,560,122
Rashad Jokubaitis        $9,122,127
Darnell Duval            $6,628,767

Roster count: 14

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 183437510, "unlikely_incentives": 0, "apron_salary": 183437510, "apron_level": "over the first apron", "room_to_first_apron": -5305510, "room_to_second_apron": 5493490}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $183,437,510

**Computation trace (the only figures you may use):**

```
  1. Atlanta salaries plus likely incentives = $183,437,510
  2. Apron salary = $183,437,510
  3. 2024-25 luxury tax line = $170,814,000
  4. 2024-25 first apron = $178,132,000
  5. 2024-25 second apron = $188,931,000
  6. Position: over the first apron
  7. Amount above the tax line = $12,623,510
  8. Amount above the first apron = $5,305,510
  9. Room below the second apron = $5,493,490
```


## Scenario 8 -- apron_status

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Nikola Nakamura | $6,713,673 | -- | 2 |
| Brennan Ibarra | $7,963,304 | -- | 2 |
| Zion Okoro | $6,279,546 | -- | 2 |
| Kristaps Dumont | $27,728,245 | -- | 2 |
| Dante Amadi | $6,644,912 | -- | 4 |
| Rashad Stavros | $3,939,010 | -- | 3 |
| Cam Vasquez | $43,787,519 | -- | 1 |
| Deni Jokubaitis | $4,773,569 | -- | 1 |
| Julian Kalinic | $7,703,780 | -- | 2 |
| Elijah Ibarra | $5,418,992 | -- | 4 |
| Dante Reddish | $13,065,911 | -- | 1 |
| Santi Osei | $50,194,615 | -- | 4 |
| Kristaps Nakamura | $4,148,276 | -- | 1 |
| Kristaps Duval | $15,454,272 | -- | 4 |

Roster count: 14

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 203815624, "unlikely_incentives": 0, "apron_salary": 203815624, "apron_level": "over the tax line", "room_to_first_apron": 5199376, "room_to_second_apron": 17870376}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $203,815,624

**Computation trace (the only figures you may use):**

```
  1. Chicago salaries plus likely incentives = $203,815,624
  2. Apron salary = $203,815,624
  3. 2026-27 luxury tax line = $200,428,000
  4. 2026-27 first apron = $209,015,000
  5. 2026-27 second apron = $221,686,000
  6. Position: over the tax line
  7. Amount above the tax line = $3,387,624
  8. Room below the first apron = $5,199,376
  9. Room below the second apron = $17,870,376
```


## Scenario 9 -- buyout_market

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
| Deni Vasquez | $6,359,009 | -- | 1 |
| Luka Sabonis | $33,653,055 | -- | 1 |
| Rashad Halvorsen | $54,126,450 | -- | 3 |
| Bogdan Amadi | $11,405,211 | -- | 2 |
| Zion Okoro | $5,735,132 | -- | 3 |
| Kristaps Sabonis | $24,341,307 | -- | 4 |
| Darnell Amadi | $3,903,944 | -- | 4 |
| Elijah Osei | $9,964,931 | -- | 3 |
| Julian Beauchamp | $10,431,741 | -- | 3 |
| Cam Dumont | $9,325,963 | -- | 3 |
| Kellen Nakamura | $7,097,676 | -- | 3 |
| Jalil Reddish | $8,581,279 | -- | 3 |
| Nikola Lindqvist | $8,254,626 | -- | 2 |

Roster count: 13

Santi Cordero is about to be bought out -- he was making $38,900,000 before the waiver. Can we sign him?
```

**Ground truth:** {"allowed": true, "pre_waiver_salary": 38900000, "non_taxpayer_mle": 14104000, "apron_level": "over the tax line", "reason": "Orlando is not over the first apron, so the buyout restriction does not apply"}

**Verdict:** ALLOWED

**Required figures (must all appear):** $38,900,000, $14,104,000

**Computation trace (the only figures you may use):**

```
  1. Orlando apron status = $193,180,324 (over the tax line)
  2. Player's pre-waiver salary = $38,900,000
  3. 2025-26 non-taxpayer mid-level = $14,104,000
  4. Allowed (Orlando is not over the first apron, so the buyout restriction does not apply)
```


## Scenario 10 -- tax_bill

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
Deni Reddish,13536195,0,2
Goran Ellington,8614960,0,4
Dante Sabonis,26084109,0,2
Rashad Kalinic,6537427,0,3
Bogdan Ferreira,10830500,0,3
Luka Marsh,49205800,0,4
Tobias Novak,10607727,0,1
Kellen Rees,6846490,0,1
Micah Halvorsen,8100218,0,2
Marcus Jokubaitis,8778830,0,4
Jalil Nakamura,12859551,0,3
Elijah Marsh,30276820,0,4
Brennan Kalinic,8463577,0,1

Roster count: 13

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 200742204, "tax_line": 170814000, "amount_over": 29928204, "is_repeater": false, "total": 83266867, "brackets": [{"index": 1, "amount": 5168000, "rate": 1.5, "owed": 7752000}, {"index": 2, "amount": 5168000, "rate": 1.75, "owed": 9044000}, {"index": 3, "amount": 5168000, "rate": 2.5, "owed": 12920000}, {"index": 4, "amount": 5168000, "rate": 3.25, "owed": 16796000}, {"index": 5, "amount": 5168000, "rate": 3.75, "owed": 19380000}, {"index": 6, "amount": 4088204, "rate": 4.25, "owed": 17374867}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $83,266,867, $29,928,204

**Computation trace (the only figures you may use):**

```
  1. Charlotte tax salary = $200,742,204
  2. 2024-25 luxury tax line = $170,814,000
  3. Amount over the tax line = $29,928,204 ($200,742,204 - $170,814,000)
  4. Rate schedule: standard (2024-25) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $5,168,000 at $1.50 per dollar = $7,752,000
  6. Bracket 2: $5,168,000 at $1.75 per dollar = $9,044,000
  7. Bracket 3: $5,168,000 at $2.50 per dollar = $12,920,000
  8. Bracket 4: $5,168,000 at $3.25 per dollar = $16,796,000
  9. Bracket 5: $5,168,000 at $3.75 per dollar = $19,380,000
  10. Bracket 6: $4,088,204 at $4.25 per dollar = $17,374,867
  11. Total luxury tax owed = $83,266,867
  12. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 11 -- anti_staleness

**What the user said:**

```
2027-28 LEAGUE THRESHOLDS
  Salary cap:          $149,634,000
  Luxury tax line:     $181,804,000
  First apron:         $189,593,000
  Second apron:        $201,087,000
  Non-taxpayer MLE:    $13,647,000
  Taxpayer MLE:        $5,501,000
  Room exception:      $8,497,000
  Tax bracket width:   $5,501,000
  Bi-annual exception: $5,322,000

ORLANDO -- 2027-28 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Santi Halvorsen | $2,925,694 | -- | 2 |
| Malik Sabonis | $8,155,906 | -- | 3 |
| Kellen Beauchamp | $27,646,697 | -- | 4 |
| Julian Amadi | $45,179,413 | -- | 4 |
| Micah Duval | $5,143,269 | -- | 4 |
| Isaiah Osei | $5,638,614 | -- | 2 |
| Brennan Nakamura | $4,062,238 | -- | 1 |
| Cam Ibarra | $3,952,503 | -- | 1 |
| Corey Beauchamp | $2,222,000 | -- | 1 |
| Deni Kearns | $3,990,452 | -- | 3 |
| Nikola Lindqvist | $20,887,536 | -- | 3 |
| Kristaps Novak | $6,903,609 | -- | 3 |
| Goran Marsh | $8,175,401 | -- | 3 |
| Kellen Dumont | $10,773,358 | -- | 1 |
| Corey Ferreira | $44,548,503 | -- | 4 |

Roster count: 15

Using the 2027-28 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2027-28", "apron_salary": 200205193, "apron_level": "over the first apron", "first_apron_provided": 189593000, "second_apron_provided": 201087000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $200,205,193, $201,087,000

**Computation trace (the only figures you may use):**

```
  1. Orlando apron salary = $200,205,193
  2. 2027-28 first apron (from the figures provided) = $189,593,000
  3. 2027-28 second apron (from the figures provided) = $201,087,000
  4. Position: over the first apron
  5. Room below the second apron = $881,807
```


## Scenario 12 -- apron_status

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
| Kristaps Jokubaitis | $10,038,639 | -- | 1 |
| Brennan Lindqvist | $9,251,778 | -- | 4 |
| Isaiah Whitfield | $7,267,210 | -- | 3 |
| Amari Duval | $18,362,574 | -- | 1 |
| Marcus Petrov | $6,375,667 | -- | 3 |
| Jalil Brantley | $10,080,077 | -- | 1 |
| Darnell Rees | $15,404,591 | -- | 2 |
| Deni Amadi | $13,980,317 | -- | 3 |
| Cam Marsh | $33,472,098 | -- | 4 |
| Alperen Marsh | $14,548,323 | -- | 2 |
| Andre Okoro | $57,736,350 | -- | 1 |
| Isaiah Amadi | $11,239,072 | -- | 4 |
| Brennan Osei | $15,370,534 | -- | 4 |

Roster count: 13

Give me our apron position and what it means for the rest of the offseason.
```

**Ground truth:** {"tax_salary": 223127230, "unlikely_incentives": 0, "apron_salary": 223127230, "apron_level": "over the second apron", "room_to_first_apron": -14112230, "room_to_second_apron": -1441230}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $223,127,230

**Computation trace (the only figures you may use):**

```
  1. Sacramento salaries plus likely incentives = $223,127,230
  2. Apron salary = $223,127,230
  3. 2026-27 luxury tax line = $200,428,000
  4. 2026-27 first apron = $209,015,000
  5. 2026-27 second apron = $221,686,000
  6. Position: over the second apron
  7. Amount above the tax line = $22,699,230
  8. Amount above the first apron = $14,112,230
  9. Amount above the second apron = $1,441,230
```


## Scenario 13 -- scenario_planning

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
| Nikola Okoro | $38,692,667 | -- | 4 |
| Cam Okoro | $23,964,106 | -- | 1 |
| Zion Dumont | $3,101,125 | -- | 3 |
| Trey Ibarra | $16,786,781 | -- | 3 |
| Malik Whitfield | $5,365,916 | -- | 3 |
| Kristaps Beauchamp | $3,850,321 | -- | 1 |
| Brennan Brantley | $2,966,283 | -- | 2 |
| Cam Petrov | $6,711,636 | -- | 1 |
| Nikola Brantley | $3,265,726 | -- | 4 |
| Santi Dumont | $7,473,348 | -- | 2 |
| Goran Ferreira | $3,549,138 | -- | 2 |
| Dante Vasquez | $22,575,215 | -- | 2 |
| Andre Dumont | $7,166,225 | -- | 2 |
| Kellen Whitfield | $47,314,789 | -- | 1 |
| Luka Vasquez | $8,001,687 | -- | 2 |

Roster count: 15

Ownership wants us out of the second apron. Walk me through how we do it.
```

**Ground truth:** {"apron_salary": 200784963, "second_apron": 188931000, "overage": 11853963, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Trey Ibarra", "salary": 16786781, "surplus": 4932818}, {"player": "Dante Vasquez", "salary": 22575215, "surplus": 10721252}, {"player": "Cam Okoro", "salary": 23964106, "surplus": 12110143}, {"player": "Nikola Okoro", "salary": 38692667, "surplus": 26838704}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $11,853,963

**Computation trace (the only figures you may use):**

```
  1. Charlotte apron salary = $200,784,963
  2. 2024-25 second apron = $188,931,000
  3. Amount over the second apron = $11,853,963
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Trey Ibarra alone clears the gap = $4,932,818 ($16,786,781 out against $11,853,963 of overage, assuming no salary comes back)
  7. Moving Dante Vasquez alone clears the gap = $10,721,252 ($22,575,215 out against $11,853,963 of overage, assuming no salary comes back)
  8. Moving Cam Okoro alone clears the gap = $12,110,143 ($23,964,106 out against $11,853,963 of overage, assuming no salary comes back)
  9. Moving Nikola Okoro alone clears the gap = $26,838,704 ($38,692,667 out against $11,853,963 of overage, assuming no salary comes back)
```


## Scenario 14 -- draft_penalty

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
Andre Ellington          $4,749,702
Brennan Okoro           $28,283,213
Alperen Reddish          $4,554,465
Marcus Novak            $12,643,034
Malik Achiuwa           $49,205,800
Micah Whitfield         $12,465,575
Kobe Vasquez             $4,245,213
Cam Stavros              $5,443,526
Cam Nakamura            $11,775,685
Micah Cordero           $12,243,835
Amari Halvorsen          $5,345,223
Brennan Halvorsen       $36,847,535
Corey Kalinic           $10,992,424

Roster count: 13

If we finish the season at this payroll, what happens to our draft picks?
```

**Ground truth:** {"pick_frozen": true, "frozen_draft_year": 2031, "pick_demoted": false, "seasons_over": 0, "reason": "Sacramento finishes over the second apron, freezing its 2031 first-round pick. It unfreezes only after finishing below the second apron in 3 of the following 4 seasons"}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Sacramento apron salary = $198,795,230 (over the second apron)
  2. Seasons finished over the second apron (within the window) (0)
  3. First-round pick frozen (the 2031 first-rounder (7 drafts out) becomes untradeable)
  4. Pick not yet demoted (demotion requires 3 of 5 seasons over the second apron)
```


## Scenario 15 -- exception_survey

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
| Amari Novak | $7,859,309 | -- | 3 |
| Nico Reddish | $18,164,819 | -- | 2 |
| Rashad Ibarra | $7,164,049 | -- | 1 |
| Rashad Rees | $7,815,492 | -- | 4 |
| Micah Lindqvist | $7,244,299 | -- | 2 |
| Kellen Stavros | $17,439,541 | -- | 3 |
| Luka Stavros | $18,694,019 | -- | 3 |
| Dante Whitfield | $7,519,890 | -- | 2 |
| Goran Marsh | $18,208,969 | -- | 3 |
| Brennan Petrov | $10,906,333 | -- | 2 |
| Darnell Jokubaitis | $18,895,920 | -- | 2 |
| Tobias Vasquez | $6,492,471 | -- | 1 |
| Corey Ellington | $54,126,450 | -- | 2 |
| Micah Achiuwa | $14,152,824 | -- | 3 |
| Nikola Brantley | $16,352,659 | -- | 2 |

Roster count: 15

Run me through our tools in free agency this summer.
```

**Ground truth:** {"apron_level": "over the second apron", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": false, "amount": null, "reason": "unavailable over the second apron -- no mid-level of any kind", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": false, "amount": null, "reason": "unavailable over the first apron", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. San Antonio apron salary = $231,037,044 (over the second apron)
  2. 2025-26 first apron = $195,945,000
  3. 2025-26 second apron = $207,824,000
  4. non-taxpayer mid-level exception: unavailable (unavailable over the first apron)
  5. taxpayer mid-level exception: unavailable (unavailable over the second apron -- no mid-level of any kind)
  6. bi-annual exception: unavailable (unavailable over the first apron)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 16 -- trade_legality

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
| Nikola Beauchamp | $8,108,986 | -- | 3 |
| Nico Nakamura | $26,040,502 | -- | 2 |
| Brennan Achiuwa | $5,463,597 | -- | 4 |
| Jalil Kearns | $9,690,310 | -- | 2 |
| Santi Stavros | $10,007,402 | -- | 1 |
| Dante Vasquez | $3,465,870 | -- | 2 |
| Andre Amadi | $34,329,196 | -- | 2 |
| Malik Kearns | $7,377,408 | -- | 3 |
| Corey Stavros | $20,797,048 | -- | 2 |
| Jalil Stavros | $4,883,230 | -- | 2 |
| Amari Brantley | $3,865,597 | -- | 3 |
| Devonte Jokubaitis | $57,736,350 | -- | 1 |
| Jalil Vasquez | $6,056,311 | -- | 4 |
| Julian Sabonis | $5,128,688 | -- | 1 |
| Zion Dumont | $9,817,599 | -- | 2 |

Roster count: 15

We're discussing a trade that sends Julian Sabonis to another team for Andre Vasquez at $4,507,546. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 5128688, "incoming_salary": 4507546, "max_incoming": 5128688, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 212146952, "hard_cap_triggered": "none", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $5,128,688, $4,507,546, $5,128,688

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Portland
  2. --- Portland (2026-27) --- (apron salary $212,768,094, over the first apron)
  3. Portland outgoing salary = $5,128,688 (Julian Sabonis $5,128,688)
  4. Portland incoming salary = $4,507,546 (Andre Vasquez $4,507,546)
  5. Portland matching limit = $5,128,688 (100% of outgoing salary (team is over the first apron))
  6. Portland apron salary after the trade = $212,146,952
  7. Verdict: LEGAL
```


## Scenario 17 -- anti_staleness

**What the user said:**

```
2027-28 LEAGUE THRESHOLDS
  Salary cap:          $150,375,000
  Luxury tax line:     $182,705,000
  First apron:         $190,532,000
  Second apron:        $202,083,000
  Non-taxpayer MLE:    $13,715,000
  Taxpayer MLE:        $5,528,000
  Room exception:      $8,539,000
  Tax bracket width:   $5,528,000
  Bi-annual exception: $5,348,000

SACRAMENTO -- 2027-28 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Nico Jokubaitis | $5,059,121 | -- | 2 |
| Kristaps Lindqvist | $6,583,976 | -- | 3 |
| Corey Beauchamp | $6,023,041 | -- | 3 |
| Alperen Ellington | $5,467,043 | -- | 4 |
| Kobe Kearns | $42,966,332 | -- | 4 |
| Nico Boateng | $14,031,890 | -- | 3 |
| Deni Novak | $6,954,293 | -- | 1 |
| Malik Nakamura | $11,226,632 | -- | 4 |
| Kristaps Cordero | $20,731,421 | -- | 3 |
| Alperen Cordero | $3,396,455 | -- | 1 |
| Zion Vasquez | $6,218,242 | -- | 3 |
| Amari Petrov | $37,869,471 | -- | 4 |
| Darnell Jokubaitis | $7,008,743 | -- | 1 |
| Amari Achiuwa | $5,823,328 | -- | 3 |
| Nico Amadi | $6,415,661 | -- | 2 |

Roster count: 15

Using the 2027-28 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2027-28", "apron_salary": 185775649, "apron_level": "over the tax line", "first_apron_provided": 190532000, "second_apron_provided": 202083000, "would_be_wrong_using_published_figures": "over the first apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $185,775,649, $202,083,000

**Computation trace (the only figures you may use):**

```
  1. Sacramento apron salary = $185,775,649
  2. 2027-28 first apron (from the figures provided) = $190,532,000
  3. 2027-28 second apron (from the figures provided) = $202,083,000
  4. Position: over the tax line
  5. Room below the second apron = $16,307,351
```


## Scenario 18 -- anti_staleness

**What the user said:**

```
2027-28 LEAGUE THRESHOLDS
  Salary cap:          $176,706,000
  Luxury tax line:     $214,698,000
  First apron:         $223,896,000
  Second apron:        $237,469,000
  Non-taxpayer MLE:    $16,115,000
  Taxpayer MLE:        $6,496,000
  Room exception:      $10,033,000
  Tax bracket width:   $6,496,000
  Bi-annual exception: $5,867,000

TORONTO -- 2027-28 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Terrance Halvorsen,10361509,0,1
Kristaps Cordero,12986837,0,2
Dante Okoro,25792718,0,1
Amari Ellington,61847099,0,3
Darnell Whitfield,8960593,0,2
Luka Beauchamp,7569115,0,3
Jaylen Amadi,15436579,0,3
Devonte Jokubaitis,7608401,0,4
Malik Ellington,22416081,0,3
Goran Whitfield,6268994,0,3
Marcus Nakamura,7332679,0,4
Micah Stavros,14243982,0,1
Santi Ibarra,9180552,0,2
Andre Nakamura,8628684,0,2
Dante Ellington,13364192,0,1

Roster count: 15

Using the 2027-28 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2027-28", "apron_salary": 231998015, "apron_level": "over the first apron", "first_apron_provided": 223896000, "second_apron_provided": 237469000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $231,998,015, $237,469,000

**Computation trace (the only figures you may use):**

```
  1. Toronto apron salary = $231,998,015
  2. 2027-28 first apron (from the figures provided) = $223,896,000
  3. 2027-28 second apron (from the figures provided) = $237,469,000
  4. Position: over the first apron
  5. Room below the second apron = $5,470,985
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

WASHINGTON -- 2024-25 CAP SHEET
Jaylen Brantley         $5,808,682
Kellen Vasquez          $8,246,954
Goran Marsh            $24,882,134
Amari Whitfield        $44,478,530
Julian Reddish          $2,560,952
Bogdan Ellington        $3,888,729
Brennan Osei            $2,221,921
Rashad Petrov           $8,553,743
Tobias Ibarra           $2,580,477
Nico Okoro              $7,414,010
Trey Vasquez           $19,706,823
Marcus Nakamura         $4,152,208
Zion Ferreira           $7,599,106
Goran Nakamura         $38,320,883
Micah Whitfield         $2,537,893

Roster count: 15
Hard cap: second apron

We're hard-capped at the second apron. Can we add Corey Boateng at $7,807,428?
```

**Ground truth:** {"legal": false, "hard_cap": "second apron", "hard_cap_limit": 188931000, "room_below_hard_cap": 5977955, "salary": 7807428, "apron_salary_after": 190760473, "reasons": ["the signing would put Washington at $190,760,473, above its second apron hard cap of $188,931,000", "Washington already carries 15 players"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $7,807,428, $188,931,000

**Computation trace (the only figures you may use):**

```
  1. Washington apron salary before signing = $182,953,045 (over the first apron)
  2. Proposed salary for Corey Boateng = $7,807,428
  3. Exception: minimum salary exception
  4. Washington apron salary after signing = $190,760,473
  5. Hard cap: second apron = $188,931,000
  6. VIOLATION -- hard cap exceeded = $1,829,473
  7. VIOLATION -- roster is full (15-man limit reached)
  8. Verdict: ILLEGAL
  9. Room below the second apron hard cap before signing = $5,977,955 ($188,931,000 - $182,953,045)
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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Andre Petrov | $22,404,128 | -- | 3 |
| Brennan Osei | $6,385,923 | -- | 4 |
| Elijah Petrov | $5,257,733 | -- | 1 |
| Jaylen Vasquez | $2,423,611 | -- | 4 |
| Trey Beauchamp | $39,264,362 | -- | 2 |
| Bogdan Jokubaitis | $7,770,520 | -- | 2 |
| Deni Rees | $5,790,294 | -- | 2 |
| Nikola Lindqvist | $7,407,118 | -- | 2 |
| Micah Halvorsen | $23,169,438 | $900,000 | 1 |
| Rashad Rees | $5,289,356 | -- | 2 |
| Luka Ellington | $6,980,149 | -- | 2 |
| Jaylen Jokubaitis | $4,809,833 | $900,000 | 2 |
| Devonte Halvorsen | $44,048,084 | -- | 4 |
| Amari Halvorsen | $4,525,760 | -- | 4 |
| Goran Okoro | $5,344,909 | $900,000 | 3 |

Roster count: 15

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 190871218, "unlikely_incentives": 2700000, "apron_salary": 193571218, "apron_level": "over the tax line", "room_to_first_apron": 2373782, "room_to_second_apron": 14252782}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $193,571,218

**Computation trace (the only figures you may use):**

```
  1. San Antonio salaries plus likely incentives = $190,871,218
  2. Unlikely incentives = $2,700,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $193,571,218
  4. 2025-26 luxury tax line = $187,895,000
  5. 2025-26 first apron = $195,945,000
  6. 2025-26 second apron = $207,824,000
  7. Position: over the tax line
  8. Amount above the tax line = $5,676,218
  9. Room below the first apron = $2,373,782
  10. Room below the second apron = $14,252,782
```


## Scenario 21 -- stretch_provision

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

If we waive and stretch Deni Achiuwa -- $95,700,000 left over 3 years -- what does the dead money look like, and is it even allowed?
```

**Ground truth:** {"legal": false, "remaining_salary": 95700000, "years_remaining": 3, "stretch_years": 7, "annual_dead_money": 13671429, "existing_stretched": 15500000, "limit": 23197050, "givebacks_required": 41820653, "reason": "the stretch is not legal as structured: $29,171,429 of dead money would exceed the $23,197,050 ceiling by $5,974,379 per season. The player would have to give back roughly $41,820,653 for the waiver to work"}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $13,671,429, $23,197,050

**Computation trace (the only figures you may use):**

```
  1. Salary remaining on the contract = $95,700,000
  2. Years remaining (3)
  3. Stretch period (2 x 3 + 1 = 7 seasons)
  4. Annual dead money if stretched = $13,671,429 ($95,700,000 / 7)
  5. Dead money already stretched = $15,500,000
  6. Total stretched dead money = $29,171,429
  7. Limit (15% of the 2025-26 cap) = $23,197,050 (15% x $154,647,000)
  8. VIOLATION -- exceeds the dead-money ceiling = $5,974,379
  9. Approximate giveback required = $41,820,653 ($5,974,379 x 7 seasons)
```


## Scenario 22 -- trade_legality

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
Deni Halvorsen           $5,902,142
Zion Kearns             $22,882,819
Bogdan Lindqvist         $6,598,706
Nico Nakamura            $3,781,581
Dante Novak              $4,717,175
Amari Cordero           $20,468,066
Amari Whitfield          $8,957,100
Corey Duval              $6,046,332
Terrance Rees           $47,648,001
Bogdan Petrov            $4,499,684
Kobe Dumont              $5,421,920
Jalil Kearns            $10,554,315
Marcus Rees             $20,730,430
Jaylen Jokubaitis        $9,849,188
Nikola Whitfield         $9,352,683

Roster count: 15

We're discussing a trade that sends Bogdan Petrov and Zion Kearns to another team for Isaiah Lindqvist at $20,336,503. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 27382503, "incoming_salary": 20336503, "max_incoming": 27382503, "matching_rule": "100% of outgoing salary (team is over the first apron)", "apron_level": "over the first apron", "apron_salary_after": 180364142, "hard_cap_triggered": "second apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $27,382,503, $20,336,503, $27,382,503

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Miami
  2. --- Miami (2024-25) --- (apron salary $187,410,142, over the first apron)
  3. Miami outgoing salary = $27,382,503 (Bogdan Petrov $4,499,684, Zion Kearns $22,882,819)
  4. Miami incoming salary = $20,336,503 (Isaiah Lindqvist $20,336,503)
  5. Miami matching limit = $27,382,503 (100% of outgoing salary (team is over the first apron))
  6. Miami hard-capped at the second apron = $188,931,000 (aggregated two or more salaries in one trade)
  7. Miami apron salary after the trade = $180,364,142
  8. Miami stays under its second apron hard cap = $8,566,858 ($188,931,000 - $180,364,142 of room to spare)
  9. Verdict: LEGAL
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

SACRAMENTO -- 2025-26 CAP SHEET
player,salary,unlikely_incentives,years_remaining
Corey Dumont,11938836,0,2
Julian Duval,8245647,0,4
Tobias Reddish,8161940,0,1
Deni Reddish,12382748,0,1
Nico Rees,9527939,0,4
Julian Halvorsen,6988374,0,3
Kristaps Cordero,9825914,0,1
Terrance Sabonis,9358477,0,2
Rashad Ellington,9873100,0,1
Jalil Ellington,5365629,0,2
Marcus Whitfield,23025115,0,2
Brennan Marsh,54126450,0,4
Goran Osei,7941280,0,4
Malik Novak,32082725,0,2
Cam Sabonis,10212765,0,4

Roster count: 15

How much tax are we paying at this payroll?
```

**Ground truth:** {"tax_salary": 219056939, "tax_line": 187895000, "amount_over": 31161939, "is_repeater": false, "total": 105276149, "brackets": [{"index": 1, "amount": 5685000, "rate": 1.0, "owed": 5685000}, {"index": 2, "amount": 5685000, "rate": 1.25, "owed": 7106250}, {"index": 3, "amount": 5685000, "rate": 3.5, "owed": 19897500}, {"index": 4, "amount": 5685000, "rate": 4.75, "owed": 27003750}, {"index": 5, "amount": 5685000, "rate": 5.25, "owed": 29846250}, {"index": 6, "amount": 2736939, "rate": 5.75, "owed": 15737399}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $105,276,149, $31,161,939

**Computation trace (the only figures you may use):**

```
  1. Sacramento tax salary = $219,056,939
  2. 2025-26 luxury tax line = $187,895,000
  3. Amount over the tax line = $31,161,939 ($219,056,939 - $187,895,000)
  4. Rate schedule: standard (2025-26) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $5,685,000 at $1.00 per dollar = $5,685,000
  6. Bracket 2: $5,685,000 at $1.25 per dollar = $7,106,250
  7. Bracket 3: $5,685,000 at $3.50 per dollar = $19,897,500
  8. Bracket 4: $5,685,000 at $4.75 per dollar = $27,003,750
  9. Bracket 5: $5,685,000 at $5.25 per dollar = $29,846,250
  10. Bracket 6: $2,736,939 at $5.75 per dollar = $15,737,399
  11. Total luxury tax owed = $105,276,149
  12. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 24 -- trade_legality

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
Dante Nakamura,5497616,0,2
Corey Kalinic,26913415,0,2
Bogdan Beauchamp,5932316,0,1
Bogdan Osei,4242648,0,1
Elijah Halvorsen,6402867,0,2
Nikola Dumont,10015084,0,4
Cam Reddish,7291469,0,2
Santi Jokubaitis,7687535,0,2
Santi Vasquez,55658370,0,3
Luka Cordero,3095293,0,2
Dante Cordero,6933760,0,3
Brennan Dumont,4934193,0,3
Zion Kalinic,4791976,0,2
Andre Dumont,13419991,0,3

Roster count: 14

We're discussing a trade that sends Cam Reddish to another team for Nikola Cordero at $13,925,019. Is that legal for us, and what does it do to our cap situation?
```

**Ground truth:** {"legal": true, "outgoing_salary": 7291469, "incoming_salary": 13925019, "max_incoming": 14832938, "matching_rule": "200% + $250,000 (outgoing at or below $9,096,000)", "apron_level": "under the tax line", "apron_salary_after": 169450083, "hard_cap_triggered": "first apron", "violations": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $7,291,469, $13,925,019, $14,832,938

**Computation trace (the only figures you may use):**

```
  1. Evaluating a 1-team trade: Sacramento
  2. --- Sacramento (2026-27) --- (apron salary $162,816,533, under the tax line)
  3. Sacramento outgoing salary = $7,291,469 (Cam Reddish $7,291,469)
  4. Sacramento incoming salary = $13,925,019 (Nikola Cordero $13,925,019)
  5. Sacramento matching limit = $14,832,938 (200% + $250,000 (outgoing at or below $9,096,000))
  6. Sacramento hard-capped at the first apron = $209,015,000 (took back more than 100% of outgoing salary)
  7. Sacramento apron salary after the trade = $169,450,083
  8. Sacramento stays under its first apron hard cap = $39,564,917 ($209,015,000 - $169,450,083 of room to spare)
  9. Verdict: LEGAL
```


## Scenario 25 -- hard_cap_consequence

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
Trey Nakamura            $49,205,800
Nico Duval                $8,271,431
Terrance Lindqvist        $8,858,717
Alperen Nakamura          $9,731,289
Nikola Dumont             $7,091,065
Julian Ibarra             $2,668,226
Andre Whitfield          $17,098,195
Kristaps Kearns           $9,841,978
Rashad Boateng            $7,559,291
Julian Achiuwa            $7,700,853
Nico Whitfield           $31,965,849
Trey Brantley             $4,731,101
Rashad Dumont             $8,123,594

Roster count: 13
Hard cap: first apron

We're hard-capped at the first apron. Can we add Kellen Marsh at $3,658,267?
```

**Ground truth:** {"legal": true, "hard_cap": "first apron", "hard_cap_limit": 178132000, "room_below_hard_cap": 5284611, "salary": 3658267, "apron_salary_after": 176505656, "reasons": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $3,658,267, $178,132,000

**Computation trace (the only figures you may use):**

```
  1. Houston apron salary before signing = $172,847,389 (over the tax line)
  2. Proposed salary for Kellen Marsh = $3,658,267
  3. Exception: minimum salary exception
  4. Houston apron salary after signing = $176,505,656
  5. Hard cap: first apron = $178,132,000
  6. Room below the hard cap = $1,626,344
  7. Verdict: LEGAL
  8. Room below the first apron hard cap before signing = $5,284,611 ($178,132,000 - $172,847,389)
```


## Scenario 26 -- buyout_market

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
Darnell Osei,5705366,0,2
Kellen Vasquez,6329764,0,1
Zion Marsh,5428180,0,4
Devonte Duval,5892861,0,1
Amari Ellington,20622544,0,4
Bogdan Novak,39821490,0,2
Santi Cordero,2580284,0,4
Deni Ferreira,14986313,0,2
Nikola Whitfield,5053263,0,2
Kobe Petrov,3265781,0,3
Micah Rees,22426191,0,3
Jalil Vasquez,6139400,0,2
Marcus Beauchamp,4804945,0,4
Andre Ferreira,9012711,0,4
Kobe Lindqvist,40502224,0,1

Roster count: 15

Julian Kearns is about to be bought out -- he was making $33,900,000 before the waiver. Can we sign him?
```

**Ground truth:** {"allowed": true, "pre_waiver_salary": 33900000, "non_taxpayer_mle": 14104000, "apron_level": "over the tax line", "reason": "San Antonio is not over the first apron, so the buyout restriction does not apply"}

**Verdict:** ALLOWED

**Required figures (must all appear):** $33,900,000, $14,104,000

**Computation trace (the only figures you may use):**

```
  1. San Antonio apron status = $192,571,317 (over the tax line)
  2. Player's pre-waiver salary = $33,900,000
  3. 2025-26 non-taxpayer mid-level = $14,104,000
  4. Allowed (San Antonio is not over the first apron, so the buyout restriction does not apply)
```


## Scenario 27 -- exception_eligibility

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
Bogdan Beauchamp       $17,103,567
Marcus Cordero          $3,284,571
Marcus Vasquez          $3,526,605
Bogdan Novak            $5,499,829
Devonte Kearns         $26,215,863
Nico Nakamura          $20,637,838
Zion Novak              $7,992,199
Corey Achiuwa           $8,185,603
Alperen Duval           $4,813,582
Kristaps Dumont        $46,722,262
Kobe Amadi              $7,294,480
Andre Cordero           $3,789,787
Zion Whitfield         $18,811,809

Roster count: 13

Can we sign Elijah Jokubaitis for $7,088,972 using the taxpayer mid-level exception? If it works, tell me what it costs us in flexibility.
```

**Ground truth:** {"legal": false, "exception": "taxpayer mid-level exception", "salary": 7088972, "hard_cap_triggered": "none", "apron_level": "under the tax line", "apron_salary_after": 180966967, "reasons": ["$7,088,972 exceeds the taxpayer mid-level exception of $5,685,000 by $1,403,972"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $7,088,972

**Computation trace (the only figures you may use):**

```
  1. Miami apron salary before signing = $173,877,995 (under the tax line)
  2. Proposed salary for Elijah Jokubaitis = $7,088,972
  3. Exception: taxpayer mid-level exception
  4. taxpayer mid-level exception maximum = $5,685,000
  5. VIOLATION -- salary exceeds the exception amount = $1,403,972
  6. Miami apron salary after signing = $180,966,967
  7. Hard cap: second apron = $207,824,000
  8. Room below the hard cap = $26,857,033
  9. Verdict: ILLEGAL
```


## Scenario 28 -- anti_staleness

**What the user said:**

```
2027-28 LEAGUE THRESHOLDS
  Salary cap:          $178,982,000
  Luxury tax line:     $217,464,000
  First apron:         $226,780,000
  Second apron:        $240,528,000
  Non-taxpayer MLE:    $16,323,000
  Taxpayer MLE:        $6,579,000
  Room exception:      $10,162,000
  Tax bracket width:   $6,579,000
  Bi-annual exception: $5,943,000

INDIANA -- 2027-28 CAP SHEET
Terrance Halvorsen       $20,500,455
Andre Whitfield           $2,882,631
Malik Jokubaitis         $17,025,064
Jaylen Achiuwa           $49,399,716
Tobias Okoro             $51,513,722
Brennan Marsh             $5,008,881
Jalil Reddish             $6,885,746
Dante Novak              $20,481,664
Dante Boateng             $3,773,481
Amari Reddish            $27,975,958
Marcus Sabonis            $4,829,841
Darnell Kearns            $3,968,357
Bogdan Osei               $7,208,881

Roster count: 13

Using the 2027-28 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2027-28", "apron_salary": 221454397, "apron_level": "over the tax line", "first_apron_provided": 226780000, "second_apron_provided": 240528000, "would_be_wrong_using_published_figures": "over the first apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $221,454,397, $240,528,000

**Computation trace (the only figures you may use):**

```
  1. Indiana apron salary = $221,454,397
  2. 2027-28 first apron (from the figures provided) = $226,780,000
  3. 2027-28 second apron (from the figures provided) = $240,528,000
  4. Position: over the tax line
  5. Room below the second apron = $19,073,603
```


## Scenario 29 -- apron_status

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
Alperen Ibarra,46688624,0,2
Zion Achiuwa,25924318,0,2
Elijah Boateng,30057194,0,3
Kellen Petrov,14708609,0,2
Andre Halvorsen,29833646,0,4
Elijah Sabonis,6385074,666666,1
Kristaps Ferreira,5149629,0,4
Tobias Beauchamp,6864708,0,1
Devonte Petrov,7200677,0,2
Amari Ellington,8467817,0,3
Amari Petrov,7143015,666666,3
Rashad Amadi,3744107,0,4
Marcus Achiuwa,4801969,666668,4

Roster count: 13

Where do we sit relative to the tax and the aprons right now?
```

**Ground truth:** {"tax_salary": 196969387, "unlikely_incentives": 2000000, "apron_salary": 198969387, "apron_level": "over the first apron", "room_to_first_apron": -3024387, "room_to_second_apron": 8854613}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $198,969,387

**Computation trace (the only figures you may use):**

```
  1. Atlanta salaries plus likely incentives = $196,969,387
  2. Unlikely incentives = $2,000,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $198,969,387
  4. 2025-26 luxury tax line = $187,895,000
  5. 2025-26 first apron = $195,945,000
  6. 2025-26 second apron = $207,824,000
  7. Position: over the first apron
  8. Amount above the tax line = $11,074,387
  9. Amount above the first apron = $3,024,387
  10. Room below the second apron = $8,854,613
```


## Scenario 30 -- anti_staleness

**What the user said:**

```
2028-29 LEAGUE THRESHOLDS
  Salary cap:          $174,000,000
  Luxury tax line:     $211,410,000
  First apron:         $220,468,000
  Second apron:        $233,833,000
  Non-taxpayer MLE:    $15,868,000
  Taxpayer MLE:        $6,396,000
  Room exception:      $9,879,000
  Tax bracket width:   $6,396,000
  Bi-annual exception: $5,777,000

ORLANDO -- 2028-29 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Dante Reddish | $10,887,256 | -- | 4 |
| Tobias Okoro | $8,323,468 | -- | 1 |
| Zion Stavros | $34,793,759 | -- | 1 |
| Darnell Petrov | $60,899,999 | -- | 4 |
| Jalil Brantley | $30,769,223 | -- | 3 |
| Kristaps Rees | $6,067,808 | -- | 4 |
| Cam Novak | $8,286,337 | -- | 3 |
| Marcus Boateng | $5,544,065 | -- | 1 |
| Deni Nakamura | $14,799,736 | -- | 3 |
| Luka Osei | $21,386,453 | -- | 4 |
| Elijah Stavros | $3,954,082 | -- | 3 |
| Jalil Whitfield | $6,469,002 | -- | 2 |
| Jaylen Lindqvist | $5,786,352 | -- | 4 |
| Rashad Novak | $4,086,249 | -- | 3 |
| Malik Rees | $11,058,737 | -- | 1 |

Roster count: 15

Using the 2028-29 thresholds above, where does this payroll put us, and which restrictions apply?
```

**Ground truth:** {"season": "2028-29", "apron_salary": 233112526, "apron_level": "over the first apron", "first_apron_provided": 220468000, "second_apron_provided": 233833000, "would_be_wrong_using_published_figures": "over the second apron", "note": "The thresholds in the prompt are the only valid source. Answering from any memorized season's figures gives the wrong tier here."}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $233,112,526, $233,833,000

**Computation trace (the only figures you may use):**

```
  1. Orlando apron salary = $233,112,526
  2. 2028-29 first apron (from the figures provided) = $220,468,000
  3. 2028-29 second apron (from the figures provided) = $233,833,000
  4. Position: over the first apron
  5. Room below the second apron = $720,474
```


## Scenario 31 -- tax_bill

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
| Jalil Reddish | $4,364,873 | -- | 2 |
| Elijah Nakamura | $5,744,122 | -- | 4 |
| Corey Rees | $5,637,481 | -- | 3 |
| Terrance Ellington | $2,403,155 | -- | 1 |
| Elijah Lindqvist | $41,425,777 | -- | 3 |
| Alperen Halvorsen | $6,080,366 | -- | 2 |
| Trey Dumont | $7,850,240 | -- | 2 |
| Marcus Nakamura | $15,257,537 | -- | 3 |
| Corey Sabonis | $38,931,556 | -- | 4 |
| Andre Ibarra | $7,144,090 | -- | 1 |
| Kobe Stavros | $13,734,247 | -- | 1 |
| Brennan Jokubaitis | $8,121,044 | -- | 2 |
| Zion Sabonis | $20,752,447 | -- | 4 |
| Jaylen Reddish | $3,492,559 | -- | 4 |
| Darnell Cordero | $3,712,339 | -- | 4 |

Roster count: 15
Repeater taxpayer: yes

What's our luxury tax bill this season? Walk me through the brackets.
```

**Ground truth:** {"tax_salary": 184651833, "tax_line": 170814000, "amount_over": 13837833, "is_repeater": true, "total": 39388416, "brackets": [{"index": 1, "amount": 5168000, "rate": 2.5, "owed": 12920000}, {"index": 2, "amount": 5168000, "rate": 2.75, "owed": 14212000}, {"index": 3, "amount": 3501833, "rate": 3.5, "owed": 12256416}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $39,388,416, $13,837,833

**Computation trace (the only figures you may use):**

```
  1. Charlotte tax salary = $184,651,833
  2. 2024-25 luxury tax line = $170,814,000
  3. Amount over the tax line = $13,837,833 ($184,651,833 - $170,814,000)
  4. Rate schedule: repeater (2024-25) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $5,168,000 at $2.50 per dollar = $12,920,000
  6. Bracket 2: $5,168,000 at $2.75 per dollar = $14,212,000
  7. Bracket 3: $3,501,833 at $3.50 per dollar = $12,256,416
  8. Total luxury tax owed = $39,388,416
  9. Repeater status applies (paid the tax in 3 of the prior 4 seasons)
  10. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 32 -- scenario_planning

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
Trey Novak              $4,432,225
Bogdan Novak           $37,476,671
Andre Brantley         $47,509,742
Goran Brantley          $6,065,569
Trey Kalinic            $2,296,000
Corey Osei              $4,686,115
Andre Ferreira         $27,126,974
Isaiah Rees             $6,730,142
Alperen Nakamura        $2,524,371
Andre Stavros           $6,779,953
Andre Lindqvist        $14,012,730
Kellen Boateng          $4,203,378
Jaylen Petrov           $6,250,239
Alperen Vasquez        $25,118,979
Amari Nakamura         $20,956,546

Roster count: 15

Ownership wants us out of the second apron. Walk me through how we do it.
```

**Ground truth:** {"apron_salary": 216169634, "second_apron": 207824000, "overage": 8345634, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Andre Lindqvist", "salary": 14012730, "surplus": 5667096}, {"player": "Amari Nakamura", "salary": 20956546, "surplus": 12610912}, {"player": "Alperen Vasquez", "salary": 25118979, "surplus": 16773345}, {"player": "Andre Ferreira", "salary": 27126974, "surplus": 18781340}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $8,345,634

**Computation trace (the only figures you may use):**

```
  1. Brooklyn apron salary = $216,169,634
  2. 2025-26 second apron = $207,824,000
  3. Amount over the second apron = $8,345,634
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Andre Lindqvist alone clears the gap = $5,667,096 ($14,012,730 out against $8,345,634 of overage, assuming no salary comes back)
  7. Moving Amari Nakamura alone clears the gap = $12,610,912 ($20,956,546 out against $8,345,634 of overage, assuming no salary comes back)
  8. Moving Alperen Vasquez alone clears the gap = $16,773,345 ($25,118,979 out against $8,345,634 of overage, assuming no salary comes back)
  9. Moving Andre Ferreira alone clears the gap = $18,781,340 ($27,126,974 out against $8,345,634 of overage, assuming no salary comes back)
```


## Scenario 33 -- hard_cap_consequence

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
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| Luka Cordero | $5,512,174 | -- | 1 |
| Brennan Cordero | $6,504,785 | -- | 1 |
| Trey Ferreira | $7,188,214 | -- | 3 |
| Rashad Rees | $5,234,240 | -- | 2 |
| Jalil Reddish | $3,849,529 | -- | 1 |
| Goran Ellington | $8,343,435 | -- | 3 |
| Malik Jokubaitis | $21,165,693 | -- | 3 |
| Alperen Ferreira | $14,970,972 | -- | 3 |
| Deni Whitfield | $17,420,215 | -- | 3 |
| Nico Whitfield | $50,508,426 | -- | 1 |
| Goran Beauchamp | $3,604,868 | -- | 4 |
| Kellen Osei | $46,184,191 | -- | 2 |
| Andre Sabonis | $20,612,495 | -- | 4 |
| Nico Duval | $6,448,326 | -- | 2 |

Roster count: 14
Hard cap: second apron

We're hard-capped at the second apron. Can we add Cam Amadi at $3,362,774?
```

**Ground truth:** {"legal": true, "hard_cap": "second apron", "hard_cap_limit": 221686000, "room_below_hard_cap": 4138437, "salary": 3362774, "apron_salary_after": 220910337, "reasons": []}

**Verdict:** LEGAL

**Required figures (must all appear):** $3,362,774, $221,686,000

**Computation trace (the only figures you may use):**

```
  1. Memphis apron salary before signing = $217,547,563 (over the first apron)
  2. Proposed salary for Cam Amadi = $3,362,774
  3. Exception: minimum salary exception
  4. Memphis apron salary after signing = $220,910,337
  5. Hard cap: second apron = $221,686,000
  6. Room below the hard cap = $775,663
  7. Verdict: LEGAL
  8. Room below the second apron hard cap before signing = $4,138,437 ($221,686,000 - $217,547,563)
```


## Scenario 34 -- exception_survey

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
Rashad Achiuwa,2567302,0,3
Nico Novak,7178301,0,3
Corey Rees,7014063,0,1
Luka Ferreira,40358746,0,2
Isaiah Duval,31523320,0,2
Corey Dumont,7992525,0,3
Amari Vasquez,22798036,0,2
Elijah Petrov,2533994,0,2
Zion Petrov,4863608,0,4
Jalil Whitfield,3115792,0,2
Luka Whitfield,3313624,0,1
Dante Amadi,10855714,0,3
Goran Halvorsen,6717354,0,4

Roster count: 13

Which exceptions can we actually use at this payroll?
```

**Ground truth:** {"apron_level": "under the tax line", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": true, "amount": 12822000, "reason": "available at $12,822,000; using it hard-caps the team at the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 5168000, "reason": "available at $5,168,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": true, "amount": null, "reason": "available, but the published amount for this season is not on file", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Brooklyn apron salary = $150,832,379 (under the tax line)
  2. 2024-25 first apron = $178,132,000
  3. 2024-25 second apron = $188,931,000
  4. non-taxpayer mid-level exception: available = $12,822,000 (available at $12,822,000; using it hard-caps the team at the first apron)
  5. taxpayer mid-level exception: available = $5,168,000 (available at $5,168,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: available (available, but the published amount for this season is not on file)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 35 -- exception_survey

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
Luka Nakamura          $4,926,949
Micah Sabonis         $26,336,274
Corey Boateng          $5,271,475
Amari Nakamura         $8,423,441
Kellen Ibarra         $48,505,923
Amari Osei             $6,853,816
Bogdan Achiuwa         $5,165,875
Marcus Novak           $6,027,238
Goran Osei             $6,440,964
Luka Rees              $5,147,151
Santi Lindqvist       $18,001,845
Jaylen Cordero         $7,482,698
Zion Kalinic           $9,356,888

Roster count: 13

Which exceptions can we actually use at this payroll?
```

**Ground truth:** {"apron_level": "under the tax line", "exceptions": [{"name": "non-taxpayer mid-level exception", "available": true, "amount": 12822000, "reason": "available at $12,822,000; using it hard-caps the team at the first apron", "hard_cap": "first apron"}, {"name": "taxpayer mid-level exception", "available": true, "amount": 5168000, "reason": "available at $5,168,000; using it hard-caps the team at the second apron", "hard_cap": "second apron"}, {"name": "bi-annual exception", "available": true, "amount": null, "reason": "available, but the published amount for this season is not on file", "hard_cap": "first apron"}, {"name": "room exception", "available": false, "amount": null, "reason": "only available to a team operating under the cap", "hard_cap": "none"}, {"name": "minimum salary exception", "available": true, "amount": null, "reason": "always available at any apron level; triggers no hard cap", "hard_cap": "none"}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** none

**Computation trace (the only figures you may use):**

```
  1. Orlando apron salary = $157,940,537 (under the tax line)
  2. 2024-25 first apron = $178,132,000
  3. 2024-25 second apron = $188,931,000
  4. non-taxpayer mid-level exception: available = $12,822,000 (available at $12,822,000; using it hard-caps the team at the first apron)
  5. taxpayer mid-level exception: available = $5,168,000 (available at $5,168,000; using it hard-caps the team at the second apron)
  6. bi-annual exception: available (available, but the published amount for this season is not on file)
  7. room exception: unavailable (only available to a team operating under the cap)
  8. minimum salary exception: available (always available at any apron level; triggers no hard cap)
```


## Scenario 36 -- tax_bill

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
Corey Reddish           $57,736,350
Darnell Brantley        $12,517,742
Julian Nakamura         $10,241,355
Corey Whitfield         $36,695,463
Kellen Cordero          $11,610,144
Devonte Nakamura        $10,564,937
Deni Vasquez             $4,242,539
Bogdan Halvorsen         $8,284,141
Isaiah Novak            $11,334,524
Jaylen Ibarra            $8,301,422
Terrance Reddish         $7,868,141
Jaylen Nakamura         $23,740,100
Brennan Ellington        $7,608,672

Roster count: 13

What's our luxury tax bill this season? Walk me through the brackets.
```

**Ground truth:** {"tax_salary": 210745530, "tax_line": 200428000, "amount_over": 10317530, "is_repeater": false, "total": 11380912, "brackets": [{"index": 1, "amount": 6064000, "rate": 1.0, "owed": 6064000}, {"index": 2, "amount": 4253530, "rate": 1.25, "owed": 5316912}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $11,380,912, $10,317,530

**Computation trace (the only figures you may use):**

```
  1. Indiana tax salary = $210,745,530
  2. 2026-27 luxury tax line = $200,428,000
  3. Amount over the tax line = $10,317,530 ($210,745,530 - $200,428,000)
  4. Rate schedule: standard (2026-27) (rates rise $0.50 per bracket beyond the published four)
  5. Bracket 1: $6,064,000 at $1.00 per dollar = $6,064,000
  6. Bracket 2: $4,253,530 at $1.25 per dollar = $5,316,912
  7. Total luxury tax owed = $11,380,912
  8. Tax distribution forfeited (taxpayers receive no share of the 50% distributed to non-taxpaying teams)
```


## Scenario 37 -- scenario_planning

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
| Jaylen Osei | $38,341,955 | -- | 2 |
| Goran Jokubaitis | $7,321,479 | -- | 1 |
| Terrance Sabonis | $29,377,764 | -- | 2 |
| Santi Petrov | $8,543,073 | -- | 2 |
| Elijah Kearns | $7,294,968 | -- | 4 |
| Tobias Reddish | $8,948,280 | -- | 2 |
| Bogdan Beauchamp | $2,627,502 | -- | 1 |
| Malik Amadi | $4,034,590 | -- | 4 |
| Dante Ellington | $5,058,059 | -- | 1 |
| Devonte Petrov | $5,577,529 | -- | 4 |
| Tobias Ibarra | $3,536,764 | -- | 1 |
| Rashad Vasquez | $2,405,317 | -- | 1 |
| Isaiah Amadi | $28,051,930 | -- | 4 |
| Bogdan Rees | $48,315,308 | -- | 1 |
| Terrance Okoro | $3,560,533 | -- | 4 |

Roster count: 15

What's the cleanest path under the second apron from here?
```

**Ground truth:** {"apron_salary": 202995051, "second_apron": 188931000, "overage": 14064051, "aggregation_banned": true, "cash_banned": true, "single_salary_solutions": [{"player": "Isaiah Amadi", "salary": 28051930, "surplus": 13987879}, {"player": "Terrance Sabonis", "salary": 29377764, "surplus": 15313713}, {"player": "Jaylen Osei", "salary": 38341955, "surplus": 24277904}, {"player": "Bogdan Rees", "salary": 48315308, "surplus": 34251257}]}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $14,064,051

**Computation trace (the only figures you may use):**

```
  1. Washington apron salary = $202,995,051
  2. 2024-25 second apron = $188,931,000
  3. Amount over the second apron = $14,064,051
  4. Aggregation unavailable (over the second apron, salaries cannot be combined in a trade)
  5. Cash unavailable (over the second apron, no cash may be sent)
  6. Moving Isaiah Amadi alone clears the gap = $13,987,879 ($28,051,930 out against $14,064,051 of overage, assuming no salary comes back)
  7. Moving Terrance Sabonis alone clears the gap = $15,313,713 ($29,377,764 out against $14,064,051 of overage, assuming no salary comes back)
  8. Moving Jaylen Osei alone clears the gap = $24,277,904 ($38,341,955 out against $14,064,051 of overage, assuming no salary comes back)
  9. Moving Bogdan Rees alone clears the gap = $34,251,257 ($48,315,308 out against $14,064,051 of overage, assuming no salary comes back)
```


## Scenario 38 -- hard_cap_consequence

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
Marcus Cordero           $36,106,962
Santi Osei                $7,529,793
Trey Rees                $29,335,365
Jaylen Rees               $7,908,077
Brennan Jokubaitis        $8,696,021
Trey Jokubaitis           $5,530,948
Marcus Lindqvist          $5,017,744
Bogdan Sabonis            $4,120,924
Kristaps Sabonis          $7,293,899
Jaylen Ibarra             $8,506,212
Dante Lindqvist          $11,049,559
Amari Rees               $57,736,350
Micah Boateng            $10,719,428
Rashad Okoro              $4,803,082

Roster count: 14
Hard cap: first apron

We're hard-capped at the first apron. Can we add Amari Amadi at $5,819,586?
```

**Ground truth:** {"legal": false, "hard_cap": "first apron", "hard_cap_limit": 209015000, "room_below_hard_cap": 4660636, "salary": 5819586, "apron_salary_after": 210173950, "reasons": ["the signing would put Portland at $210,173,950, above its first apron hard cap of $209,015,000"]}

**Verdict:** ILLEGAL

**Required figures (must all appear):** $5,819,586, $209,015,000

**Computation trace (the only figures you may use):**

```
  1. Portland apron salary before signing = $204,354,364 (over the tax line)
  2. Proposed salary for Amari Amadi = $5,819,586
  3. Exception: minimum salary exception
  4. Portland apron salary after signing = $210,173,950
  5. Hard cap: first apron = $209,015,000
  6. VIOLATION -- hard cap exceeded = $1,158,950
  7. Verdict: ILLEGAL
  8. Room below the first apron hard cap before signing = $4,660,636 ($209,015,000 - $204,354,364)
```


## Scenario 39 -- apron_status

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
| Julian Amadi | $7,200,739 | -- | 1 |
| Terrance Reddish | $8,340,637 | -- | 4 |
| Brennan Boateng | $20,797,422 | $333,333 | 2 |
| Elijah Duval | $7,757,367 | -- | 4 |
| Malik Ibarra | $16,285,372 | -- | 3 |
| Jalil Ferreira | $19,060,834 | -- | 1 |
| Trey Ferreira | $4,056,239 | -- | 4 |
| Alperen Petrov | $49,205,800 | -- | 2 |
| Kobe Sabonis | $10,228,505 | $333,333 | 2 |
| Tobias Beauchamp | $9,417,032 | -- | 1 |
| Dante Cordero | $7,011,770 | -- | 1 |
| Dante Kearns | $11,162,254 | $333,334 | 3 |
| Nikola Vasquez | $4,055,292 | -- | 2 |

Roster count: 13

Are we over the second apron? How much room do we have?
```

**Ground truth:** {"tax_salary": 174579263, "unlikely_incentives": 1000000, "apron_salary": 175579263, "apron_level": "over the tax line", "room_to_first_apron": 2552737, "room_to_second_apron": 13351737}

**Verdict:** (no yes/no verdict -- explain the situation)

**Required figures (must all appear):** $175,579,263

**Computation trace (the only figures you may use):**

```
  1. Detroit salaries plus likely incentives = $174,579,263
  2. Unlikely incentives = $1,000,000 (counts toward apron salary only, not cap or tax salary)
  3. Apron salary = $175,579,263
  4. 2024-25 luxury tax line = $170,814,000
  5. 2024-25 first apron = $178,132,000
  6. 2024-25 second apron = $188,931,000
  7. Position: over the tax line
  8. Amount above the tax line = $4,765,263
  9. Room below the first apron = $2,552,737
  10. Room below the second apron = $13,351,737
```


