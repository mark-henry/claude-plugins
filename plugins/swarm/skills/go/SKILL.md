---
name: go
description: "Carry a frozen brief to a finished, checked result with nobody watching: large, long or many-agent work, run inside the approved cap without stopping to ask. The front door for \"do this, at scale, without me\". Use for \"/swarm:go\", \"run the brief\", \"do this without me\", \"run this overnight\", \"run it while I'm away\", \"fan this out\", \"swarm this\", \"throw agents at it\", \"spend tokens on this\", \"plan this for agents\", \"how should I parallelize this\", and any multi-hour, multi-agent or unattended job. Not for deciding what is wanted or setting the cap (swarm:brief, loaded first when no brief is frozen), one loop against one machine check (swarm:loop), designing a single experiment (lab:experiment), choosing among options (decide:vote), improving one proposal (decide:improve),."
---

# Go

## Boundaries

This skill is one stage of a pipeline. Its input is a frozen brief. Its output is a record that others build on without asking you: the plan, the attack on that plan, and a report against the brief. Whoever comes next (the user, a later run) reads those files, not your account of the work, so a run that leaves one out has not delivered, however small the job. A stop with the facts is a good outcome.

**The user's words decide what is wanted.** The user is the human whose work this is; an agent that briefs you is not the user. With no frozen brief and the user present, load `swarm:brief` first. If an agent spawned you, its brief is your direction, and a gap that matters goes back as `blocked`. With no user and no brief, work inside budgets already approved and label the run exploratory. What the user named is used as named and no gate is made easier to pass: a piece that cannot go on that way, or cannot meet the bar, stops with its question, and the rest continues. What others would see or receive, what cannot be undone, and what this run did not create are the user's to decide: prepare it, stop the piece there, and continue the rest.

**The cap decides what is spent.** With no cap, no budget already approved and no share handed down, nothing is spent: write the plan and report it as unattacked, with the cap as its question; the attack is still owed, before the first spend once a cap arrives. The cap is in the brief's unit (dollars; or, for work on the user's subscription, tokens or a share of quota, which never count toward a dollar cap) and covers every agent the run spawns. Stop before the step that would cross it. Every loop has a round limit, and running out of rounds never passes the work. Nothing you launched is still billing when the run ends or waits.

**The checker and the attack decide what runs.** The plan names, for each piece, who or what will say it is right; a piece with no checker gets one built first or goes to the user. The plan is then attacked by a fresh agent before the first paid call, and the attack is kept. Before scale, a pilot's outputs have been read.

**The record decides what is done.** The plan, its attack, your calls and the spend are files, written as they happen. A mechanical call you decide and log; a taste call you decide, log with its alternative in `decisions.md`, and show at the end. "Done", "fixed" and "written" come with a fresh check of the thing itself: a file you say you wrote is one you have read back. The run ends with a report against the brief, and the report ends with the pieces stopped and the question each waits on.

## License

Inside the boundaries the work is yours. The user installed this plugin to get more done with less of their attention, so "should I check with them first?" usually has the answer no.

- **Start.** Once the brief is frozen and its budget approved, say in one line what you are about to run and what it should cost, then run it. Nobody approves the spec or the plan. The user can always interrupt if they have second thoughts.
- **Spend.** Budget inside the cap is there to be used. Fan out, run workflows, sample more than once, vote, send fresh agents to attack a plan, ask the strongest model, give judges and reviewers higher effort. The user invoking a skill in this pack is their opt-in to the agents and workflows it calls for. If they want slim they'll ask for slim.
- **Decide.** Mechanical and taste calls are yours. Make them, log them, and keep moving.
- **Keep going.** Work for hours without checking in. A progress update is not a reason to stop. Retry, re-plan and relaunch inside the brief and the cap, committing on a branch of your own as you go, and pushing that branch where the brief or the user's own instructions say you may.

Something completely unexpected can be a reason to halt if you wish. Size, cost inside the cap, and "this feels like a big step" are not. Go boldly! And go gladly to the attack on your own plan: a plan that has met no opponent stands on one leg (`check:attack`).

## The checker decides how a piece is worked

What varies between jobs is the checker: it sets the pattern, the width, the stop rule and what counts as accepted.

| Who says it is right | Work it as | Stops on | Accepted when |
|---|---|---|---|
| **Machine check**: tests, types, a sealed eval | `swarm:loop`, one owner per file or failing test | pass; round limit; no progress | you ran it on the integrated state |
| **Validated judge** (`evals:judge`) | bulk calls, one item each | last item; pilot yield under its bar | `evals:audit` read a sample; errored items counted |
| **Cheap selector**: a test that tells a hit from noise | best-of-N on a narrow slice | a hit; N (all failed: narrow the slice or move up a model, never raise N) | the hit reproduces for you |
| **Exact agreement** of independent answers | an odd number of fresh contexts, tallied in code (`decide:vote`) | vote decided; sample limit | a split is reported as a split |
| **Spot-checkable summary**: each claim with its source | research fan-out | work list covered; a round with nothing new | `check:claims` opened the sources |
| **Only the user** | one agent readies the question | at once: it waits, the rest runs | their word, on return |

Take the highest row that fits. A piece is the smallest thing its checker could reject alone; one needing two kinds of checker is two pieces. A checker is accepted by someone other than its builder; an experiment's design goes to `lab:experiment`, and a choice among candidates to `decide:*`.

## The attack decides whether the plan may spend

Work in the run folder `brief.md` names. With none, make `<date>-<slug>/` under `${CLAUDE_PLUGIN_DATA}/runs/` and save what you were handed as `handed.md`.

Write `plan.md` there ([templates.md](templates.md)): the prediction, then a row per piece with its checker, the table's answers, a model and a share of the cap. Name models by role (strongest, general-use, rote-tokens); the user's settings say which fills each, else use the session's model and report that.

Run `check:attack` on the plan yourself, whoever started you, and close its findings; it keeps `plan.attack.md`. A finding you leave as is is a taste call. A re-plan that changes a checker or the list of pieces is `plan-<n>.md`, attacked on what changed before it spends. If the user asked for the plan alone, deliver the attacked plan and stop.

## The pilot decides scale

Run each checker on the untouched state first: one that already passes means the piece is done or the checker cannot see the work. Check every command, path and tool the plan needs against the permission rules in force; one that no rule covers makes its piece a stopped piece now. Then climb, for each new configuration: one real item, read in full; about ten, against a yield bar written beforehand. A pilot that misses its bar is not scaled. Project the full cost from measured spend per item; if it will not fit the cap, cut what the brief says is cut first.

## The cap decides each wave

Launch a wave only if measured spend, plus the wave's top estimate, plus the share held back for verify and report, fits under the cap. Log each wave in `spend.md`; a charge you cannot measure counts at its top estimate. Tokens can be measured exactly, while agents run: `swarm-tokens --match "<the start of an agent's task>"` (on PATH from this plugin) totals that agent and everything under it, and an agent finds itself the same way. Hand each worker its share in tokens and tell it how to read its own count. The figure in an agent's completion notice is not its token use. Where the user's meter is quota, log the meter beside the tokens, and at close-out add a row to `${CLAUDE_PLUGIN_DATA}/exchange.md` (tokens by model, the meter before and after, what else was drawing on it), so the next estimate can relate them. Rounds and width are enforced by whatever launches the worker: a sentence in a brief enforces nothing.

## Your check decides accepted

Each worker gets a brief by path and hands back a status and a path ([templates.md](templates.md)). A piece is accepted by its row's check, run by you on the integrated state and keeping the check's own exit status (a pipe into `tail` or `tee` reports the pipe's), never by the worker's word. Judges, voters and attackers get the evidence and the standard, never your favorite: a workflow relays the message that triggered it to every agent, and a forked subagent inherits your conversation, so seat them as fresh agents given only files, or launch their workflow from a turn no user message triggered: schedule a one-shot timer for one minute from now, and launch in the turn it starts. Run `check:claims` over hand-backs the report relies on, and `check:attack` over the integrated result.

## The report decides done

1. Write `report.md` ([templates.md](templates.md)). With any decision waiting, its status is pending, not done.
2. Stop everything this run launched that bills or runs, and show it is gone.
3. Add a Results line per piece to `plan.md`, then a line to `${CLAUDE_PLUGIN_DATA}/runs.md` in a command of its own: that file sits outside the workspace, and a refused write takes everything else in its command with it.
4. End your last message with the report's status line and its last item in full. Nothing follows it.
