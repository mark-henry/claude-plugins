# claude-plugins

Small [Claude Code](https://claude.com/claude-code) plugins I use every day, published as a plugin marketplace. Each plugin installs on its own, so take only what you need.

```
/plugin marketplace add mark-henry/claude-plugins
/plugin install video@mark-henry
```

| Plugin | Command | What it does |
|---|---|---|
| `quota` | `/quota:check` | Weekly quota left on Claude and ChatGPT subscriptions behind [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI), against an even-spend target. Rebalances weights across Claude accounts so quota that's about to reset gets used, and a protected main account doesn't run out. Adds a `subquota` command and a SessionStart report. |
| `video` | `/video:clip` | Download and clip videos with yt-dlp and ffmpeg, including clipping a past window ("40 to 30 minutes ago") from a YouTube stream that is still live. Adds `live-clip`. |
| `flights` | `/flights:calendar` | Scrape the Google Flights date-picker price calendar (cheapest fare per day across months) through the browser-use MCP. Adds `flights-tfs` and `flights-roundtrip-tfs` URL builders. |
| `sleep` | `/sleep:last-night` | Infer last night's bedtime and wake time from the Mac's lid log, cross-checked against Chrome history. `lidsleep --json` gives the times to scripts that record them, for example in a daily note. macOS only. |
| `gordian` | `/gordian:cut` | Step back from a codebase that has grown by many small edits and find the one simplification that removes the most branches. |
| `figure` | `/figure:make` | Turn a result into a figure that stands alone: the claim as the title, a caption that qualifies it, then the chart or table that proves it. |
| `lab` | `/lab:experiment` | Standard checks for a single ML experiment (a fine-tune, an RL run, an LLM eval or judge, a skill test). Fourteen lines: read raw items, score the intended n, a scorer that fails a broken output and passes a good one, a baseline that reproduces, the independent unit, one primary metric and smallest effect written before scoring, pilot power, saturated items, test scored once, a run id on every number, no leakage, trivial-policy floors, and data recomputed per arm. `prereg.py` stamps each run (a snapshot of the tree under `refs/lab/`, the command, config, models, data hashes) and refuses the label counted when a line fails; `check`, `parity`, `ledger` and `quote` hold the rest. A fresh agent signs off any number that leaves your hands. Assumes git and a tracker (MLflow, W&B, Inspect). |
| `decide` | `/decide:draftoff`, `/decide:docket` | Ways to reach a decision, with fresh agents or with you. `draftoff`: for a long or high-stakes document, three fresh agents draft the whole thing on different organizing ideas, a judge grafts the best parts onto one base, and a blind pick against a sealed plain draft says whether the process beat plain writing. `docket`: hold court over a backlog of decisions: one small, self-contained item at a time, with the background, the cost and a recommendation; the ruling is carried out, and the next item is chosen by judgment (ready before pending, unblocking and time-sensitive first, related items together), not by arrival order. Works for any kind of item. |
| `check` | `/check:attack`, `/check:eyebrow` | Can this be trusted? A fresh agent that has not seen your reasoning finds what is wrong with a plan, a brief or finished work. One or two blind readers run what can be run and paste the evidence under each finding; you label every finding fixed, declined, refuted or for the user. `eyebrow`: before work starts on a plan, ask who has tried it and what happened; a fresh agent on the strongest model says what the people who know the area best would say, and a web search looks for the case against. |
| `unattended` | `/unattended:interview`, `/unattended:go`, `/unattended:arbiter` | Run work unattended and trust the result. interview: question the user until they have decided what they want, then freeze it as a written brief an unattended run can build against. go: carry a frozen brief to a checked result inside the approved cap, with proof of done and the user's decisions last. arbiter: keep the judge of done out of the worker's reach, with the arbiter-loop script on PATH. |
| `naming` | `/naming:pick` | Choose a name for something other people or code will use: state its job, list the siblings it must not be confused with, brainstorm a dozen candidates in different styles (including a concrete metaphor), test them against the classic rules (Martin, Kernighan and Pike, Evans, Feitelson, Arnaoudova), and recommend one with a long and a short form. |
| `amazon` | `/amazon:cart` | Read the Amazon Cart, Amazon Fresh Cart and Whole Foods Market Cart, flagging same-day items that ride a delivery window inside the normal cart. Reads run in a dedicated agent Chrome (`agent-chrome`), so there is no remote-debugging prompt. Adding is done by you: Amazon flags automated adds, and its old add-to-cart link is dead, so `amazon-cart open ASIN...` opens the product pages for you to click. |
| `evals` | `/evals:build-judge`, `/evals:spot-check`, `/evals:tune-prompt` | `build-judge`: build an LLM judge you can trust. The procedure is Hamel Husain's [evals-skills](https://github.com/hamelsmu/evals-skills) plugin (error analysis, judge prompt, validation by true-positive and true-negative rates on a held-out split, not raw agreement); this skill adds house rules it doesn't cover, such as one item per call, pairwise order bias, burned test sets and re-validation. `spot-check`: before an eval's aggregate is trusted, a subagent reads a stratified sample of 30–50 scored items (top, bottom, middle, disagreements) and flags scores that are too high, too low or broken, so the human only looks at what survives. `tune-prompt`: tune a new prompt-driven component (a router, a skill, an agent prompt) live, one real case at a time: show the input, seal a written prediction, run it, have the human rule pass or fail with a critique while the agent's prediction and its own verdict stay sealed until the ruling is in, and change the prompt only when two or three critiques share a cause. Graduates to `build-judge` at about 30 cases. |
| `upstream` | `/upstream:pr` | Send a pull request to a repo someone else owns. Before any commit is written, read the project's agent instructions (`CLAUDE.md`, `AGENTS.md` and their Copilot and Cursor cousins), `README.md`, `CONTRIBUTING.md`, PR template and CI workflows, and note the rules that apply, including any AI policy. Then check for duplicate issues and PRs, fork and branch from fresh upstream, keep the diff to one topic, match their commit format and DCO sign-off, run their checks, and show the user the drafted PR before it goes public. |

Claude also picks up each skill on its own when a request matches, so you rarely need to type the commands.

## Setup notes

**quota.** Requires CLIProxyAPI with its management API enabled, plus `jq` and `curl`. Settings live in `~/.config/quota.env`; the defaults are at the top of `plugins/quota/bin/subquota`. For example:

```bash
QUOTA_PROTECTED_EMAIL=me@example.com   # main account: keep a 15% reserve, never route it dry
```

On macOS, `subquota --install-launchd` rebalances every 15 minutes in the background.

**flights.** Needs the browser-use plugin and a running Chrome.

**amazon.** Needs the browser-use plugin (for `browser-harness`) and Google Chrome. Run `agent-chrome --show` once and sign in to Amazon in that window; it keeps its own profile at `~/.chrome-agent`. macOS only.

## Developing

Clone the repo and add the clone as a local marketplace:

```
git clone https://github.com/mark-henry/claude-plugins ~/claude-plugins
claude plugin marketplace add ~/claude-plugins
claude plugin install quota@mark-henry
```

Installs are copied into Claude Code's plugin cache and versioned by commit, so after editing, commit and then run `claude plugin marketplace update mark-henry && claude plugin update quota@mark-henry`. To try uncommitted edits, start a session with `claude --plugin-dir ~/claude-plugins/plugins/quota`.

MIT licensed.
