---
name: auto
description: "Hand a question or proposal to the right challenge pattern automatically: a selector agent routes it to a blind vote (discrete picks), a gauntlet (improving one proposal), a vote then a gauntlet (pick a starting point, then refine it), a gauntlet then a vote (parallel challenge chains, then a blind vote that includes the original), or none (a check or lookup beats opinion), then runs it. Logs each routing decision so the selector prompt can be refined. Use for \"/decide:auto\", \"challenge or vote, whichever fits\", \"get the best answer to this with agents\", \"settle this\", or when it's unclear whether decide:improve or decide:vote fits."
---

# Route to vote, gauntlet or both

Invoking this skill is the user's opt-in to running a Workflow: one selector agent, then the chosen pattern, at up to about 2–3x the cost of `decide:improve` alone when the route is composed.

## Run it

1. Copy three scripts to your scratchpad: `auto.js` from this directory, `../vote/vote.js` and `../improve/gauntlet.js`. `scriptPath` refuses plugin paths, and `auto.js` runs the other two as child workflows.
2. Build the args. The rules are the same as for the sibling skills: pass the user's proposal verbatim, write context for strangers, put hard limits in `constraints`, and leave out which answer you favor.
3. Run `Workflow({scriptPath: "<scratchpad>/auto.js", args: {..., scripts: {vote: "<scratchpad>/vote.js", gauntlet: "<scratchpad>/gauntlet.js"}}})`.

| arg | meaning |
|---|---|
| `question` and/or `proposal` | at least one; `proposal` is something to improve, `question` is what is being decided |
| `options` | optional discrete options (strings or `{label, option}`) |
| `goal`, `context`, `constraints`, `criteria` | as in `decide:improve` and `decide:vote` |
| `route` | optional override: `vote`, `gauntlet`, `vote_then_gauntlet`, `gauntlet_then_vote`, `none` (skips the selector) |
| `scripts` | required: `{vote, gauntlet}` scratchpad paths |
| `depth`, `width`, `lenses`, `proposers`, `voters`, `effort`, `model`, `judge_model` | passed through to the child patterns |

## The routes

| route | when | what runs |
|---|---|---|
| `none` | a test, benchmark, lookup or calculation answers it better than opinion | nothing; returns what to do instead |
| `vote` | the answer is a pick from a discrete set | `decide:vote` |
| `gauntlet` | one proposal in hand; improve it | `decide:improve`, one chain of two by default |
| `vote_then_gauntlet` | no proposal; the answer is a built thing (design, plan, approach) | a vote among independent candidates picks the starting point, then a gauntlet refines the winner, told what it beat and what voters worried about |
| `gauntlet_then_vote` | a proposal that could fail in several distinct ways, or whose premise is in doubt | 2–4 parallel chains through different lenses, then a blind vote among their versions and the original, so "the challengers made it worse" is a possible result |

Independent proposers find basins and a relay climbs within one, so the composed routes put independence first when the basin is unknown, and a vote last when the climb might have gone wrong.

## Report back

1. **The route and why**, in one line. Say if you would have routed it differently.
2. **The answer**, in full.
3. Then the details of whichever pattern ran, as the sibling skills report them:
   - for a vote: the margin, whether the methods agree, and the winner's worries;
   - for a gauntlet: the chain's path and its last residual doubt.

   For `gauntlet_then_vote`, say whether the original won (`original_won`). If it did, the challenges didn't beat it, and that is a result in itself.

## Log the routing decision

Tuning the selector is `evals:shadow` work: predict the route before a run, then rule on it afterwards. After reporting, append one JSON line in the `evals:shadow` format to `${CLAUDE_PLUGIN_DATA}/auto-log.jsonl` (this plugin's data folder, which survives updates; create it if needed). Include the date, a one-line summary of the request (no secrets or private text), the route, the selector's `why`, whether it was overridden, and a one-line outcome. If the user later says the route was wrong, or a different pattern would have done better, append a line with `"verdict": "misrouted"` and their reason.

To refine the selector: read the log, collect the misrouted lines, and edit the `SELECTOR` constant at the top of `auto.js`. Don't edit it from a single case; wait for a pattern of two or three.
