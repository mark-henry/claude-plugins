---
name: payoff
description: "Measure whether agent spend is paying off: cost per accepted result for each kind of work, discard rate, review time, cost spread on the same task, and a matched half-budget comparison, ending in a scale / hold / build-a-better-checker call per kind of work. Reads the Results lines of swarm plans and fills gaps from ccusage and git/PR history, marked as estimates. Use for \"/swarm:payoff\", \"is this agent spend paying off\", \"where did the tokens go\", \"cost per PR\", \"should we scale this up\", or after a batch of swarm work finishes."
---

# Is the agent spend paying off?

Token counts say whether someone is using agents, not whether the agents are producing anything. Heavy use is not waste by itself. Self-reports are not a measure either. So the measure is cost per accepted result, including people's time, broken down by kind of work, with a check against a smaller budget.

## Steps

1. **Collect the results.** Read the Results lines of each `swarm:go` plan in the period (`${CLAUDE_PLUGIN_DATA}/runs/*/plan.md`, or wherever the user keeps runs): one line per ruling, with piece, accepted / killed / redirected, cost and review minutes. Read the run log too (`${CLAUDE_PLUGIN_DATA}/runs.md`), one line per run written at close-out; where a run has none, append it yourself, not from a workflow script. Where lines are missing, reconstruct:
   - cost from session logs with ccusage (how much was spent) or ccwhy (where it went);
   - acceptance from git or PR history (merged, reverted, closed unmerged).

   Mark every reconstructed number as an estimate. A field nobody recorded is unavailable, not zero: leave it out of the sums.
2. **Group by kind of work**, such as merged PR, kept experiment result, validated label set, confirmed finding, or research answer. Use the plan's checker types (machine check, judge, selector, agreement, summary) when nothing better fits. A method run's log line (a vote, a bakeoff, an attack) adds the route, the prediction and whether it hit, the control result and, later, the user's verdict; group these by route as well as kind.
3. **For each kind, compute:**
   - **cost per accepted result**, as API-equivalent dollars or quota percent: total cost over the accepted count;
   - **accepted / attempted**, counting agent runs only: a question the user settled with no agent run behind it stays out of the denominator;
   - **the share discarded or rewritten** after acceptance, counting reverts, follow-up fixes and results that did not replicate;
   - **human review time** per accepted result;
   - **the cost spread on one task type** (min, median, max). A long tail is a target. Measure spend rather than asking agents to forecast it: their forecasts run low.
4. **Where a comparison is cheap, run a matched half-budget test.** Give a comparable class of tasks half the budget (fewer samples, fewer agents, a smaller model) and compare cost per accepted result. Report it with its n; one pair of runs proves nothing. A multi-agent method (debate, panel, chain, best-of-N, a new workflow) likewise meets the simple baseline once at matched budget, and again when the model changes: independent samples with a majority vote, independent drafts with a blind judge's pick for free text, or the bare model.
5. **Make one call per kind of work:**
   - **scale:** cost per accepted result is flat or falling as spend grows;
   - **hold:** acceptances are flat while cost grows, so the work is past the knee;
   - **build a better checker:** the discard rate or review time is high, so the checker, not the agent count, is the bottleneck (`swarm:go`'s checker table; `evals:judge` for judges).
6. **Report** with the template below. Lead with the calls, then the table. If any input is an estimate, say so in the line under the table.

## Output

```markdown
## Swarm review: <period>
Calls: <kind → scale / hold / build a better checker>, …

| Kind of work | Accepted / attempted | Cost per accepted | Discarded or rewritten | Review time per accepted | Cost spread (min / median / max) | Call |
|---|---|---|---|---|---|---|
| <kind> | <n / N> | <$ or quota %> | <share> | <minutes> | <…> | <call> |

Half-budget test: <kind, n, result / none run>
Baseline test: <method, n, result / none run>
Estimates: <which numbers, from what / none>
```

## Pitfalls

- **Token totals or leaderboards as the metric.** Token totals are a diagnostic, not a score.
- **Counting acceptances without the later reverts and replication failures**, which flatters fast, sloppy work.
- **Mixing kinds of work in one ratio.** A cheap label set and an expensive merged refactor are not the same unit.

The studies and sources behind these instructions are in [references/evidence.md](references/evidence.md).
