---
name: loop
description: "Set up and run an unattended, oracle-gated agent loop (Ralph-style): a spec with a done-bar, a task ledger only the check can flip, the scorer and held-out set out of the agent's reach, a short prompt, one task per fresh agent pass, and a supervisor that runs the check itself and stops on done, a cap or a stall. Ships run-loop.sh. Use for \"/swarm:loop\", \"Ralph loop\", \"run this unattended\", \"let it grind\", \"loop until the tests pass\", ports, migrations, refactors, harness or eval-infrastructure builds, or any piece swarm:plan assigns the loop pattern. Not for work without a machine check: build the check first, or use another pattern."
---

# Oracle-gated agent loop

A loop is worth running unattended only when a pass/fail signal exists that the agent cannot fake: "the task verifier must be nearly perfect, or Claude solves the wrong problem" [1]. The pattern is Huntley's Ralph loop: one prompt file, a fresh agent each pass, and all state on disk [2]. What makes it safe is the infrastructure around the loop.

## 1. Set up the loop directory

| File | What it holds | Who may write it |
|---|---|---|
| `SPEC.md` | goals, non-goals, "done when" criteria [3] | the human or planner |
| `ledger.json` | one entry per task: id, description, `passes` | only the check flips `passes`; agents may only add notes. JSON, because models overwrite it less readily than Markdown [4] |
| `PROMPT.md` | the per-pass instruction | the human or planner |
| `PROGRESS.md` | one line per pass: task taken, outcome, next hint | the agent |
| the check | a command: exit 0 when done, otherwise the number passing as the first token of its last line | outside the agent's writable tree |
| held-out items | items the agent never sees, run only by the supervisor at the end | outside the agent's writable tree |

Keep the scorer, the test items and the held-out set out of the agent's reach: a read-only mount, another user, or a path outside its container. Frontier models have modified tests and scoring code to raise scores [5]. StrongDM keeps its end-to-end scenarios outside the codebase as a holdout the agents cannot see [6].

Give the check a fast sampled mode (1–10% of items) so each pass gets feedback in minutes, with terse, grep-able output [1].

## 2. Write a short prompt

A 1,500-word prompt made RepoMirror's agents "slower and dumber" than a 103-word one [7]. `PROMPT.md` says, in about that many words:
- read `SPEC.md`, `ledger.json` and the tail of `PROGRESS.md`;
- take one task that isn't passing;
- make it pass by running the fast check;
- commit, and append one line to `PROGRESS.md`;
- never edit or delete tests, the check or the ledger's `passes` field ("It is unacceptable to remove or edit tests" [4]);
- stop after one task.

One task per fresh context keeps each pass well inside its window [4].

## 3. Run under a supervisor

`run-loop.sh` (in this directory) is the supervisor:

```bash
AGENT_CMD='claude -p --permission-mode bypassPermissions' \
CHECK_CMD='./check --fast' \
STALL=3 path/to/run-loop.sh path/to/loop-dir 40
```

- Each pass pipes `PROMPT.md` to a fresh agent, then runs the check itself. The agent's word is never the signal.
- Done when the check exits 0. Stops at the pass cap (exit 2), after `STALL` passes without a new best count (exit 3), or when a `STOP` file appears (exit 4). The iteration cap is the main safety mechanism in Anthropic's ralph-wiggum plugin [8].
- An agent that dies, or kills its own process (both the C compiler run and RepoMirror saw agents `pkill` themselves [1][7]), is simply restarted by the next pass.
- Logs: `loop.log` (one line per pass) and `logs/pass-N.log`.
- Bypass permission prompts only inside a container, VM or sandbox [9]. Set a cost cap in the agent command or the account as well as the pass cap.

For parallel loops, give each loop its own worktree and its own slice of the ledger, claimed atomically. Keep claims short: Cursor's agents held locks too long, and 20 agents ran at the throughput of 2–3 [10]. For a one-shot mechanical migration, Claude Code's `/batch` splits the work into 5–30 worktree units that each open a PR [11].

## 4. Smoke, then scale

Run three passes and read every log, then fix the prompt and the check, and only then start the real run [11]. Watch for:
- **claims of completion with no change in the check.** RepoMirror's agents overstated how finished their ports were [7].
- **edits to tests or the check**, which should be impossible by construction; if one happens, the reach control has failed.
- **every pass taking the same big task.** When Linux kernel compilation was a single task, every agent hit the same bug. Splitting it against a reference (GCC) let them work in parallel [1].

## 5. Close out

When the loop stops, the supervisor or a fresh agent:
1. runs the full check, and the held-out set if there is one;
2. reports the exit reason, passes used, best count, held-out result and any suspicious passes;
3. writes a Results line in the `swarm:plan` plan, if one exists.

A loop that stopped on stall or cap needs a person or planner to look at why. Usually the next task is too big, or the check is wrong. More passes rarely fix either.

## Sources
1. Carlini, Anthropic, Feb 2026: https://www.anthropic.com/engineering/building-c-compiler
2. Huntley, Jul 2025: https://ghuntley.com/ralph/
3. OpenAI, long-horizon Codex tasks: https://developers.openai.com/blog/run-long-horizon-tasks-with-codex
4. Anthropic, Nov 2025: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
5. METR, Jun 2025: https://metr.org/blog/2025-06-05-recent-reward-hacking
6. Willison on StrongDM's software factory, Feb 2026: https://simonwillison.net/2026/feb/7/software-factory/
7. RepoMirror, Aug 2025: https://github.com/repomirrorhq/repomirror/blob/main/repomirror.md
8. atcyrus, on the ralph-wiggum plugin: https://www.atcyrus.com/stories/ralph-wiggum-technique-claude-code-autonomous-loops
9. Claude Code sandbox docs: https://code.claude.com/docs/en/sandbox-environments
10. Cursor, Jan 2026: https://cursor.com/blog/scaling-agents
11. Claude Code best practices: https://code.claude.com/docs/en/best-practices
