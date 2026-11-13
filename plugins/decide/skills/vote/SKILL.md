---
name: vote
description: "Pick among discrete options by blind vote: independent proposers write options (or you supply them), duplicates are merged so votes don't split, and voters who each see a different order rank the pool; returns the plurality, Borda and Condorcet winners with margins, so a split vote shows up as a split. Use for \"/decide:vote\", \"vote on it\", \"put it to a vote\", \"which of these\", \"pick one of\", \"majority vote\", choosing a name, library, approach or answer from a short list, or when the options are already known and the question is which. Not for improving one proposal (decide:improve), and not for open design spaces where the options don't exist yet (decide:bakeoff)."
---

# Put it to a vote

Invoking this skill is the user's opt-in to running a Workflow (proposers + one pooling agent + voters). The script is `vote.js` in this directory. `scriptPath` refuses plugin paths, so copy the script to your scratchpad and run `Workflow({scriptPath: "<scratchpad>/vote.js", args: {...}})`.

**Vote or gauntlet?** A vote picks a point from a set. It works best when the answer is one of several discrete options and the errors of independent judges are mostly uncorrelated. `decide:improve` moves a single point. Each challenger amends or replaces the current version, which suits continuous spaces: polishing wording, tuning a design, or noticing that "actually there's a library for this". The two compose. Run a vote to pick the starting point, then run `decide:improve` on the winner with the voters' worries as its agenda and the beaten options as full text; its closing pick already puts the vote's winner up against every revision.

How it works:
1. **Propose.** Unless `options` are given, `proposers` agents each work alone and list their two or three best answers, best first, as genuinely different choices. Each starts its search from a different place (the practitioner's default, the simplest, existing tools, robustness, the skeptic's pick, cheapest to reverse, most ambitious). Asking each proposer for one option doesn't work: on a question with an obvious answer, every proposer writes it and nothing is left to vote on. Each option's `first_choice_of` (how many proposers ranked it first) is a self-consistency signal in its own right.
2. **Pool.** One agent merges proposals that are the same choice in different words, so near-duplicates don't split the vote. It never drops or judges an option, and code checks that: a candidate the merge lost is put back, and one counted twice is counted once.
3. **Vote.** `voters` agents each rank the whole pool by letter. Each sees a different rotation, reversed for every other voter, to spread position bias. Voters don't know who proposed what. They mark any option that breaks a hard constraint, and may say that none of the options is acceptable or that the question is wrongly framed.
4. **Tally.** In code, not by an agent: first-choice counts, Borda points and the Condorcet winner. An option that a majority marks as breaking a constraint can't win and is left out of every tally, so its votes pass to each voter's next choice. If a majority rules out every option, or says none is acceptable, there is no winner.

## Before launch

1. **The question** must have a discrete answer: "which library", "which name", "which of these three plans". If the honest answer is "a blend", the question is wrong. Narrow it, or use `decide:improve`. A question of fact is never put to a vote: if a test, lookup or computation can answer it, run that, and if the evidence is missing, check sources.
2. **Options or not.** Pass `options` when the set is known, such as the user's shortlist or the candidates from `naming:pick`. Include the current choice if there is one, so the incumbent can win. Leave them out to have the proposers generate the set; that is also how to find options nobody has listed. Supplied options skip the pool step, so merge near-identical ones yourself: two near-twins split the vote and hand the win to a worse third.
3. **Context for strangers.** The agents know nothing of this conversation. Give them facts, numbers with denominators and paths to open, and put hard limits in `constraints`. Leave out which option you favor.
4. **Size.** The defaults are 5 proposers and 5 voters. Use an odd number of voters. More voters only help when the votes are split; when the margin is wide, three voters were enough.

## Args

| arg | meaning |
|---|---|
| `question` | required |
| `options` | optional list of strings or `{label, option}`; skips the proposers |
| `goal`, `context`, `constraints`, `criteria` | `constraints` are hard limits (an option that breaks one is out); `criteria` is what to judge by |
| `proposers`, `voters` | default 5 each |
| `method` | `borda` (default; uses whole rankings) or `plurality` |
| `effort` | default `high` |
| `model`, `judge_model` | proposer model; the voter and pooling model (defaults to `model`) |

## After it returns

Report in this order:
1. **The winner**, in full, and its margin, e.g. "Borda 18 vs 11 of 20". Say whether plurality, Borda and Condorcet agree. When they agree with a wide margin, the result is strong. When they disagree, or the margin is a point or two, call it a split. With a split, the vote has not decided; say what the two front-runners trade off. If the result has no winner, the answer is "none of these": report that with the voters' reasons, not the top-ranked option.
2. **The table**: each option's first-choice count, Borda points, out-flags and, if proposers ran, how many proposed it.
3. **The winner's worries**, which come from the voters who picked it.
4. **Where you disagree, if anywhere.** Don't override the vote silently. If the user's own option lost, say so plainly; the user decides.

A vote measures agreement, not correctness. Voters from the same model share blind spots, so a confident wrong answer can win unanimously. When the stakes are high and a check exists (tests, a benchmark, the user's own judgment on two finalists), run the check on the top two instead of trusting the margin.

The study behind these instructions is in [references/evidence.md](references/evidence.md).
