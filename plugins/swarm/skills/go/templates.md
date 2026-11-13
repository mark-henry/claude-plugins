# Templates for swarm:go

Angle brackets are gaps to fill; delete what does not apply.

## plan.md

```markdown
# Plan: <run-name>    brief: <path to brief.md or handed.md>
Bar: <from the brief, with its denominator>    Fallback bar: <…>
Cap: <in the brief's unit>    Cut first: <from the brief>    Held back for verify and report: <share>
Prediction, written before any result: <expected result and range; what would surprise>

| Piece (owns) | Checker | Exists? | Work it as, how wide | Model role | Share; round limit | Accepted when |
|---|---|---|---|---|---|---|
| <piece> (<files, items>) | <table row: `command`> | <yes / build first> | <loop, bulk, best-of-N, vote, fan-out; N> | <strongest, general-use or rote-tokens> | <…> | <the check that passes> |
| User's row | the user | | one agent readies the question | | | <the question, asked last in the report> |

Order: <waves; what waits on what>

## Pilot
- <configuration>: check on untouched state <pass / fail>; yield bar <…>; read <n>; yield <k/n>; <cost per item>; projected <range> against <share>

## Results
- <date> <piece>: <accepted / killed / redirected>, cost <$ or quota %>, <why>
```

## spend.md, one line per wave

```
<time> | <wave> | top estimate <…> | measured <…>, from <source> | total <…> of cap <…>; held back <…>
```

## decisions.md, one line per call

```
D-<n> | <time> | mechanical or taste | chose <X> over <Y> | why | cost if wrong
```

## The worker's brief

```markdown
# Brief: <piece>    model role: <…>
Objective, one line: <…>
Read first (absolute paths): <brief.md or handed.md; …>
You own: <files, items>. Do not touch: <…>.
Done when: `<check>` gives <expected>. The launcher runs its own check.
Budget: <share; rounds>, enforced by the launcher.
If it cannot be done as directed, stop and report the exact numbers; do not work around it.
Return: write the result to <absolute path> as below; reply with its Status line and that path only.

Status: done | done_with_concerns | needs_context | blocked
If not done, or concerns: <why, with exact numbers and what was tried>
Result: <paths; commit of the state checked>
Check run: `<command>` gave <output>; exit <n>
Departures from the brief: <… or none>
Spend: <of share>
```

## runs.md line

```
<date> | swarm:go | <run-name> | <what ran> | cost <actual> against estimate <…> and cap <…> | <hours> | <status>
```

## report.md

```markdown
# Report: <run-name>    STATUS: done | pending (<n> decisions) | stopped at <cap or limit>, pending (<n>)    <"exploratory: no frozen brief", if so>
1. Result against the bar: <met or missed>, on <the bar or the fallback>; the check, shown
2. Where it is: <paths, branch, commits>
3. My taste calls: <D-n: chose A over B; cost if wrong>; attack findings left as is, each with its reason
4. Spend: <actual> against estimate <…> and cap <…>; wall time
5. Coverage that did not run: <checks, attacks, pilots; models asked for but not served>
6. Released: <each thing this run launched that bills or runs, with the output showing it is gone>
7. Stopped pieces, and the question each waits on:
   - <piece>: <the question, readable cold>. I recommend <…>. Until you answer, <what stands>.
   (or: Nothing needs you.)
```
