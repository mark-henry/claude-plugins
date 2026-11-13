---
name: draftoff
description: "Write a long or high-stakes document (a skill, a plan, a spec, a report) as a draft-off: three fresh agents each draft the whole thing from the same brief on a different organizing idea, a fourth writes a plain default draft that stays sealed, a judge grafts the best parts onto one base, and a blind pick among the grafted result, the bare base and the default says whether the process beat plain writing. Use for \"/decide:draftoff\", \"draft-off\", \"draft it three ways\", \"get three drafts and merge\", \"write this skill properly\", or any document whose structure is itself an open question. Not for a short document or one with a single sensible structure (just write it), not for improving a draft that exists (decide:improve), not for code or designs that must be built and measured (decide:bakeoff), and not for finding what is wrong with a finished draft (check:attack)."
---

# Draft-off

One writer picks a structure in the first paragraph and never sees the others. A draft-off buys three structures and keeps the best parts of each. Invoking this skill is the go-ahead: say in one line how many agents will run and what it should cost, then run. It is about seven agents on a document of a few thousand words.

## 1. One brief for every drafter

Write a single brief file and give every drafter the same one:

- the situation, in facts;
- what the user wants, in their own words, quoted;
- the specification and every ruling that binds the text, in whole;
- the raw material, by path, marked as material and not as a checklist;
- the form: frontmatter, word limit, companion files allowed;
- the hand-in: the draft at a named path, and a short notes file saying what was left out and why, what in the material contradicts the rulings, and the one thing the drafter is least sure of.

Leave out your own outline, your favorite structure and any earlier draft. State the property the document must have, never an example of it.

## 2. Diverge

Seat four fresh agents on the strongest model, each given only the brief and its own paths, each told to write nothing else and spawn no one.

- Three get an organizing lean, one line each, and they must differ in kind: by the order of events, by the thing that decides (a rule, a checker, an artifact), and the shortest text that would still change what a reader does. One lean may reject the premise.
- The fourth gets no lean. Its draft is the default: what plain writing would have produced. It stays sealed until the pick; the judge and the synthesizer never see it.

Nothing a drafter can see tells it what the other leans are. Seat them as `swarm:go` seats blind agents (Run, Blind seats).

## 3. Graft

A fresh judge who wrote no draft reads the brief, writes down what the ideal document would do before opening any draft, then reads the three and their notes. It picks a base, or rejects all three, and numbers the grafts to take from the others and the defects to fix. A separate synthesizer applies them to the base and logs each graft it changed or declined, with the reason. Where the drafts agree on structure, say so: agreement between independent drafts is the strongest signal the run gives.

## 4. Pick, blind

Before any attack or polish, another fresh judge, ideal first, chooses among three texts: the grafted result, the bare base and the sealed default. They carry neutral shuffled labels with no lean, author or model; the judge runs both orders; it uses only the criteria the brief states; and it is told that length is not merit. "None of these" is a valid result.

The grafted result is nearly a superset of its base, and a superset cannot be blinded, so the comparison that counts is against the default.

## 5. Then check it

The winner is a draft, not a finished text. Run `check:attack` on it once, against the brief. If it condenses sources, run `check:claims` for coverage. Fixes after an attack add words: count them, and say when the text has passed its limit.

## The record

Keep the brief, the four drafts with their notes, the judge's ideal and graft list, the synthesizer's log, the label map and both picks beside the result. Add a line to `${CLAUDE_PLUGIN_DATA}/runs.md`: the document, the leans, the base chosen, which of the three texts won, tokens and time. If the default wins or ties in a third of your runs, the process is not earning its cost: stop using it for that kind of document.

Report: the winner and what it is built from; where the drafts agreed; what the default would have given; the word count against the limit; and last, anything the user must decide.
