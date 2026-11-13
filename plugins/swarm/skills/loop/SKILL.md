---
name: loop
description: "Set up and run an unattended, oracle-gated agent loop (Ralph-style): a spec with a done-bar, a task ledger only the check can flip, the scorer and held-out set out of the agent's reach, a short prompt, one task per fresh agent pass, and a supervisor that runs the check itself and stops on done, a cap or a stall. Ships the `swarm-loop` supervisor. Use for \"/swarm:loop\", \"Ralph loop\", \"run this unattended\", \"let it grind\", \"loop until the tests pass\", ports, migrations, refactors, harness or eval-infrastructure builds, or any piece swarm:go assigns the loop pattern. Not for work without a machine check: build the check first, or use another pattern. Not Claude Code's built-in /loop, which re-runs a prompt on a timer inside one session."
---

# Oracle-gated agent loop

A loop is worth running unattended only when a pass/fail signal exists that the agent cannot fake. The pattern is Huntley's Ralph loop: one prompt file, a fresh agent each pass, and all state on disk. What makes it safe is the infrastructure around the loop.

## 1. Set up the loop directory

The loop directory is the agent's working directory, usually the root of its own worktree. It holds:

| File | What it holds | Who may write it |
|---|---|---|
| `SPEC.md` | goals, non-goals, hard constraints, deliverables, "done when" criteria | the human or planner |
| `ledger.json` | one entry per task: id, description, `passes` | only the check flips `passes`; agents may only add notes. JSON, because models overwrite it less readily than Markdown. The supervisor never reads it, so an agent that edits it misleads only the next agent, never the stop decision |
| `PROMPT.md` | the per-pass instruction | the human or planner |
| `PROGRESS.md` | one line per pass: task taken, outcome, next hint | the agent |
| the check | a command: exit 0 when done, otherwise the number passing as the first token of its last line | outside the agent's writable tree |
| held-out items | items the agent never sees, run only by the supervisor's final command | outside the agent's writable tree |

Keep the scorer, the test items and the held-out set out of the agent's reach, and out of its sight: another user, or a path outside its container, rather than a read-only mount it can still read. A check that executes code the agent wrote runs it isolated and only reads the results. The agent's repository config and git hooks are executable input too: a host-side check never runs git commands under them, even only to read files.

Give the check a fast sampled mode (1–10% of items) so each pass gets feedback in minutes, with terse, grep-able output. Failure output echoes inputs and what the agent produced, never expected answers; before launch, check the agent's memory and config files for leaked answers.

## 2. Write a short prompt

`PROMPT.md` says, in about 100 words:
- read `SPEC.md`, `ledger.json` and the tail of `PROGRESS.md`;
- take one task that isn't passing;
- make it pass by running the fast check, and rerun the tests that passed before so the fix breaks nothing;
- commit, and append one line to `PROGRESS.md`;
- never edit or delete tests or the check, and never touch the ledger's `passes` field, which only the check flips;
- stop after one task.

One task per fresh context keeps each pass well inside its window and leaves a clean commit to check.

## 3. Run under a supervisor

`swarm-loop` (on PATH from this plugin; the file is `${CLAUDE_PLUGIN_ROOT}/bin/swarm-loop`) is the supervisor:

```bash
AGENT_CMD='claude -p --permission-mode bypassPermissions' \
CHECK_CMD='/outside/agent/reach/check --fast' \
FINAL_CMD='/outside/agent/reach/check --full --held-out' \
STALL=3 swarm-loop path/to/loop-dir 40
```

- It runs the check once before the first pass. If the check already passes, no agent runs; if it fails without a count on its last line, the loop stops before spending (exit 5).
- Each pass pipes `PROMPT.md` to a fresh agent, then runs the check itself. The agent's word is never the signal. Freeze the scorer before the first pass: record its content hash where the agent cannot write, and have `CHECK_CMD` verify it on every check.
- Done when the check exits 0, and the loop stops at once: agents left running after the work is done drift into busywork and unrequested features. Stops at the pass cap (exit 2), after `STALL` passes without a new best count over the baseline (exit 3), or when a `STOP` file appears in the state directory described below (exit 4). The pass cap counts every pass run against the state directory, across relaunches: a relaunch continues the count and the pass numbering, and running more means raising the number. It is both a safety limit and cost control; 10–20 passes is a reasonable start for a new task. On any stop, `FINAL_CMD`, if set, runs once into `logs/final.log`.
- An agent that dies or kills its own process is restarted by the next pass, as long as the supervisor survives. `swarm-loop` is a bash script, so an agent running as the same user can kill it too. Run the agent as another user or in a container, out of reach of the supervisor's processes.
- Logs: `loop.log` (one line per pass), `logs/pass-N.log` and `logs/final-pass-N.log` (one per launch, never overwritten) go to a state directory, by default `<loop-dir>.swarm-loop` beside the loop directory (override with `STATE_DIR`), and so does `STOP`. Keeping them outside the agent's tree keeps them out of git and keeps held-out results from `FINAL_CMD` away from the agents of a later rerun.
- Launch it in the background (the Bash tool's `run_in_background`, or `nohup … &` in a terminal): a 40-pass loop outlives a foreground tool call. Give each pass a wall-clock limit inside `AGENT_CMD` (`timeout`, or coreutils' `gtimeout` on macOS), and the check one inside `CHECK_CMD`, because a hung agent or check stalls the whole loop.
- Bypass permission prompts only inside a container, a VM or the sandbox runtime, not the `/sandbox` Bash sandbox alone, which leaves file tools, MCP servers and hooks on the host. Claude Code refuses `--dangerously-skip-permissions` as root, so run it as a non-root user. Set a cost cap in the agent command or the account as well as the pass cap.

For parallel loops, give each loop its own worktree and its own slice of the ledger, claimed atomically. Keep claims short and release them on failure. For a one-shot mechanical migration, Claude Code's `/batch` splits the work into 5–30 units and shows the plan; once approved, each unit gets its own worktree and opens a PR or reports what happened.

## 4. Smoke, then scale

Run three passes and read every log, then fix the prompt and the check, and only then start the real run. Watch for:
- **claims of completion with no change in the check.**
- **edits to tests or the check**, which should be impossible by construction; if one happens, the reach control has failed. Quieter forms count too: a skipped test, a golden output regenerated over buggy output, a widened timeout or threshold, an added suppression, a bypassed pre-commit check.
- **every pass taking the same big task.** Split it against a reference, so passes can work in parallel.
- **placeholder or minimal implementations passing a shallow check.** Make the check test real behavior.

## 5. Close out

When the loop stops, the supervisor or a fresh agent:
1. runs the full check, and the held-out set if there is one (`FINAL_CMD` does this automatically);
2. reports the exit reason, passes used, best count, held-out result, any suspicious passes, and the important properties the check leaves untested (performance, maintainability);
3. writes a Results line in the `swarm:go` plan (`plan.md` in the run folder), if it was given one.

A loop that stopped on stall or cap needs a person or planner to look at why. Usually the next task is too big, or the check is wrong. More passes rarely fix either. Relaunching with a changed check, held-out set or cap is that person's or planner's call, never the loop agent's; keep the old logs and note the change in `loop.log`.

The studies, incidents and sources behind these instructions are in [references/evidence.md](references/evidence.md).
