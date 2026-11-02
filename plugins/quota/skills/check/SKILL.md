---
name: check
description: "Quota left on Claude and ChatGPT subscriptions behind CLIProxyAPI vs an even-spend target, plus Claude account rebalancing. Use before big fan-outs or bulk LLM jobs, when picking a model family or account, or when asked about quota."
---

Run `subquota` (~0.1s, on PATH from this plugin; named so it doesn't collide with macOS's `/usr/bin/quota`). `subquota --dry-run` shows the Claude weights a rebalance would set; `subquota --rebalance` sets them. A SessionStart hook runs `subquota --quiet`, so the report is usually already in context.

Reading it: `97% vs 83% (+14)` = weekly % left vs the % left if spent evenly, and the slack (negative = over pace). Numbers are the account-wide rate-limit headers as of the last proxied request (`seen`). Big slack near a reset will be lost: lean on that account or family. Over pace on GPT: prefer Claude workers, and vice versa.

Rebalancing: `subquota --install-launchd` runs `--rebalance` every 15 min via CLIProxyAPI's `PATCH /v0/management/auth-files/fields`, logging changes to `~/Library/Logs/quota-rebalance.log`. With that installed, don't hand-edit weights; change the settings in `~/.config/quota.env` instead (defaults are at the top of the script). During a heavy fan-out, run `subquota --rebalance` yourself. Policy: weight ∝ headroom ÷ hours to reset, floor 10, 0 with no headroom. Headroom is an account's remaining quota, except that `QUOTA_PROTECTED_EMAIL` (the main account that must not run out) keeps back max(15%, its target). If no account has headroom, the protected one takes everything. Weights are session-affine, so changes only steer new sessions.
