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
| `lab` | `/lab:experiment`, `/lab:supervisor` | `experiment`: the one guideline for a single ML experiment (a fine-tune, an RL run, an LLM eval or judge). An order of events, then thirteen rules, each followed by how to meet it and its traps: arms differ in one recorded thing, prediction and denominator before results, controls, a noise floor that spans the claim, leakage and held-out discipline, a validated instrument, the freeze, one script-written record and one commit per run. It carries the preregistration record and its tool (`prereg.py`: a prediction per arm and metric, the commit stamped, a parity check, then predicted against observed), and a sign-off where a fresh agent rules on the design before launch and on the number before it is quoted, against `checks.md`. `supervisor`: the door to that sign-off. |
| `decide` | `/decide:vote`, `/decide:improve`, `/decide:bakeoff`, `/decide:docket` | Ways to reach a decision, with fresh agents or with you. `improve`: run a proposal you or Claude already have (a plan, design, fix, name or decision) through a chain of fresh subagents. Each asks "is there a better way to do this?" and either keeps it with a defense or hands on a better complete version. The default is one chain of two challengers; extra chains run in parallel, each optionally through its own lens. Blind pickers then rank the original and every version, so "the challengers made it worse" is a possible result. A Workflow under the hood. It named itself: the user's proposal `design:rebuttal` went in, and `decide:improve` came out. `vote` is for picking among discrete options rather than improving one: independent proposers (or a given list), duplicates merged, blind voters who each see a different order, and a plurality, Borda and Condorcet tally with margins, so a split shows as a split. Vote to pick a starting point, then run the gauntlet on the winner. `bakeoff`: adversarial design as a multi-agent Workflow: independent brainstormers each take a stance (open, outside the obvious component, adversary, skeptic), a selector picks maximally distinct solution families, each is prototyped, red-teamed and repaired in its own sandbox, and a judge recommends. It starts by locking the brief with `swarm:brief`; most of the skill is guidance on writing the brief without anchoring the brainstorm. `docket`: hold court over a backlog of decisions: one small, self-contained item at a time, with the background, the cost and a recommendation; the ruling is carried out, and the next item is chosen by judgment (ready before pending, unblocking and time-sensitive first, related items together), not by arrival order. Works for any kind of item. |
| `check` | `/check:attack`, `/check:claims` | Two ways to ask "can this be trusted?". `attack`: a fresh agent that has not seen your reasoning finds what is wrong with a plan, a brief or finished work. It returns findings with quoted evidence and changes nothing; a second fresh agent checks any finding that would change a decision; the whole exchange is kept as a file. `claims`: fresh agents verify what a report, draft or hand-back asserts before it travels: that "done" and "passing" are true of the actual artifact, that each cited source says what it is cited for, and that a synthesis covers what its sources hold. |
| `swarm` | `/swarm:brief`, `/swarm:go`, `/swarm:loop`, `/swarm:payoff` | Run large agent jobs with little supervision. `brief`: an interview that freezes a goal before costly work: it attacks every vague term, missing denominator and gameable bar, looks for what makes the work unnecessary or smaller, gets the budget cap and the permissions the run will need while the user is still present, and writes a `## Frozen brief` that other skills consume. `go`: carries a frozen brief to a finished, checked result with nobody watching. It holds the boundaries of unattended work (the cap, other people and the irreversible, measurement, evidence) and the license to act inside them without checking in. Each piece of work is planned around who or what will say it is right, which sets its pattern (unattended loop, bulk judge calls, best-of-N, blind vote, research fan-out, or a question for the user), its width, its stop rule and what counts as accepted. The plan is attacked by a fresh agent before anything is spent, a pilot is read before scale, and the report ends with the decisions that wait for the user. `loop`: an unattended Ralph-style loop gated by a check the agent can't touch; the supervisor takes a baseline, runs the check itself after every pass, keeps its logs and held-out results outside the agent's tree, and stops on done, a pass cap, a stall or a STOP file. `payoff`: cost per accepted result for each kind of work, ending in a scale, hold or build-a-better-checker call. Adds `swarm-loop`. |
| `naming` | `/naming:pick` | Choose a name for something other people or code will use: state its job, list the siblings it must not be confused with, brainstorm a dozen candidates in different styles (including a concrete metaphor), test them against the classic rules (Martin, Kernighan and Pike, Evans, Feitelson, Arnaoudova), and recommend one with a long and a short form. |
| `amazon` | `/amazon:cart` | Read the Amazon Cart, Amazon Fresh Cart and Whole Foods Market Cart, flagging same-day items that ride a delivery window inside the normal cart. Reads run in a dedicated agent Chrome (`agent-chrome`), so there is no remote-debugging prompt. Adding is done by you: Amazon flags automated adds, and its old add-to-cart link is dead, so `amazon-cart open ASIN...` opens the product pages for you to click. |
| `evals` | `/evals:judge`, `/evals:audit`, `/evals:shadow` | `judge`: build an LLM judge you can trust. The procedure is Hamel Husain's [evals-skills](https://github.com/hamelsmu/evals-skills) plugin (error analysis, judge prompt, validation by true-positive and true-negative rates on a held-out split, not raw agreement); this skill adds house rules it doesn't cover, such as one item per call, pairwise order bias, burned test sets and re-validation. `audit`: before an eval's aggregate is trusted, a subagent reads a stratified sample of 30–50 scored items (top, bottom, middle, disagreements) and flags scores that are too high, too low or broken, so the human only looks at what survives. `shadow`: tune a new prompt-driven component (a router, a skill, an agent prompt) live, one real case at a time: show the input, seal a written prediction, run it, have the human rule pass or fail with a critique while the agent's prediction and its own verdict stay sealed until the ruling is in, and change the prompt only when two or three critiques share a cause. Graduates to `judge` at about 30 cases. |
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
