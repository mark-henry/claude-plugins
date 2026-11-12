# Templates for swarm:go

Angle brackets are gaps to fill; delete what does not apply.

## plan.md

```markdown
# Plan: <run-name>    brief: <path>, frozen <date>    hash: <of the lines above "## Pilot", recorded in plan.attack.md>
Bar: <from the brief, with its denominator>    Fallback bar: <…>
Cap: <$ and tokens>    Cut first: <from the brief>    Held back for verify and report: <share>
Prediction, written before any result: <expected result and range; what would surprise>
Numbers that will meet a bar: <lab:prereg record, or none>

| Piece (owns) | Cites | Checker | Exists, out of reach? | Work it as, how wide | Model role | Share; stops on | Accepted when |
|---|---|---|---|---|---|---|---|
| <piece> (<files, items>) | <R_NAME> | <machine check, judge, selector, agreement or summary: `command`> | <yes / build first> | <loop, bulk, best-of-N, vote, fan-out; N> | <strongest, general-use or rote-tokens> | <$; M rounds; enforced by the launcher> | <the check that passes, earlier passes included> |
| User's row | <R_NAME> | the user | n/a | one agent readies the question | | | <the question, asked last in the report> |

Order: <waves; what waits on what>
Choices sent out: <choice: decide:vote, decide:improve or decide:bakeoff>
What no piece's check exercises: <failure modes, handed to the final attack>

## Pilot
- <configuration>: check on untouched state <pass / fail>; bar <yield at least …, written before the pilot>; read <n> (<which>); yield <k/n>; <cost per item>; projected <range> against <share>

## Results
- <date> <piece>: <accepted / killed / redirected>, cost <$ or quota %>, review <minutes>, <why>
```

## spend.md, one line per wave

```
<time> | <wave> | top estimate <…> | measured <…>, from <source> | total so far <…> of cap <…>; held back <…>
```

## decisions.md, one line per call

```
D-<n> | <time> | mechanical, taste or assumption | chose <X> over <Y> | why | cost if wrong; what switching takes | evidence: <path, commit>
```

## briefs/<piece>.md, the worker's brief

```markdown
# Brief: <piece>    plan: <path>#<piece> @ <hash>    model role: <…>, effort <…>
Objective, one line: <…>
Read first (absolute paths): <brief.md, rulings.md, …>
Base state: <commit or hash>. Check your workspace matches before editing; stop on a mismatch.
Facts: <numbers with denominators; what was tried and what happened; no diagnosis>
You own: <files, items>. Do not touch: <…>. The user's limits, verbatim: "<…>"
Without the user's word, quoted above: no post, message, pull request, push to a shared branch or merge; nothing this run did not create deleted, overwritten or stopped; nothing irreversible; no security change; no new account, credential or payment. Prepare it, stop there and report. The same line goes to any helper.
Private data: <where it may go>
Done when: `<check>` gives <expected>. The launcher runs checks you cannot see.
Budget: <share; rounds>, enforced by <the launcher>. You may spawn helpers inside this share. Do not seat a reviewer of your own work: hand it back unreviewed.
Exits: if <X> fails after honest attempts, stop and report the exact numbers; do not work around it. A stop with the facts is a good outcome.
Unclear? Return needs_context before building.
Return: write the full result to <absolute path>; reply with the status line and that path only.
```

## results/<piece>.md, the hand-back

```markdown
Status: done | done_with_concerns | needs_context | needs_attack | blocked
If not done: <why, with exact numbers and what was tried>
Result: <paths; commit or hash of the state checked>
Check run: `<command>` gave <output, pasted>; exit <n>; <time>
Checked myself: <…>    Relayed from a helper, a page or a file: <…>
Read in full / skimmed / not read: <…>
Departures from the brief, substitutions: <… or none>
Spend: <of share>    Helpers: <how many, on what>
Reviewed: no; the dispatcher seats the reviewer
Concerns: <…>
```

## runs.md line

```
<date> | swarm:go | <run-name> | <what ran> | cost <actual> against estimate <…> and cap <…> | <hours> | <status>
```

## report.md

```markdown
# Report: <run-name>    STATUS: done | pending (<n> decisions) | stopped at <cap, limit or halt>, pending (<n>)    <"exploratory: no frozen brief", if so>
1. Result against the bar: <met or missed>, on <the bar or the fallback>. Each requirement: <R_NAME: met, partly or not addressed; the check, shown>
2. Where it is: <paths, branch, commits>. Prepared but not pushed, merged or posted: <…>
3. My assumptions and taste calls: <D-n: chose A over B; cost if wrong; what flipping takes>; attack findings left as is, each with its reason
4. Spend: <actual> against estimate <…> and cap <…>; wall time; by piece
5. Numbers quoted: <each with its prereg record or "exploratory", and its audit>
6. Coverage that did not run: <checks, seats, routes; what was not read; models asked for but not served>
7. Released: <each thing this run launched that bills or runs (boxes, endpoints, background loops, timers), with the output showing it is gone>. Left running by the user's word: <their words, or none>
8. Stopped pieces, and the question each waits on:
   - <piece>: <the question, readable cold>. I recommend <…>. Until you answer, <what stands>.
   (or: Nothing needs you.)
```
