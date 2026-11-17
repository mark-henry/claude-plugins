# Effective tokens, and what they cost in subscription quota

Dated 2026-11-15. The meter has changed without notice before; check a rate against a fresh reading before relying on it.

## The unit

An effective token is one token weighted by its price relative to an input token:

| Kind | Weight |
|---|---|
| input | 1 |
| cache write (5 minutes) | 1.25 |
| cache read | 0.1 |
| output | 5 |

`agent-tokens` (on PATH from this plugin) reports it as the `weighted` column, per agent and per model. It is exact for what it counts: each API reply's usage, once per message id. It does not weight by model: compare runs of one model directly, and scale by each model's price to compare across models (a top-tier model costs several times a mid-tier one per effective token).

Estimates, caps and shares handed to agents are all in this unit. A share handed in raw tokens is several times larger than it looks, because output and cache writes weigh more than 1.

## Why this weighting

The subscription shows only a percentage of a weekly limit. The vendor publishes no unit, no weights and no tokens per percent; its help pages say only that the model and the effort level matter and that some plans have a separate weekly limit for the top-tier model. Independent measurements agree on the shape (the API price ratios) and disagree on the exact numbers:

| Source | Cache read | Cache write | Output |
|---|---|---|---|
| These weights (API price ratios) | 0.1 | 1.25 | 5 |
| GitHub issues anthropics/claude-code#103376 and #106322 (Oct 2026): several users weight "by API price ratio" and find weeks with different cache mixes then line up | 0.1 | 1.25 (2 for a one-hour write) | 5 |
| A gateway operator's regression on real accounts' limit changes (wokey.ai/claude-usage-limits, fit dated 2026-09-28, R² 0.965) | "close to none" | "about the same as uncached input" | "roughly 4–7 times" |
| A user's fit on the top plan (zenn.dev, 2026-09-29) | 0.025 | 1.25 | 5 (8 before mid-September) |

So: output at 5 and cache write near 1 to 1.25 are well supported. Cache reads may count for less than 0.1, which makes these weights overstate a run that is mostly cache reads. `agent-tokens` does not separate one-hour cache writes. Across models the factor is not exactly the price ratio either (the gateway operator measures the general-use model at about 0.6 of the top tier per token).

The rate itself moves. In issue #103376 one user's allowance went from about 5.2 million effective tokens per 1% of the weekly meter to about 3.85 million within a month on the top plan; a user on the smallest plan saw about 0.85 million per 1% fall to about 0.29 million.

## Mapping to percent of quota

- Keep your own table: `${CLAUDE_PLUGIN_DATA}/exchange.md`, one row per run, with effective tokens by model and the meter before and after. A row is clean only if little else drew on the meter.
- One measured rate, for orientation only: about 5 million effective tokens per 1% of the weekly limit, on the top subscription plan, for agents on the general-use and mid-tier models, November 2026, from one fairly clean run.
- The meter is readable by program: Claude Code's status line JSON carries `rate_limits.seven_day.used_percentage` and `five_hour.used_percentage`.
- Quote a quota figure to the user only as a translation of the effective-token figure, with the date of the rate.
