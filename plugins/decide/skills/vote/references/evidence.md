# Evidence for decide:vote

The study finding and source list moved out of the body of `decide:vote`, verbatim. Each passage sits under a line naming the instruction it backs. Product and model names are as they stood when the passage was written.

## Sources
1. Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet", ICLR 2024, Sec. 4 and Table 7: https://arxiv.org/abs/2310.01798

## Vote or gauntlet?

Backs: a vote works best when the answer is one of several discrete options and the errors of independent judges are mostly uncorrelated.

> At matched budget, sampling independently and taking the majority beat multi-agent debate (88.2% vs 83.0% on GSM8K with gpt-3.5 at 9 responses each; the gains credited to debate came from aggregation [1]).

## Backs: "Two voters… if they differ, tiebreakers vote one at a time" and "from different model families"

Arithmetic, not a study. If each voter is independently right with probability p, a majority of n is right with probability: p = 0.7 gives 70% (1), 78% (3), 84% (5), 87% (7); p = 0.9 gives 90%, 97%, 99%, 99.7%. Asking two and adding a third only when they differ has exactly the accuracy of best-of-three, for 2.4 voters on average at p = 0.7 and 2.2 at p = 0.9. These hold for a two-way choice between independent voters. Voters whose errors correlate at ρ are worth about n / (1 + (n − 1)ρ) independent ones: five at ρ = 0.5 are worth about 1.7. Hence diversity of model before headcount.
