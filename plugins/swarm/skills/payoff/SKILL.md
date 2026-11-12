---
name: payoff
description: "Measure whether agent spend is paying off: cost per accepted result for each kind of work, discard rate, review time, cost spread on the same task, and a matched half-budget comparison, ending in a scale / hold / build-a-better-checker call per kind of work. Reads the Results lines of swarm plans and fills gaps from ccusage and git/PR history, marked as estimates. Use for \"/swarm:payoff\", \"is this agent spend paying off\", \"where did the tokens go\", \"cost per PR\", \"should we scale this up\", or after a batch of swarm work finishes."
---

# Is the agent spend paying off?

Token counts say whether someone is using agents, not whether the agents are producing anything. Across about 12,000 developers at 200 companies in Q1 2026, the top decile used about 10x the median's tokens for about 2x the output, and token cost per merged PR ran from $0.28 to $89.32 across usage tiers [1]. Heavy use is not waste by itself: counting salary, Jellyfish later found cost per merged PR fell 26% in a year while AI spend rose 60x, with tokens about 2.5% of the cost [7]. Self-reports are not a measure either: developers in METR's early-2025 study took 19% longer with AI while estimating afterwards that it had sped them up by about 20%; METR's 2026 follow-up finds a probable speedup (−18%, 95% CI −38% to +9%) and still calls self-reported speedups unreliable [2]. So the measure is cost per accepted result, including people's time, broken down by kind of work, with a check against a smaller budget.

## Steps

1. **Collect the results.** Read the Results lines of each `swarm:go` plan in the period (`${CLAUDE_PLUGIN_DATA}/runs/*/plan.md`, or wherever the user keeps runs): one line per ruling, with piece, accepted / killed / redirected, cost and review minutes. Read the run log too (`${CLAUDE_PLUGIN_DATA}/runs.md`), one line per run written at close-out; where a run has none, append it yourself, not from a workflow script. Where lines are missing, reconstruct:
   - cost from session logs with ccusage (how much was spent) or ccwhy (where it went) [3];
   - acceptance from git or PR history (merged, reverted, closed unmerged).

   Mark every reconstructed number as an estimate. A field nobody recorded is unavailable, not zero: leave it out of the sums.
2. **Group by kind of work**, such as merged PR, kept experiment result, validated label set, confirmed finding, or research answer. Use the plan's checker types (machine check, judge, selector, agreement, summary) when nothing better fits. A method run's log line (a vote, a bakeoff, an attack) adds the route, the prediction and whether it hit, the control result and, later, the user's verdict; group these by route as well as kind.
3. **For each kind, compute:**
   - **cost per accepted result**, as API-equivalent dollars or quota percent: total cost over the accepted count;
   - **accepted / attempted**, counting agent runs only: a question the user settled with no agent run behind it stays out of the denominator;
   - **the share discarded or rewritten** after acceptance, counting reverts, follow-up fixes and results that did not replicate;
   - **human review time** per accepted result;
   - **the cost spread on one task type** (min, median, max). Runs on the same task varied by up to 30x in tokens on late-2025 models (typically about 2x between cheapest and costliest), and accuracy often peaks at intermediate spend and saturates beyond it [4], so a long tail is a target. Measure spend rather than asking agents to forecast it: their forecasts run low [4].
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

- **Token totals or leaderboards as the metric.** An employee-built Meta leaderboard of token use encouraged "tokenmaxxing" and came down two days after it was reported [5], and Amazon's engineering guidelines called usage metrics such as token consumption "deeply flawed" when disconnected from results [6]. Token totals are a diagnostic, not a score.
- **Counting acceptances without the later reverts and replication failures**, which flatters fast, sloppy work.
- **Mixing kinds of work in one ratio.** A cheap label set and an expensive merged refactor are not the same unit.

## Sources
1. Jellyfish research (Nicholas Arcolano), interviewed by WorkOS, Aug 2026: https://workos.com/blog/nicholas-arcolano-jellyfish-token-maxing-diminishing-returns
2. METR, Becker et al., early-2025 RCT: https://arxiv.org/abs/2507.09089; Feb 2026 update: https://metr.org/blog/2026-02-24-uplift-update/
3. SingYee, Apr 2026: https://dev.to/singyee/i-analyzed-187-claude-code-sessions-6744-worth-of-tokens-heres-where-they-actually-went-2ae5
4. Bai et al., Apr 2026: https://arxiv.org/abs/2604.22750
5. Fortune, Apr 2026: https://fortune.com/2026/04/09/meta-killed-employee-ai-token-dashboard/
6. Tom's Hardware, Oct 2026: https://www.tomshardware.com/tech-industry/artificial-intelligence/amazon-tells-engineers-to-stop-tokenmaxxing-to-look-productive-says-ai-will-be-central-to-software-development-but-usage-is-not-the-goal-new-guidelines-claim
7. Jellyfish, Oct 2026, via StartupHub: https://www.startuphub.ai/ai-news/market-research/2026/tokens-are-cheap-but-is-the-math-real
