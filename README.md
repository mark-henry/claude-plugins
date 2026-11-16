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
| `lab` | `/lab:experiment` | Standard checks for a single ML experiment (a fine-tune, an RL run, an LLM eval or judge, a skill test). Fourteen lines: read raw items, score the intended n, a scorer that fails a broken output and passes a good one, a baseline that reproduces, the independent unit, one primary metric and smallest effect written before scoring, pilot power, saturated items, test scored once, a run id on every number, no leakage, trivial-policy floors, data recomputed per arm, and a raised eyebrow at the design before the run. `prereg.py` stamps each run (a snapshot of the tree under `refs/lab/`, the command, config, models, data hashes) and refuses the label counted when a line fails; `check`, `parity`, `ledger` and `quote` hold the rest. A fresh agent signs off any number that leaves your hands. Assumes git and a tracker (MLflow, W&B, Inspect). |
| `decide` | `/decide:draftoff`, `/decide:docket` | Ways to reach a decision, with fresh agents or with you. `draftoff`: for a long or high-stakes document, three fresh agents draft the whole thing on different organizing ideas, a judge grafts the best parts onto one base, and a blind pick against a sealed plain draft says whether the process beat plain writing. `docket`: hold court over a backlog of decisions: one small, self-contained item at a time, with the background, the cost and a recommendation; the ruling is carried out, and the next item is chosen by judgment (ready before pending, unblocking and time-sensitive first, related items together), not by arrival order. Works for any kind of item. |
| `check` | `/check:eyebrow` | Can this be trusted? Before work starts on a plan, ask who has tried it and what happened: a fresh agent on the strongest model says what the people who know the area best would say, and a web search looks for the case against. |
| `unattended` | `/unattended:interview`, `/unattended:go`, `/unattended:arbiter` | Run work unattended and trust the result. interview: question the user until they have decided what they want, then freeze it as a written brief an unattended run can build against. go: carry a frozen brief to a checked result inside the approved cap, with proof of done and the user's decisions last. arbiter: keep the judge of done out of the worker's reach, with the arbiter-loop script on PATH. |
| `naming` | `/naming:pick` | Choose a name for something other people or code will use: state its job, list the siblings it must not be confused with, brainstorm a dozen candidates in different styles (including a concrete metaphor), test them against the classic rules (Martin, Kernighan and Pike, Evans, Feitelson, Arnaoudova), and recommend one with a long and a short form. |
| `amazon` | `/amazon:cart` | Read the Amazon Cart, Amazon Fresh Cart and Whole Foods Market Cart, flagging same-day items that ride a delivery window inside the normal cart. Reads run in a dedicated agent Chrome (`agent-chrome`), so there is no remote-debugging prompt. Adding is done by you: Amazon flags automated adds, and its old add-to-cart link is dead, so `amazon-cart open ASIN...` opens the product pages for you to click. |
| `evals` | `/evals:build-judge`, `/evals:spot-check`, `/evals:tune-prompt` | `build-judge`: build an LLM judge you can trust. The procedure is Hamel Husain's [evals-skills](https://github.com/hamelsmu/evals-skills) plugin (error analysis, judge prompt, validation by true-positive and true-negative rates on a held-out split, not raw agreement); this skill adds house rules it doesn't cover, such as one item per call, pairwise order bias, burned test sets and re-validation. `spot-check`: before an eval's aggregate is trusted, a subagent reads a stratified sample of 30–50 scored items (top, bottom, middle, disagreements) and flags scores that are too high, too low or broken, so the human only looks at what survives. `tune-prompt`: tune a new prompt-driven component (a router, a skill, an agent prompt) live, one real case at a time: show the input, seal a written prediction, run it, have the human rule pass or fail with a critique while the agent's prediction and its own verdict stay sealed until the ruling is in, and change the prompt only when two or three critiques share a cause. Graduates to `build-judge` at about 30 cases. |
| `upstream` | `/upstream:pr` | Send a pull request to a repo someone else owns. Before any commit is written, read the project's agent instructions (`CLAUDE.md`, `AGENTS.md` and their Copilot and Cursor cousins), `README.md`, `CONTRIBUTING.md`, PR template and CI workflows, and note the rules that apply, including any AI policy. Then check for duplicate issues and PRs, fork and branch from fresh upstream, keep the diff to one topic, match their commit format and DCO sign-off, run their checks, and show the user the drafted PR before it goes public. |

Claude also picks up each skill on its own when a request matches, so you rarely need to type the commands.

## How the skills are written

The `unattended`, `check`, `decide`, `lab` and `evals` plugins follow a few rules. They are here for anyone extending the pack.

- **A skill does not tell the model how to do its job.** On current models, text that says how to plan, split, verify or delegate measures at about zero for more tokens, and Anthropic's own guidance says to delete it ([Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5), [Claude Code best practices](https://code.claude.com/docs/en/best-practices)). A skill says what the model cannot know: the boundaries, the contract with the next stage, the user's own words, and the check that decides "done".
- **Encourage the agent's ambition and autonomy, without telling it how.** Inside the boundaries the work is the agent's, and the only nudge is toward doing more of it unasked.
- **The record is owed at any size; the effort scales with the stakes.** A small job still ends in a report with its checks behind it. A second look is for steps that are expensive or cannot be run twice.
- **Enforce with code where code can.** A rule a script can hold is held by the script (`arbiter-loop`, `prereg.py`), and the text stays true of what the script does and does not enforce.
- **Budgets on a subscription are in effective tokens:** input tokens, plus 1.25 times cache writes, 0.1 times cache reads and 5 times output tokens. That weighting follows list-price ratios, so one number covers a run across models. Metered spend is capped in dollars.

### Naming the model for a seat

Models change monthly, operators differ, and user preferences and budgets matter, so a skill never directly names a model. When a skill seats an agent, it always describes in poetry what that seat needs; the agent running the skill resolves this description from continuous capabilities space into the discrete model-and-effort-level space.

To write the poetry, list what the agent in that seat must be capable of. Then compress the list into a few words that name the capabilities the list turns on. 

For example:

- Rules on "done" for unattended work from the work itself; reads claims of success and planted persuasion without being moved; runs things before it believes them → "a model that will not be talked past"
- Reads a long scored item whole and notices where the score and the item disagree, dozens of times over; needs no rare knowledge → "a rigorous-enough, affordable model"
- Knows what the experts in a field would say about a plan, from memory, and will say the plan is unnecessary → "the most worldly model, wise enough to say don't"
- Plans from a draft brief and reports every gap it would have to guess at, where a stronger model would quietly fill them → "a model no stronger than the one that will build"
- Builds ordinary, well-specified things, pass after pass → "the cheapest model that follows a spec"
- Holds the shape of a long document whose structure is still open → "a model with taste that can hold a whole document's shape"
- Plays a persona for a whole interview without volunteering what it was told to withhold → "a model that stays in character and keeps a secret"
- Generates millions of rows of jsonl → "the fast rote-tokens model"

Write it fresh for each seat. The test: a reader should be able to guess the job from the phrase.

Never a product, vendor or version, and never a bare label ("the strong model", "tier 2") that says nothing about the job. 

**For operators.** The running agent picks among your models and effort levels. Steer it with a line in your own instructions, such as: "Opus is the daily driver model. A Fable review is required before spending more than $5. Sonnet is OK for uncomplicated implementation."

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
