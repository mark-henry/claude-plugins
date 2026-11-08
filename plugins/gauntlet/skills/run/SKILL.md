---
name: run
description: "Run a proposal (plan, design, fix, name, decision) through a gauntlet of fresh subagents, each asking \"is this the best way to do this?\" and either keeping it with a defense or handing on a better complete version. Default is one chain of two challengers; extra chains run in parallel and a final agent merges them. Returns the final version, what changed at each step, and residual doubts. Use for \"/gauntlet:run\", \"gauntlet\", \"is this the best way to do this?\", \"rebuttal\", \"challenge this\", \"pressure-test this\", \"poke holes in\", or \"run it past a couple of agents\", when a proposal is already in hand. Not for generating options from scratch: use diverge:design for wide design spaces and diverge:lite for five quick stances."
---

# Run the gauntlet

Invoking this skill is the user's opt-in to running a Workflow (depth × width agents, plus one merge agent when width > 1). The script is `gauntlet.js` in this directory. `scriptPath` refuses plugin paths, so copy the script to your scratchpad and run `Workflow({scriptPath: "<scratchpad>/gauntlet.js", args: {...}})`.

How it works: each chain starts from the proposal. Every challenger gets the current best version, the goal and the context, plus a list of what earlier challengers changed (so it doesn't undo work without a reason). Each challenger considers at least one materially different alternative. It returns `keep`, `amend` or `replace`, with the reasons, a list of changes, a complete standalone version (not a diff) and its residual doubt. That version goes to the next challenger. When width > 1, the chains run independently in parallel and a merge agent picks or combines their final versions.

## Before launch

1. **The proposal.** If the user proposed something, pass it verbatim. If not, write your own best proposal in full, as something to beat rather than a draft to polish.
2. **Context for strangers.** The challengers know nothing of this conversation. Give them facts: the goal, the constraints, numbers with denominators, file paths to open, siblings or alternatives that already exist, and anything already tried. Leave out the reasons you like the proposal; they will find its strengths or fail to.
3. **Shape.** Default `depth: 2, width: 1`. Use more width when the proposal could fail in several different ways. Give each chain a lens (e.g. `["correctness", "simplicity", "cost"]`) so the chains disagree usefully. Use more depth only if a chain is still changing at its last step.

## Args

| arg | meaning |
|---|---|
| `proposal` | required: the thing to challenge, in full |
| `goal`, `context`, `constraints` | strongly recommended; `constraints` are hard limits, not preferences |
| `depth` | challengers per chain (default 2) |
| `width` | parallel chains (default 1); >1 adds a merge agent at xhigh effort |
| `lenses` | optional, one per chain |
| `effort` | challenger effort (default `high`) |
| `model`, `judge_model` | optional overrides for challengers and for the merge agent |

## After it returns

Report back in this order:
1. **The final version**, or the merged recommendation when width > 1.
2. **The chain's path**, e.g. `replace → amend`, with one line per step on what changed and why.
3. **The last residual doubt.**
4. **Where you disagree with the result, if anywhere.** Never override it silently.

If the original was the user's and the gauntlet replaced it, say so plainly; the user decides. A chain of all `keep` verdicts is a result too: report it as "survived two challenges", not as nothing happening.
