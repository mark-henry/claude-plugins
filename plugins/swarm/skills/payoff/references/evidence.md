# Evidence for swarm:payoff

Study findings, reported incidents and the numbered source list moved out of the body of `swarm:payoff`, verbatim. Each passage sits under a line naming the instruction it backs; bracketed numbers point into the source list. Product and model names are as they stood when the passage was written.

## Sources
1. Jellyfish research (Nicholas Arcolano), interviewed by WorkOS, Aug 2026: https://workos.com/blog/nicholas-arcolano-jellyfish-token-maxing-diminishing-returns
2. METR, Becker et al., early-2025 RCT: https://arxiv.org/abs/2507.09089; Feb 2026 update: https://metr.org/blog/2026-02-24-uplift-update/
3. SingYee, Apr 2026: https://dev.to/singyee/i-analyzed-187-claude-code-sessions-6744-worth-of-tokens-heres-where-they-actually-went-2ae5
4. Bai et al., Apr 2026: https://arxiv.org/abs/2604.22750
5. Fortune, Apr 2026: https://fortune.com/2026/04/09/meta-killed-employee-ai-token-dashboard/
6. Tom's Hardware, Oct 2026: https://www.tomshardware.com/tech-industry/artificial-intelligence/amazon-tells-engineers-to-stop-tokenmaxxing-to-look-productive-says-ai-will-be-central-to-software-development-but-usage-is-not-the-goal-new-guidelines-claim
7. Jellyfish, Oct 2026, via StartupHub: https://www.startuphub.ai/ai-news/market-research/2026/tokens-are-cheap-but-is-the-math-real

## Opening

Backs: token counts say whether someone is using agents, not whether the agents are producing anything.

> Across about 12,000 developers at 200 companies in Q1 2026, the top decile used about 10x the median's tokens for about 2x the output, and token cost per merged PR ran from $0.28 to $89.32 across usage tiers [1].

Backs: heavy use is not waste by itself.

> Heavy use is not waste by itself: counting salary, Jellyfish later found cost per merged PR fell 26% in a year while AI spend rose 60x, with tokens about 2.5% of the cost [7].

Backs: self-reports are not a measure either.

> Self-reports are not a measure either: developers in METR's early-2025 study took 19% longer with AI while estimating afterwards that it had sped them up by about 20%; METR's 2026 follow-up finds a probable speedup (−18%, 95% CI −38% to +9%) and still calls self-reported speedups unreliable [2].

## Steps

Backs: step 1, reconstruct cost from session logs with ccusage or ccwhy.

> cost from session logs with ccusage (how much was spent) or ccwhy (where it went) [3];

Backs: step 3, compute the cost spread on one task type; a long tail is a target.

> Runs on the same task varied by up to 30x in tokens on late-2025 models (typically about 2x between cheapest and costliest), and accuracy often peaks at intermediate spend and saturates beyond it [4], so a long tail is a target.

Backs: step 3, measure spend rather than asking agents to forecast it.

> Measure spend rather than asking agents to forecast it: their forecasts run low [4].

## Pitfalls

Backs: token totals are a diagnostic, not a score.

> An employee-built Meta leaderboard of token use encouraged "tokenmaxxing" and came down two days after it was reported [5], and Amazon's engineering guidelines called usage metrics such as token consumption "deeply flawed" when disconnected from results [6].
