---
name: vote
description: "Pick among discrete options by blind vote: two voters on different models rank the options in different orders; if they disagree, heavier tiebreakers vote one at a time until one option has a majority, and a split is reported as a split. Use for \"/decide:vote\", \"vote on it\", \"put it to a vote\", \"which of these\", \"pick one of\", choosing a name, library, approach or answer from a short list, or when the options are already known and the question is which. Not for writing the options (ask fresh agents for their best answers, or use decide:draftoff or decide:bakeoff), not for improving one proposal (decide:improve), and not for a question of fact (run the check)."
---

# Put it to a vote

A vote picks one of several options that already exist. Invoking this skill is the go-ahead: say in one line which seats will vote and what it should cost, then run. The script is `vote.js` in this directory. `scriptPath` refuses plugin paths, so copy it to your scratchpad and run `Workflow({scriptPath: "<scratchpad>/vote.js", args: {...}})`, from a turn that carries no favorite (`swarm:go`, "Your check decides accepted").

How it works:

1. **Two voters** rank every option by letter, each seeing a different order. They mark any option that breaks a hard constraint, and may say that none is acceptable or that the question is wrongly framed.
2. **If they agree** on a first choice, that is the result and nobody else is asked.
3. **If they differ,** tiebreakers vote one at a time, each heavier than the last, until one option holds a majority of first choices or the seats run out.
4. **Code tallies:** first choices, Borda points and the Condorcet winner. An option a majority marks as breaking a constraint is left out of every tally. A majority for "none of these" means no winner. Seats exhausted without a majority is a split, and a split has no winner, only a leader.

## Seats

Two voters who agree are worth more when their mistakes are not the same mistakes. No two voters may be the same seat: the script refuses two that share model, effort and persona.

- **Voters:** two different general-use models, from different families where the user's settings name a route to more than one. With one model only, the same model at two effort levels or as two personas; the defaults are two personas on the session's model.
- **First tiebreaker:** the next model up from the voters.
- **Second tiebreaker:** stronger still, or the strongest of another family, your choice.
- The rote-tokens model is not seated: it adds a vote without adding judgment.

The user's settings say which model fills each role. A seat is `{model}` or `{agentType}`, with an optional `effort` and `persona`. Say in the report which seats differed in what.

## Before launch

1. **The question** has a discrete answer: "which library", "which name", "which of these plans". If the honest answer is a blend, use `decide:improve`. A question of fact is never voted on: run the test, lookup or computation.
2. **The options** are yours to bring, in full. Include the current choice, so the incumbent can win, and merge near-twins yourself: two of them split the vote and hand the win to a worse third. With no options yet, ask a few fresh agents for their best answers independently and pool what comes back; for a document use `decide:draftoff`, for a design `decide:bakeoff`.
3. **Context for strangers.** The voters know nothing of this conversation. Give them facts, numbers with denominators and paths to open; put hard limits in `constraints` and what to judge by in `criteria`. Leave out which option you favor.

## Args

| arg | meaning |
|---|---|
| `question` | required |
| `options` | required: two or more strings or `{label, option}` |
| `goal`, `context`, `constraints`, `criteria` | `constraints` are hard limits (an option that breaks one is out); `criteria` is what to judge by |
| `voters` | seats for the first round, no two alike; default two personas on the session's model |
| `tiebreakers` | seats asked one at a time while undecided, heaviest last; default one further persona on the session's model |
| `method` | `borda` (default) or `plurality`, for the table's order |
| `effort` | default `high`; a seat's own `effort` overrides it |

## After it returns

Report in this order:

1. **The winner**, in full, with how it was reached: both voters agreed, or decided by which tiebreaker. On a split, say so and say what the front-runners trade off; the `leader` is not a winner. With no winner because none was acceptable, report that with the voters' reasons.
2. **The table** (first choices, Borda points, out-flags) and which seats voted on which models, including any seat that returned nothing.
3. **The winner's worries,** from the voters who picked it.
4. **Where you disagree, if anywhere.** Never override the vote silently. If the user's own option lost, say so plainly; the user decides.

A vote measures agreement, not correctness. When the stakes are high and a check exists (tests, a benchmark, the user's own judgment on two finalists), run the check on the top two.

Why these numbers, and the study behind them: [references/evidence.md](references/evidence.md).
