# Demo prompt template

Paste a current cap sheet, then ask. The model is built to reason from figures it is handed,
so the quality of the answer depends on the quality of the paste. [capsheets.com](https://www.capsheets.com/)
is the best free source and updates promptly after transactions.

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

DENVER -- 2026-27 CAP SHEET
| Player | Salary | Unlikely incentives | Years left |
| --- | ---: | ---: | ---: |
| ... paste your roster here ... |

Roster count: 15
Repeater taxpayer: yes

We need to get under the second apron before the deadline. What are our options,
and what are we giving up?
```

## Questions that show what it does

- "Is this trade legal for us?" — with two or three salaries going out
- "What's our tax bill, and how does it break down by bracket?"
- "Which exceptions do we still have, and what does using each one cost us?"
- "If we waive and stretch him, what's the dead money and is it even allowed?"
- "We're hard-capped at the first apron. Can we add this player?"
- "What happens to our draft picks if we finish the season here?"

## The demo worth running first

Change one threshold in the pasted block and ask the same question again. The answer should
change with it. That is the whole architectural bet: rules and reasoning live in the weights,
figures live in the prompt, and July 1 never makes the model wrong.
