# claude-plugins

Plugins that encourage the models to spend more tokens and work more independently, plus misc utilities

## Design principles

- **Encourage the agent's ambition and autonomy.** I want to spend more tokens. Inside the boundaries the work is the agent's, and the only nudge is toward doing more of it unasked.
- **A skill does not tell the model how to do its job within the parameters set.** On current models, the science and Anthropic's guidance and my own tests show that telling the model how to do its job is not as good as letting RL do its thing ([Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5), [Claude Code best practices](https://code.claude.com/docs/en/best-practices)). A skill says what the model cannot know: the boundaries, the contract with the next stage, the user's own words, and the check that decides "done". The model is allowed to scale effort to the stakes. 
- **Enforce with code where code can.** A scriptable rule is scripted
- **Budgets on a subscription are in effective tokens:** meaningful budgeting by using Anthropic's unpublished quota math

## The skill pack

| Plugin | Command | What it does |
|---|---|---|
| `unattended` | `/unattended:interview`, `/unattended:go`, `/unattended:arbiter` | Run work unattended and trust the result. `interview`: question the user until they have decided what they want, then freeze it as a written brief an unattended run can build against. `go`: carry a frozen brief to a checked result inside the approved cap, with proof of done and the user's decisions last. `arbiter`: keep the judge of done out of the worker's reach, featuring the `arbiter-loop` script. |
| `check` | `/check:eyebrow` | Before giving you what you ask, have a skeptic arch an eyebrow. Draws wisdom from the weights and from the internet and notices the skulls. |
| `decide` | `/decide:draftoff`, `/decide:docket` | Ways to reach a decision, with fresh agents or with you. `draftoff`: for a long or high-stakes document, three fresh agents draft the whole thing on different organizing ideas, a judge grafts the best parts onto one base, and a blind pick against a sealed plain draft says whether the process beat plain writing. `docket`: hold court over a backlog of decisions: one small, self-contained item at a time, with the background, the cost and a recommendation; the ruling is carried out, and the next item is chosen by judgment (ready before pending, unblocking and time-sensitive first, related items together), not by arrival order. Works for any kind of item. |
| `lab` | `/lab:experiment` | Standard checks for a single ML experiment (a fine-tune, an RL run, an LLM eval or judge, a skill test). Fourteen lines: read raw items, score the intended n, a scorer that fails a broken output and passes a good one, a baseline that reproduces, the independent unit, one primary metric and smallest effect written before scoring, pilot power, saturated items, test scored once, a run id on every number, no leakage, trivial-policy floors, data recomputed per arm, and a raised eyebrow at the design before the run. `prereg.py` stamps each run (a snapshot of the tree under `refs/lab/`, the command, config, models, data hashes) and refuses the label counted when a line fails; `check`, `parity`, `ledger` and `quote` hold the rest. A fresh agent signs off any number that leaves your hands. Assumes git and a tracker (MLflow, W&B, Inspect). |
| `evals` | `/evals:build-judge`, `/evals:spot-check`, `/evals:tune-prompt` | `build-judge`: build an LLM judge you can trust. Under the hood, it's just Hamel Husain's [evals-skills](https://github.com/hamelsmu/evals-skills) plugin plus some house rules. `spot-check`: before an eval's aggregate is trusted, actually look at its outputs. `tune-prompt`: tune a new prompt-driven component (a router, a skill, an agent prompt) live, test-driving one real case at a time. Graduates to `build-judge` at about 30 cases. |

## Utilities

| Plugin | Command | What it does |
|---|---|---|
| `video` | `/video:clip` | Download and clip videos with yt-dlp and ffmpeg, including clipping a window from a live stream. Adds `live-clip`. |
| `flights` | `/flights:calendar` | Scrape the Google Flights date-picker price calendar (cheapest fare per day across months) through the browser-use MCP. Adds `flights-tfs` and `flights-roundtrip-tfs` URL builders. |
| `gordian` | `/gordian:cut` | Step back from a codebase that has grown by many small edits and find the one simplification that removes the most branches. |
| `figure` | `/figure:make` | Turn a result into a figure that stands alone: the claim as the title, a caption that qualifies it, then the chart or table that proves it. |
| `naming` | `/naming:pick` | AIs are so bad at naming things sometimes. |
| `upstream` | `/upstream:pr` | Send a pull request to a repo someone else owns. Follows some simple rules to avoid embarrassment. |
| `quota` | `/quota:check` | This is specific to [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI), but it allows you to check remaining quota and make it visible to agents. |

Writing or changing a skill here: see [CONTRIBUTING.md](CONTRIBUTING.md).

MIT licensed.
