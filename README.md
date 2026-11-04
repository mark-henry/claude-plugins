# claude-tools

Small [Claude Code](https://claude.com/claude-code) plugins I use every day, published as a plugin marketplace. Each plugin installs on its own, so take only what you need.

```
/plugin marketplace add mark-henry/claude-tools
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
| `naming` | `/naming:pick` | Choose a name for something other people or code will use: state its job, list the siblings it must not be confused with, brainstorm a dozen candidates in different styles (including a concrete metaphor), test them against the classic rules (Martin, Kernighan and Pike, Evans, Feitelson, Arnaoudova), and recommend one with a long and a short form. |
| `court` | `/court:hold` | Hold court over a backlog of decisions: one small, self-contained item at a time, with the background, the cost and a recommendation; the ruling is carried out, and the next item is chosen by judgment (ready before pending, unblocking and time-sensitive first, related items together), not by arrival order. Works for any kind of item. |

Claude also picks up each skill on its own when a request matches, so you rarely need to type the commands.

## Setup notes

**quota.** Requires CLIProxyAPI with its management API enabled, plus `jq` and `curl`. Settings live in `~/.config/quota.env`; the defaults are at the top of `plugins/quota/bin/subquota`. For example:

```bash
QUOTA_PROTECTED_EMAIL=me@example.com   # main account: keep a 15% reserve, never route it dry
```

On macOS, `subquota --install-launchd` rebalances every 15 minutes in the background.

**flights.** Needs the browser-use plugin and a running Chrome.

## Developing

Clone the repo and add the clone as a local marketplace:

```
git clone https://github.com/mark-henry/claude-tools ~/claude-tools
claude plugin marketplace add ~/claude-tools
claude plugin install quota@mark-henry
```

Installs are copied into Claude Code's plugin cache and versioned by commit, so after editing, commit and then run `claude plugin marketplace update mark-henry && claude plugin update quota@mark-henry`. To try uncommitted edits, start a session with `claude --plugin-dir ~/claude-tools/plugins/quota`.

MIT licensed.
