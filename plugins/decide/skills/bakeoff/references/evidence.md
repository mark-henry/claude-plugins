# Evidence for decide:bakeoff

Run records and test notes moved out of the body of `decide:bakeoff`, verbatim. Each passage sits under a line naming the instruction it backs. Product and model names are as they stood when the passage was written.

## Step 0: freeze the brief

Backs: schedule a one-shot timer for one minute from now, and launch in the turn it starts.

> A cron-fired turn isn't a user request, so the harness relays nothing and agents see only the script's text (tested 2026-11-03 with a one-agent probe: launched from a user turn, the agent's first message was that turn verbatim; launched from a cron, it had no relay block).

## Counts and models

Backs: Effort: set it explicitly; a role with a `models` override silently falls back to that model's own default.

> A role without `efforts` inherits the session's effort, but a role with a `models` override silently falls back to that model's own default (Fable: high), tested 2026-11-02.

Backs: Effort: try `high` or `xhigh` for attack and judge first, and log the result.

> Both logged runs ran at medium (judge at high), so nothing yet says whether higher pays.

Backs: Cost: at 3 picks, about 15 agents and 2–2.5M tokens, plus any paid API spend in the prototypes; the measurements drive wall time.

> At 3 picks, about 15 agents and 2–2.5M tokens, which has cost between about 1.5 and 12 points of one Ultra account's weekly quota at Opus medium (runs 1-3; the expensive run had 7 h of overloaded measurements), plus any paid API spend in the prototypes.

> Wall time ranged from 70 minutes to 7 hours, driven by the measurements.

## Sandboxes

Backs: prefer a git worktree per pick on its own branch, so porting the winner is a cherry-pick.

> Prefer a git worktree per pick on its own branch, so porting the winner is a cherry-pick: run 4's history-less copies had to be ported by hand, and two families had built the same shared requirement with different flag spellings.

Backs: Share the CPU: give each sandbox at most (cores ÷ picks) worker processes and write that cap into `measure`.

> Run 3 let each sandbox use every core; load hit 163 and the run took 7 hours instead of about 1.

Backs: build any shared measurement script and run it on cases whose answers you already know, including the domain's edge cases.

> Run 3's audit mis-graded every instance with a pre-existing shift until an agent caught it mid-run, and the fix never reached the other sandboxes, so their final reports quoted the wrong baseline.

Backs: have one agent red-team the script itself.

> In run 3 every attacker independently found that a per-arm constant beat the audit's cheap-policy finder.

Backs: run the test command inside a sandbox copy, not the original.

> Excluding `.venv` from the copy broke `uv run pytest` for ten agents in run 3.

Backs: measure the numbers the bar's feasibility hinges on yourself and put them in `context`.

> In run 4 all twelve chain agents ended with "n not counted": the count needed data they weren't allowed to read, and the power verdict turned on it.

Backs: a run that decides what to run, rather than fixing code, can skip the shared script once those numbers are in hand.

> A run that decides what to run, rather than fixing code, can skip the shared script once those numbers are in hand: run 4 used tests, numeric power estimates and dry runs only, and took 39 minutes.

## args

Backs: `minutes`: over budget, agents report unfinished work instead of overrunning.

> In run 3 one repairer took 168 minutes and the judge waited 4 hours on that chain.
