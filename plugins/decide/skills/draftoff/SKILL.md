---
name: draftoff
description: "Write a long or high-stakes document (a skill, a plan, a spec, a report) by draft-off: several fresh drafts on different organizing ideas, grafted into one, then picked blind against a plain draft. Use for \"/decide:draftoff\", \"draft-off\", \"draft it three ways\", \"get three drafts and merge\", \"write this skill properly\", or any document whose structure is itself an open question. Not for a short document or one with a single sensible structure (just write it), not for improving a draft that exists (decide:improve), not for code or designs that must be built and measured (decide:bakeoff), and not for finding what is wrong with a finished draft (check:attack)."
---

# Draft-off

Invoking this skill is the go-ahead: say in one line how many agents will run and what it should cost, then run.

## 1. One brief for every drafter

Write a single brief file and give every drafter the same one:

- the situation, in facts;
- what the user wants, in their own words, quoted;
- the criteria: what the finished document must do for its reader. Whoever asked for the draft-off passes them in; with none given, draw them from the user's words and say so. The drafters write to them and every judge judges by them, and by nothing else;
- the specification and every ruling that binds the text, in whole;
- the raw material, by path, marked as material and not as a checklist;
- the form: frontmatter, word limit, companion files allowed;
- the hand-in: the draft at a named path, and a short notes file saying what was left out and why, what in the material contradicts the rulings, and the one thing the drafter is least sure of.

Leave out your own outline, your favorite structure and any earlier draft. State the property the document must have, never an example of it.

## 2. Diverge

Seat four fresh agents on the strongest model, each given only the brief and its own paths, each told to write nothing else and spawn no one.

- Three get an organizing lean, one line each, and they must differ in kind: by the order of events, by the thing that decides (a rule, a checker, an artifact), and the shortest text that would still change what a reader does. One lean may reject the premise.
- The fourth gets no lean. Its draft is the default: what plain writing would have produced. It stays sealed until the pick; whoever grafts never sees it.

Nothing a drafter can see tells it what the other leans are. Seat them as `swarm:go` seats blind agents (Run, Blind seats).

## 3. Graft

The grafter is a fresh judge, or you, if you wrote none of the drafts. It reads the brief, writes down what the ideal document would do before opening any draft, then reads the three and their notes. It picks a base, or rejects all three, and numbers the grafts to take from the others and the defects to fix. A separate synthesizer applies them to the base and logs each graft it changed or declined, with the reason. Where the drafts agree on structure, say so: agreement between independent drafts is the strongest signal the run gives.

If you graft, you do not open the default and you do not pick.

## 4. Pick, blind

Before any attack or polish, two fresh judges each rank three texts, ideal first: the grafted result, the bare base and the sealed default. The texts carry neutral shuffled labels with no lean, author or model, and each judge gets a different order. Each uses only the brief's criteria and is told that length is not merit. "None of these" is a valid ranking.

- Both rank the same text first: it wins.
- They differ: a third fresh judge, a third order, breaks the tie.
- Three judges, three different first choices: the outcome is `split`. Carry the grafted result forward and say so.
- Two judges say none of these, or the grafter rejected all three: stop and report what the judges wanted. The brief is the suspect, not the drafters.

## 5. Then check it

The winner is a draft, not a finished text. Run `check:attack` on it once, against the brief. If it condenses sources, run `check:claims` for coverage. Fixes after an attack add words: count them, and say when the text has passed its limit.

## The record

Keep the brief, the four drafts with their notes, the ideal and graft list, the synthesizer's log, the label map and every ranking beside the result. Add a row to `${CLAUDE_PLUGIN_DATA}/draftoff.md`, creating it with this header on first use. A run that stops early still gets its row.

```markdown
| Date | Document | Kind | Leans | Grafted by | Base | Rankings (first choice per judge) | Outcome | Tokens | Minutes | Record |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-12 | swarm:go | skill | by stage; by checker; shortest | caller | by checker | result, result | result | 1.1M | 55 | <path> |
```

Outcome is one of `result`, `base`, `default`, `none`, `split`, `no pick`. Read the file before a run: when `default` or `split` makes up a third of the rows for a kind of document, the process is not earning its cost for that kind.

Report: the winner and what it is built from; where the drafts agreed; what the default would have given; the word count against the limit; and last, anything the user must decide.
