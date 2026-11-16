---
name: draftoff
description: "Write a long or high-stakes document (a skill, a plan, a spec, a report) by draft-off: several fresh drafts on different organizing ideas, grafted into one, then picked blind against a plain draft. Use for \"/decide:draftoff\", \"draft-off\", \"draft it three ways\", \"get three drafts and merge\", \"write this skill properly\", or any document whose structure is itself an open question. Not for a short document or one with a single sensible structure (just write it), not for improving a draft that exists, not for code or designs that must be built and measured."
---

# Draft-off

Invoking this skill is the go-ahead: say in one line how many agents will run and what it should cost, then run.

## 1. One brief for every drafter

One file, the same for every drafter: the situation in facts; the user's words, quoted; the criteria; the rulings in whole; raw material by path (material, not a checklist); the form and word limit. The criteria say what the finished document must do for its reader. Whoever asked for the draft-off passes them in; with none given, draw them from the user's words and say so. The drafters write to them, and every judge judges by them and nothing else. Each drafter hands in a draft and short notes: what it left out and why, where the material contradicts the rulings, and what it is least sure of.

Leave out your own outline, your favorite structure and any earlier draft. State the property the document must have, never an example of it.

## 2. Diverge

Seat four fresh agents on the strongest model, each given only the brief and its own paths (seated blind, as `unattended:go` says), and each with a folder of its own that no other brief names.

- Three get an organizing lean, one line each, and they must differ in kind: by the order of events, by the thing that decides (a rule, a checker, an artifact), and the shortest text that would still change what a reader does. One lean may reject the premise.
- The fourth gets no lean. Its draft is the default: what plain writing would have produced. It stays sealed until the pick: whoever grafts does not open its folder.

## 3. Graft

The grafter is a fresh judge, or you, if you wrote none of the drafts. It reads the brief, writes down what the ideal document would do before opening any draft, then reads the three and their notes. A conflict in the brief that the notes name is fixed in the brief first. It picks a base, or rejects all three, and lists the grafts to take from the others, the defects to fix and where the drafts agree. A separate synthesizer applies them to the base and logs each graft it changed or declined, with the reason.

If you graft, you do not open the default and you do not pick.

## 4. Pick, blind

Before any polish, two fresh judges each rank three texts, ideal first: the grafted result, the bare base and the sealed default. The texts carry neutral shuffled labels with no lean, author or model, and each judge gets a different order. Each uses only the brief's criteria and is told that length is not merit. "None of these" is a valid ranking.

- Both rank the same text first: it wins.
- They differ: a third fresh judge, a third order, breaks the tie.
- Three judges, three different first choices: the outcome is `split`. Carry the grafted result forward and say so.
- Two judges say none of these, or the grafter rejected all three: stop and report what the judges wanted. The brief is the suspect, not the drafters.

## 5. Then check it

Have a fresh agent red-team the winner once, against the brief, running what in it can be run. If it condenses sources, check its coverage against them, each claim opened at its source. Fixes add words: count them, and say when the text has passed its limit.

## The record

Keep the brief, the four drafts with their notes, the ideal and graft list, the synthesizer's log, the label map and every ranking beside the result. Add a row to `${CLAUDE_PLUGIN_DATA}/draftoff.md`, creating it with this header on first use. A run that stops early still gets its row.

```markdown
| Date | Document | Kind | Leans | Grafted by | Base | Rankings (first choice per judge) | Outcome | Tokens | Minutes | Record |
|---|---|---|---|---|---|---|---|---|---|---|
| 2027-01-15 | onboarding guide (example row; delete) | guide | by stage; by checker; shortest | caller | by checker | result, default, result | result | 900k | 50 | <path> |
```

Outcome is one of `result`, `base`, `default`, `none`, `split`, `no pick`. Read the file before a run: when `default` or `split` makes up a third of the rows for a kind of document, the process is not earning its cost for that kind.

Report: the winner and what it is built from; where the drafts agreed; what the default would have given; the word count against the limit; and last, anything the user must decide.
