# Templates for lab:experiment

Angle brackets are gaps to fill. An empty field is an unchecked threat: fill it or write "n/a: reason". The run record's fields are rule 8's in [SKILL.md](SKILL.md) and are not repeated here; the prereg record's are written by `prereg.py new`.

## plan.md, the experiment's plan page

```markdown
# Plan: <slug>  (<date>; draft | attacked | frozen | closed)    brief: <path>    prereg: <path>
Question: <one>    Decision per outcome: <action for each>
Sentence hoped for: <metric, denominator, comparator, scope>
Sentence per other outcome: null <…> | worse <…> | inconclusive <…> | no arm clears <…>    (the test assigning each)

| H_<NAME> | hypothesis | where the gain concentrates; where the control ties | surprise if |
| BAR_<NAME> | metric | denominator; all-items rate beside it? | pass bar | what a miss means |
Null picture: <the figure if the treatment does nothing, noise band drawn>    Smallest effect worth detecting: <…>

| Arm | differs in (one thing) | buys which word of the sentence | command |
  rows for: untreated; simple baseline (matched budget, for a multi-sample method); constant answer;
  positive control (stages, defined pass); mechanism off; same data without the ingredient <later | n/a: reason>
| Knob | matched / fixed / tuned per arm (budget) | value; tuned on which arm |
  include: warm start, length and token cap, compute, run window, upstream generator or selector (model, commit)
| RIVAL_<NAME> | explanation | arm or check whose failure would show it | found in: plan / trace read |

Floor: <runs, what each seed varies, cost>, or claim narrowed to: <…>
n: <seeds, items, samples per item; why; minimum detectable effect>
Instrument: <checker and why; known pass and near-miss fail; where untreated, constant, pass and fail score; score against length; judge record; how cheats score>
Held-out: <train / dev / sealed and their hashes; runs that have scored sealed; decisions dev has made>
Reward (RL): <strategy: what it is paid>; base pass rate <…>; horizon <…>
| KILL_<NAME> | condition in numbers | set from | action |
Rungs: <rung: cost, stops when>    Cap: <from the brief>    Analysis script: <path>
Amendments: <date; change; reason; code names>
FREEZE <date>: <what rule 7 lists>
```

## read.md

Fill in order; do not look at line 6 before lines 1–5 are written.

```markdown
# Read: <run ids>    <date>
1. Ran as configured: <config diff against the FREEZE; end reason per run; cost; truncation>
2. Instrument ran: <parse yield k/n; errored and missing counted apart from fails>
3. Samples read per arm: <n, drawn by what rule; validity, refusal, length; tampering attempts>
4. Controls: <positive control pass or fail; constant output and simple baseline values; where arms sit between the fixture's pass and fail; score against length>
5. Audit: <evals:audit verdict; run ids; contrasts its sample covered>
6. Headline: <BAR_<NAME>: value, n/N, interval or every seed; untreated and simple baseline beside it; all-items rate; floor>
7. Effective denominator: <items where arms differed>    Other aggregations: <does it survive>
8. Rivals: <RIVAL_<NAME>: excluded by <control> | not excluded; new ones the reading surfaced>
9. Blind read, where a human did one: <path, n, draw rule, taxonomy | n/a: unattended>
10. <H_<NAME>>: hit | miss; confirmed | rejected | unresolved; fired guards and kills; leak audit if above the predicted interval
```

## report.md

```markdown
# <the sentence the supervisor signed, with n>    [confirmatory | exploratory]
prereg <file>: predicted <X>, got <Y> (<n/N>)
<figure: the claim as title; every seed drawn>
What ran: <arms, seeds, items; run ids, killed and relaunched included; cost against the cap>
Beside it: untreated <…>; simple baseline <…>; positive control <…>; floor <…>
Read: parse yield <k/n>; audit <verdict>; effective denominator <…>; gain where predicted? <…>
Not excluded: <RIVAL_…>    Guards and kills that fired: <KILL_…>    Amendments, waivers: <…>
Would change my mind: <…>
Supervisor: <per number: signoff.md's last verdict at quote on its sentence: SIGNED | SIGNED WITH WAIVER | NOT SIGNED: rules unmet, what would meet each; verdicts before it: n>
Next: <proposal, price>
Needs your decision: <numbered, each with a recommendation; or "Nothing needs you.">
```
