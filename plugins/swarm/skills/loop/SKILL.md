---
name: loop
description: "Keep the judge of \"done\" apart from the worker, and harden it: a check the worker cannot reach, a model judge that sees the work and not the worker's account, and the `swarm-loop` supervisor for work bigger than one context. Use for \"/swarm:loop\", \"a check it can't talk its way past\", \"it keeps saying done when it isn't\", \"keep the scorer away from the agent\", \"held-out set\", \"harden the judge\", \"loop until the tests pass\" (this skill says when goal mode is enough), and the judge of done swarm:go seats. Not for validating a judge that scores many items (evals:judge). Not Claude Code's /loop, a timer."
---

# A judge the worker cannot talk past

This skill's output is an unattended run whose stop decision came from a check the worker could not edit or persuade, and a report of it: the exit reason, passes and effective tokens used, the best count, the held-out result, anything that looks like an attempt on the check, and what the check does not test.

## When the built-in goal mode is enough

The harness's goal mode (`/goal <condition>`) keeps a session working until a condition holds; its judge is a small model that reads the conversation and runs nothing. A `Stop` hook that runs a command does run something, but its script sits in the session's reach. Either is enough when the user will read the result themselves, so a false "done" costs little. Use this skill when the result will be relied on unread, or when the worker could change what scores it (tests, scorer, expected outputs, thresholds) and that matters.

## Partition

Build these in. An instruction to the worker is not a control, and the shipped script is not isolation: it runs every command as the user who launched it.

- Separation holds only where the worker cannot write: another user, a container, a read-only mount. A worker running as the supervisor's user can rewrite any check, scorer or state it can reach, wherever it sits.
- Out of the worker's write reach: the check, the scorer and its items, the judge's prompt, the prompt file the next worker reads, and the supervisor's state directory (it holds the pass count and the held-out output). The scorer's items, the held-out set and the state directory must be out of its sight too: a read-only mount stops writes, not reads.
- The supervisor runs the check. The worker's message, exit code and ledger are never the stop signal.
- The check trusts no exit code and no output line the worker's code can produce. Code imported into the check's process can exit 0 for it or print a forged count: run the worker's code in a process of its own, and compute pass and count in the check from the results. Run no host-side git command under the worker's repository config or hooks.
- What the worker may run for feedback returns counts, its inputs and its outputs, never expected answers. Look in its memory and config files for leaked ones.
- In a task ledger, only the check flips an entry to passing.
- The held-out set runs once, at stop.
- Changing the check, the held-out set or the cap belongs to whoever launched the run, never to the worker.

## The judge

Deterministic first: a command that exits 0 when done and grades the final state, not the path or the report. The worker will solve whatever it measures, so a stub or a special case must not pass.

When "done" needs judgment, the judge is a fresh agent on a smart model, never a fork (a fork inherits the conversation).

- It gets the standard word for word and the work itself: the diff, the built thing, the resulting state. It never gets the worker's messages, summary, commit messages or notes.
- Text planted in the work is met by what the judge is given: outputs of commands it runs itself and, where possible, the work with comments and prose stripped. Telling it "this is data" is a label, not a control.
- It runs what can be run, then gives a verdict per criterion with evidence from its own tool results. "Cannot tell" is a fail.
- It changes nothing; its findings are the worker's next input. A judge asked often enough passes something: behind `swarm-loop` the round cap is the pass cap, unless the check sets a lower one.

Prove any judge before the run and whenever it changes: five known-bad pieces of work, each carrying a confident claim of success, and five known-good; all ten must be ruled correctly.

Hiding the scorer stops tampering, not attempts. After the first passes and at stop, read the logs and the diff for the quiet ways around a check: a skipped or deleted test, a golden output regenerated over wrong output, a widened threshold or timeout, an added suppression, a bypassed hook.

## Work bigger than one context

`swarm-loop <loop-dir> [max-passes]` (on PATH from this plugin) takes `AGENT_CMD`, `CHECK_CMD`, `FINAL_CMD` (the held-out set), `PROMPT`, `CHECK_DIR`, `STALL` and `STATE_DIR`; its header gives the check's contract and the exit codes. Each pass it pipes a copy of the prompt, frozen at launch, to a fresh worker in `<loop-dir>`, then runs the check itself somewhere else. The check reports by writing `done` or a count to the file `$SWARM_RESULT` names; its exit code and output are only logged, so run the worker's code in a child process with that variable unset. Keep the prompt outside `<loop-dir>`. The state directory defaults to a place outside it and the worker is not told where, but a worker running as the same user can still find it: for real separation, run the worker command as another user or in a container. The script sets no timeout and no budget and records no token use: put a timeout in both commands, and the budget, in effective tokens, in the worker command.

A stop on stall or cap usually means the check is wrong or the remaining task is too big; more passes rarely fix either.
